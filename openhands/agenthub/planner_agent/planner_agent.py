"""PlannerAgent: A meta-agent that orchestrates task execution through planning and delegation."""

import json
import os
from collections import deque
from typing import TYPE_CHECKING

from openhands.llm.llm_registry import LLMRegistry

if TYPE_CHECKING:
    from openhands.events.action import Action
    from openhands.llm.llm import ModelResponse

import openhands.agenthub.codeact_agent.function_calling as function_calling
from openhands.agenthub.planner_agent.plan import ExecutionPlan, PlanStep, StepStatus
from openhands.agenthub.planner_agent.tools import get_planner_tools
from openhands.controller.agent import Agent
from openhands.controller.state.state import State
from openhands.core.config import AgentConfig
from openhands.core.logger import openhands_logger as logger
from openhands.core.message import Message
from openhands.events.action import (
    AgentDelegateAction,
    AgentFinishAction,
    AgentThinkAction,
    MessageAction,
)
from openhands.events.event import Event
from openhands.llm.llm_utils import check_tools
from openhands.memory.condenser import Condenser
from openhands.memory.condenser.condenser import Condensation, View
from openhands.memory.conversation_memory import ConversationMemory
from openhands.utils.prompt import PromptManager


class PlannerAgent(Agent):
    """A meta-agent that orchestrates complex tasks through planning and delegation.

    The PlannerAgent:
    1. Analyzes user queries and repository context
    2. Creates structured execution plans
    3. Delegates steps to specialized agents (CodeActAgent, BrowsingAgent, etc.)
    4. Collects feedback from sub-agents
    5. Refines plans based on feedback
    6. Iterates until the goal is achieved

    This enables hierarchical task decomposition and better utilization of specialized agents.
    """

    VERSION = '1.0'

    def __init__(self, config: AgentConfig, llm_registry: LLMRegistry) -> None:
        """Initialize the PlannerAgent.

        Args:
            config: Agent configuration
            llm_registry: Registry for accessing LLMs
        """
        super().__init__(config, llm_registry)
        self.pending_actions: deque['Action'] = deque()
        self.current_plan: ExecutionPlan | None = None
        self.reset()
        self.tools = get_planner_tools()

        # Create conversation memory
        self.conversation_memory = ConversationMemory(self.config, self.prompt_manager)

        # Create condenser
        self.condenser = Condenser.from_config(self.config.condenser, llm_registry)
        logger.debug(f'Using condenser: {type(self.condenser)}')

        # Override with router if needed
        self.llm = self.llm_registry.get_router(self.config)

        logger.info(f'PlannerAgent initialized with {len(self.tools)} tools')

    @property
    def prompt_manager(self) -> PromptManager:
        """Get the prompt manager for this agent."""
        if self._prompt_manager is None:
            self._prompt_manager = PromptManager(
                prompt_dir=os.path.join(os.path.dirname(__file__), 'prompts'),
                system_prompt_filename=self.config.resolved_system_prompt_filename,
            )
        return self._prompt_manager

    def reset(self) -> None:
        """Reset the agent's internal state."""
        super().reset()
        self.pending_actions.clear()
        self.current_plan = None

    def step(self, state: State) -> 'Action':
        """Execute one step of the planning/execution loop.

        This is the main entry point for the agent. It:
        1. Checks for pending actions and returns them first
        2. Processes conversation history and gets LLM response
        3. Converts LLM response to actions (create_plan, update_plan, delegate_task, etc.)
        4. Returns the next action to execute

        Args:
            state: Current state including conversation history

        Returns:
            Action: The next action to execute
        """
        # Return pending actions first
        if self.pending_actions:
            return self.pending_actions.popleft()

        # Check for exit command
        latest_user_message = state.get_last_user_message()
        if latest_user_message and latest_user_message.content.strip() == '/exit':
            return AgentFinishAction()

        # Condense conversation history if needed
        condensed_history: list[Event] = []
        match self.condenser.condensed_history(state):
            case View(events=events):
                condensed_history = events
            case Condensation(action=condensation_action):
                return condensation_action

        logger.debug(
            f'Processing {len(condensed_history)} events from {len(state.history)} total'
        )

        # Get initial user message
        initial_user_message = self._get_initial_user_message(state.history)

        # Build messages for LLM
        messages = self._get_messages(condensed_history, initial_user_message)

        # Add current plan context to the messages if we have one
        if self.current_plan:
            plan_context = self._format_plan_context()
            # Insert plan context before the last message (usually user's latest)
            if messages:
                # Add as a system-style message
                messages.append(
                    Message(
                        role='user',
                        content=[
                            {
                                'type': 'text',
                                'text': f'\n<current_plan>\n{plan_context}\n</current_plan>\n',
                            }
                        ],
                    )
                )

        # Call LLM
        params: dict = {'messages': messages}
        params['tools'] = check_tools(self.tools, self.llm.config)
        params['extra_body'] = {
            'metadata': state.to_llm_metadata(
                model_name=self.llm.config.model, agent_name=self.name
            )
        }

        response = self.llm.completion(**params)
        logger.debug(f'LLM response: {response}')

        # Convert response to actions
        actions = self.response_to_actions(response, state)
        logger.debug(f'Generated {len(actions)} actions from response')

        # Add actions to pending queue
        for action in actions:
            self.pending_actions.append(action)

        # Return first action
        if self.pending_actions:
            return self.pending_actions.popleft()
        else:
            # No actions generated, ask for clarification
            return MessageAction(
                content='I need more information to proceed. Can you provide more details?'
            )

    def _get_initial_user_message(self, history: list[Event]) -> MessageAction:
        """Find the initial user message from history.

        Args:
            history: Full event history

        Returns:
            The first user message action

        Raises:
            ValueError: If no initial user message is found
        """
        for event in history:
            if isinstance(event, MessageAction) and event.source == 'user':
                return event

        raise ValueError('Initial user message not found in history')

    def _get_messages(
        self, events: list[Event], initial_user_message: MessageAction
    ) -> list[Message]:
        """Build message history for LLM.

        Args:
            events: Condensed event history
            initial_user_message: The first user message

        Returns:
            List of messages formatted for LLM
        """
        if not self.prompt_manager:
            raise Exception('Prompt Manager not instantiated')

        messages = self.conversation_memory.process_events(
            condensed_history=events,
            initial_user_action=initial_user_message,
            max_message_chars=self.llm.config.max_message_chars,
            vision_is_active=self.llm.vision_is_active(),
        )

        if self.llm.is_caching_prompt_active():
            self.conversation_memory.apply_prompt_caching(messages)

        return messages

    def response_to_actions(
        self, response: 'ModelResponse', state: State
    ) -> list['Action']:
        """Convert LLM response to actions.

        This method processes the LLM's response and converts tool calls into actions.
        It handles:
        - create_plan: Creates a new ExecutionPlan
        - update_plan: Updates existing plan
        - delegate_task: Delegates to sub-agent via AgentDelegateAction
        - think: Records reasoning
        - view_plan: Shows current plan
        - finish: Completes the task

        Args:
            response: LLM response
            state: Current state

        Returns:
            List of actions to execute
        """
        # First, use standard function calling to get actions
        actions = function_calling.response_to_actions(response, mcp_tool_names=[])

        # Now process PlannerAgent-specific actions
        planner_actions: list['Action'] = []

        for action in actions:
            # Check if this is a message action with tool calls in the response
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                    tool_calls = choice.message.tool_calls
                    if tool_calls:
                        for tool_call in tool_calls:
                            planner_action = self._handle_tool_call(
                                tool_call, state
                            )
                            if planner_action:
                                planner_actions.append(planner_action)

        # If we generated planner-specific actions, use those
        if planner_actions:
            return planner_actions

        # Otherwise, return the standard actions
        return actions

    def _handle_tool_call(
        self, tool_call, state: State
    ) -> 'Action | None':
        """Handle a specific tool call from the LLM.

        Args:
            tool_call: Tool call from LLM response
            state: Current state

        Returns:
            Action or None
        """
        function_name = tool_call.function.name
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            logger.error(f'Failed to parse tool arguments: {tool_call.function.arguments}')
            return MessageAction(content='Error: Invalid tool arguments')

        logger.info(f'Handling tool call: {function_name} with args: {arguments}')

        # Handle create_plan
        if function_name == 'create_plan':
            return self._handle_create_plan(arguments, state)

        # Handle update_plan
        elif function_name == 'update_plan':
            return self._handle_update_plan(arguments, state)

        # Handle delegate_task
        elif function_name == 'delegate_task':
            return self._handle_delegate_task(arguments, state)

        # Handle think
        elif function_name == 'think':
            thought = arguments.get('thought', '')
            return AgentThinkAction(thought=thought)

        # Handle view_plan
        elif function_name == 'view_plan':
            if self.current_plan:
                plan_summary = self._format_plan_context()
                return MessageAction(content=f'Current plan:\n{plan_summary}')
            else:
                return MessageAction(content='No plan has been created yet.')

        # Handle finish
        elif function_name == 'finish':
            summary = arguments.get('summary', 'Task completed')
            outputs = arguments.get('outputs', {})
            return AgentFinishAction(final_thought=summary, outputs=outputs)

        return None

    def _handle_create_plan(self, arguments: dict, state: State) -> 'Action':
        """Handle create_plan tool call.

        Args:
            arguments: Tool arguments
            state: Current state

        Returns:
            Action
        """
        goal = arguments.get('goal', '')
        steps_data = arguments.get('steps', [])
        context = arguments.get('context', {})

        # Create plan steps
        steps = []
        for step_data in steps_data:
            step = PlanStep(
                id=step_data.get('id', f'step{len(steps) + 1}'),
                description=step_data.get('description', ''),
                agent_type=step_data.get('agent_type', 'CodeActAgent'),
                inputs=step_data.get('inputs', {}),
                dependencies=step_data.get('dependencies', []),
                created_at=len(state.history),
            )
            steps.append(step)

        # Create execution plan
        self.current_plan = ExecutionPlan(
            goal=goal,
            steps=steps,
            context=context,
            created_at=len(state.history),
            updated_at=len(state.history),
        )

        logger.info(f'Created plan with {len(steps)} steps: {goal}')

        # Return a message describing the plan
        plan_desc = f"Created execution plan for: {goal}\n\nSteps:\n"
        for i, step in enumerate(steps, 1):
            plan_desc += f"{i}. {step.description} (using {step.agent_type})\n"

        return MessageAction(content=plan_desc)

    def _handle_update_plan(self, arguments: dict, state: State) -> 'Action':
        """Handle update_plan tool call.

        Args:
            arguments: Tool arguments
            state: Current state

        Returns:
            Action
        """
        if not self.current_plan:
            return MessageAction(content='Error: No plan exists to update')

        step_id = arguments.get('step_id')
        new_status = arguments.get('status')
        result = arguments.get('result')
        error = arguments.get('error')
        new_steps_data = arguments.get('new_steps', [])
        refinement_reason = arguments.get('refinement_reason', '')
        refinement_changes = arguments.get('refinement_changes', '')

        # Find and update the step
        step = self.current_plan.get_step(step_id)
        if step:
            if new_status:
                step.status = StepStatus(new_status)
            if result:
                step.result = result
            if error:
                step.error = error

            if step.status == StepStatus.COMPLETED:
                step.completed_at = len(state.history)
            elif step.status == StepStatus.IN_PROGRESS:
                step.started_at = len(state.history)

        # Add new steps if provided
        for step_data in new_steps_data:
            new_step = PlanStep(
                id=step_data.get('id', f'step{len(self.current_plan.steps) + 1}'),
                description=step_data.get('description', ''),
                agent_type=step_data.get('agent_type', 'CodeActAgent'),
                inputs=step_data.get('inputs', {}),
                dependencies=step_data.get('dependencies', []),
                created_at=len(state.history),
            )
            self.current_plan.add_step(new_step)

        # Record refinement
        if refinement_reason and refinement_changes:
            self.current_plan.add_refinement(
                reason=refinement_reason,
                changes=refinement_changes,
                event_id=len(state.history),
            )

        logger.info(f'Updated plan - Step {step_id} status: {new_status}')

        # Return status message
        status_msg = f"Updated plan - Step '{step_id}' marked as {new_status}"
        if new_steps_data:
            status_msg += f", added {len(new_steps_data)} new steps"

        return MessageAction(content=status_msg)

    def _handle_delegate_task(self, arguments: dict, state: State) -> 'Action':
        """Handle delegate_task tool call.

        Args:
            arguments: Tool arguments
            state: Current state

        Returns:
            AgentDelegateAction
        """
        step_id = arguments.get('step_id')
        agent_type = arguments.get('agent_type', 'CodeActAgent')
        task = arguments.get('task', '')
        inputs = arguments.get('inputs', {})

        # Update the step to in-progress
        if self.current_plan:
            step = self.current_plan.get_step(step_id)
            if step:
                step.status = StepStatus.IN_PROGRESS
                step.started_at = len(state.history)

        logger.info(f'Delegating step {step_id} to {agent_type}: {task}')

        # Create delegation action
        delegate_inputs = {'task': task, **inputs}

        return AgentDelegateAction(
            agent=agent_type,
            inputs=delegate_inputs,
            thought=f'Delegating step {step_id} to {agent_type}',
        )

    def _format_plan_context(self) -> str:
        """Format current plan for context in messages.

        Returns:
            Formatted plan string
        """
        if not self.current_plan:
            return 'No plan created yet.'

        context = f"Goal: {self.current_plan.goal}\n"
        context += f"Iteration: {self.current_plan.iteration}\n"
        context += f"Progress: {len(self.current_plan.get_completed_steps())}/{len(self.current_plan.steps)} steps completed\n\n"

        context += 'Steps:\n'
        for step in self.current_plan.steps:
            status_emoji = {
                StepStatus.PENDING: '⏳',
                StepStatus.IN_PROGRESS: '🔄',
                StepStatus.COMPLETED: '✅',
                StepStatus.FAILED: '❌',
                StepStatus.BLOCKED: '🚫',
            }.get(step.status, '❓')

            context += f"{status_emoji} {step.id}: {step.description} ({step.agent_type}) - {step.status.value}\n"

            if step.result:
                context += f"  Result: {step.result[:100]}...\n"
            if step.error:
                context += f"  Error: {step.error[:100]}...\n"

        if self.current_plan.refinements:
            context += '\nRefinements:\n'
            for ref in self.current_plan.refinements[-3:]:  # Show last 3
                context += f"  Iteration {ref.iteration}: {ref.reason}\n"

        return context
