# Building a PlannerAgent Scaffold - Quick Start Guide

## Overview

A PlannerAgent is a specialized agent that excels at task decomposition, planning, and orchestrating sub-agents to handle complex multi-step tasks. It should:

1. **Break down** complex user requests into actionable subtasks
2. **Plan** the execution order and dependencies
3. **Delegate** subtasks to specialized agents (CodeActAgent, BrowsingAgent, etc.)
4. **Track** progress and manage task state
5. **Coordinate** results across multiple agents

## Key Architecture Points for PlannerAgent

### 1. Inheritance Strategy
```python
from openhands.controller.agent import Agent

class PlannerAgent(Agent):
    """A multi-agent orchestrator that plans and delegates tasks"""
    VERSION = '1.0'
    
    def __init__(self, config: AgentConfig, llm_registry: LLMRegistry):
        super().__init__(config, llm_registry)
        # Initialize planner-specific components
        self.plan_tracker = {}  # Track subtasks
        self.tools = self._get_tools()
```

Alternative: Could inherit from CodeActAgent if you need its capabilities as base.

### 2. Core Components to Implement

#### A. Task Planning Tool
- Breaks down user request into subtasks
- Returns structured plan with dependencies
- Tool format:
```json
{
    "type": "function",
    "function": {
        "name": "create_plan",
        "description": "Break down a complex task into subtasks",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "subtasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "description": {"type": "string"},
                            "assigned_agent": {"type": "string"},
                            "dependencies": {"type": "array"}
                        }
                    }
                }
            }
        }
    }
}
```

#### B. Subtask Execution Actions
- Use `AgentDelegateAction` to delegate to other agents:
```python
return AgentDelegateAction(
    agent='CodeActAgent',  # Agent name (must be registered)
    inputs={'task': 'Fix the bug in module X'},
    thought='Delegating code fix to CodeActAgent'
)
```

#### C. Progress Tracking
- Maintain task state in agent memory
- Use TaskTrackingAction (if available) to track progress
- Update plan based on subtask results

### 3. The Step Loop

```python
def step(self, state: State) -> Action:
    """
    Planning-specific step implementation
    
    Flow:
    1. Check if we have a plan
    2. If not, create plan from user request
    3. Check which subtasks are ready to execute
    4. Delegate next subtask to appropriate agent
    5. If all subtasks done, synthesize results
    6. Return appropriate action
    """
    
    # Get conversation history
    messages = self._get_messages(state)
    
    # Call LLM with planning-specific prompt
    response = self.llm.completion(
        messages=messages,
        tools=self.tools,
        extra_body={
            'metadata': state.to_llm_metadata(
                model_name=self.llm.config.model,
                agent_name=self.name
            )
        }
    )
    
    # Convert LLM response to actions
    actions = self.response_to_actions(response)
    
    # Queue actions for execution
    for action in actions:
        self.pending_actions.append(action)
    
    # Return first action
    return self.pending_actions.popleft() if self.pending_actions else AgentFinishAction()
```

### 4. Response Parsing

```python
def response_to_actions(self, response: ModelResponse) -> list[Action]:
    """Parse LLM response into planning actions"""
    actions = []
    
    for tool_call in response.choices[0].message.tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        if tool_name == 'create_plan':
            # Create plan action (custom action type)
            action = CreatePlanAction(
                plan=arguments.get('plan'),
                thought=response.choices[0].message.content
            )
        elif tool_name == 'delegate_task':
            # Delegate to another agent
            action = AgentDelegateAction(
                agent=arguments.get('agent_type'),
                inputs={'task': arguments.get('task_description')},
                thought=response.choices[0].message.content
            )
        elif tool_name == 'finish':
            # Finish the planning task
            action = AgentFinishAction(
                outputs=arguments.get('results'),
                thought=response.choices[0].message.content
            )
        else:
            action = self._parse_tool_call(tool_call, arguments)
        
        actions.append(action)
    
    return actions
```

### 5. System Prompt Strategy

Create `prompts/system_prompt.j2`:

```jinja2
# PlannerAgent System Prompt

You are a strategic task planner and orchestrator. Your role is to:

1. **Analyze** complex user requests
2. **Decompose** into logical subtasks
3. **Plan** optimal execution order considering dependencies
4. **Delegate** subtasks to specialist agents
5. **Synthesize** results into coherent solutions

## Available Agents

{% for agent_name in available_agents %}
- {{ agent_name }}: {{ agent_descriptions[agent_name] }}
{% endfor %}

## Available Tools

Use the tools provided to:
- `create_plan`: Break down tasks and create execution plan
- `delegate_task`: Assign work to specialist agents
- `think`: Log your reasoning process
- `finish`: Complete the task and return results

## Decision Rules

1. If user request is simple and clear, delegate directly
2. If complex with multiple concerns:
   - Break into subtasks
   - Identify dependencies
   - Create execution plan
   - Execute in order
3. Monitor subtask results and adapt as needed
4. Always delegate to appropriate specialist agent

## Example Plan Structure

{
    "goal": "Build and deploy a feature",
    "subtasks": [
        {
            "id": "task-1",
            "description": "Write code for feature X",
            "agent": "CodeActAgent",
            "dependencies": []
        },
        {
            "id": "task-2",
            "description": "Test the implementation",
            "agent": "CodeActAgent",
            "dependencies": ["task-1"]
        },
        {
            "id": "task-3",
            "description": "Deploy to production",
            "agent": "CodeActAgent",
            "dependencies": ["task-2"]
        }
    ]
}
```

### 6. Configuration

Add to your OpenHands config file:

```toml
[agent.PlannerAgent]
enable_cmd = true
enable_editor = true
enable_browsing = true
enable_think = true
enable_finish = true
enable_plan_mode = true
system_prompt_filename = "system_prompt.j2"

[agent.PlannerAgent.model_routing]
# Optional: Route planning decisions to a different model
# planning_model = "claude-opus"
```

### 7. Directory Structure

```
openhands/agenthub/planner_agent/
├── __init__.py                    # Registration
├── planner_agent.py               # Main agent class
├── function_calling.py            # Response parsing
├── prompts/
│   ├── system_prompt.j2           # Main prompt
│   └── plan_template.j2           # Plan formatting
├── tools/
│   ├── plan_creation.py           # Planning tool
│   ├── task_delegation.py         # Delegation tool
│   └── progress_tracking.py       # Progress tracking
└── README.md                      # Documentation
```

### 8. Registration

In `__init__.py`:

```python
from openhands.agenthub.planner_agent.planner_agent import PlannerAgent
from openhands.controller.agent import Agent

Agent.register('PlannerAgent', PlannerAgent)
```

### 9. Delegation Pattern

The key to PlannerAgent is using `AgentDelegateAction`:

```python
# When a subtask is ready:
action = AgentDelegateAction(
    agent='CodeActAgent',  # Target agent type
    inputs={
        'task': 'Implement feature X with following spec...',
        'context': 'This is part of larger task, subtask 2 of 4'
    },
    thought='Delegating implementation to CodeActAgent'
)

# The controller will:
# 1. Create new AgentController with new agent instance
# 2. Increment delegate_level
# 3. Share iteration_flag and budget_flag
# 4. Run agent until it returns AgentFinishAction
# 5. Capture result as AgentDelegateObservation
# 6. Resume PlannerAgent with observation
```

### 10. State Flow

```
PlannerAgent.step() called
    ↓
Get user request from state.history
    ↓
LLM analyzes request
    ↓
Check: Already have plan?
    ├─ NO → create_plan tool → CreatePlanAction
    │       ↓
    │       Add plan to agent's memory
    │       ↓
    │       Return CreatePlanAction
    │
    └─ YES → Check: Which subtasks ready to execute?
             ↓
             Get next ready subtask
             ↓
             Return AgentDelegateAction(agent, task)
             ↓
             (Controller spawns delegate)
             ↓
             Delegate executes task
             ↓
             (Controller receives AgentDelegateObservation)
             ↓
             Next step() sees observation
             ↓
             Update plan progress
             ↓
             Return next AgentDelegateAction
             ↓
             (Repeat until all done)
             ↓
             Return AgentFinishAction(results)
```

### 11. Special Considerations

#### A. Shared Budget & Iterations
- budget_flag and iteration_flag are shared across parent and delegates
- PlannerAgent needs to allocate budget carefully
- Each subtask uses iterations from shared counter

#### B. Memory Management
- Store plan in pending_actions or custom memory
- Use state.inputs/outputs for plan data
- Consider condensation for long conversations

#### C. Error Handling
- When delegate fails (AgentState.ERROR), need strategy
- Can retry, skip, or reassign to different agent
- Report error and ask user for guidance

#### D. Result Synthesis
- When all subtasks done, synthesize results
- Compare against original goals
- Return in AgentFinishAction.outputs

## Testing Strategy

1. **Unit Test**: Test plan creation logic in isolation
2. **Integration Test**: Test with DummyAgent delegates
3. **E2E Test**: Test with real CodeActAgent
4. **Delegation Test**: Verify parent-child communication

## Key Differences from CodeActAgent

| Aspect | CodeActAgent | PlannerAgent |
|--------|-------------|-------------|
| **Primary Role** | Direct execution | Orchestration |
| **Tools** | Bash, edit, browser | Plan, delegate, think |
| **LLM Calls** | Multiple per task | Fewer, more strategic |
| **Agent Interaction** | N/A | Heavy use of delegation |
| **State Management** | Linear execution | Plan-based tracking |
| **Error Handling** | Retry directly | Reassign/report |

## Common Pitfalls

1. **Not updating plan state**: Track which subtasks completed
2. **Infinite delegation**: Ensure delegates make progress
3. **Budget mismanagement**: Plan should use budget wisely
4. **Missing context**: Pass sufficient context to delegates
5. **Ignoring delegation results**: Use results to adapt plan

## Resources

- Agent Base Class: `/openhands/controller/agent.py`
- AgentController: `/openhands/controller/agent_controller.py`
- CodeActAgent example: `/openhands/agenthub/codeact_agent/`
- Full Architecture Guide: `PLANNER_AGENT_ARCHITECTURE.md`
- Delegation Details: Section 6 of Architecture Guide
