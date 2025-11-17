#!/usr/bin/env python3
"""
Simple test script for PlannerAgent.

This script demonstrates how to use the PlannerAgent programmatically.
It creates a simple test scenario and shows the agent's planning behavior.

Usage:
    python examples/test_planner_agent.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openhands.agenthub.planner_agent import PlannerAgent
from openhands.controller.agent import Agent
from openhands.core.config import AgentConfig, LLMConfig


def verify_registration():
    """Verify PlannerAgent is registered."""
    print("🔍 Verifying agent registration...")
    agents = Agent.list_agents()
    print(f"   Registered agents: {', '.join(agents)}")

    if 'PlannerAgent' in agents:
        print("   ✅ PlannerAgent is registered!\n")
        return True
    else:
        print("   ❌ PlannerAgent not found in registry\n")
        return False


def inspect_planner_agent():
    """Inspect PlannerAgent configuration."""
    print("🔧 Inspecting PlannerAgent...")

    # Create a dummy config (no API calls will be made)
    llm_config = LLMConfig(
        model='gpt-4',
        api_key='dummy-key-for-inspection',
    )

    agent_config = AgentConfig(agent_name='PlannerAgent', llm_config=llm_config)

    # This would normally require a proper LLM registry, but we can inspect the class
    print(f"   Agent class: {PlannerAgent.__name__}")
    print(f"   Version: {PlannerAgent.VERSION}")
    print(f"   Module: {PlannerAgent.__module__}")

    # Show available methods
    methods = [
        m for m in dir(PlannerAgent) if not m.startswith('_') and callable(getattr(PlannerAgent, m))
    ]
    print(f"   Key methods: {', '.join(methods[:10])}...")
    print()


def show_planning_tools():
    """Show available planning tools."""
    print("🛠️  Available Planning Tools:")

    from openhands.agenthub.planner_agent.tools import get_planner_tools

    tools = get_planner_tools()
    for i, tool in enumerate(tools, 1):
        function_name = tool['function']['name']
        description = tool['function']['description'].split('\n')[0]
        print(f"   {i}. {function_name}: {description}")
    print()


def show_example_plan():
    """Show example plan structure."""
    print("📋 Example Plan Structure:")

    from openhands.agenthub.planner_agent.plan import (
        ExecutionPlan,
        PlanStep,
        StepStatus,
    )

    # Create example plan
    plan = ExecutionPlan(
        goal='Add a contact form to the homepage',
        steps=[
            PlanStep(
                id='step1',
                description='Analyze current homepage structure',
                agent_type='CodeActAgent',
                inputs={'task': 'Examine homepage files'},
                status=StepStatus.COMPLETED,
            ),
            PlanStep(
                id='step2',
                description='Create contact form component',
                agent_type='CodeActAgent',
                inputs={'task': 'Create React component'},
                status=StepStatus.IN_PROGRESS,
            ),
            PlanStep(
                id='step3',
                description='Add backend endpoint',
                agent_type='CodeActAgent',
                inputs={'task': 'Create API endpoint'},
                status=StepStatus.PENDING,
                dependencies=['step2'],
            ),
        ],
        context={'framework': 'React', 'backend': 'Express'},
    )

    # Show plan summary
    print(plan.get_summary())

    # Show plan details
    print('   Steps Detail:')
    for step in plan.steps:
        status_emoji = {
            StepStatus.PENDING: '⏳',
            StepStatus.IN_PROGRESS: '🔄',
            StepStatus.COMPLETED: '✅',
            StepStatus.FAILED: '❌',
        }.get(step.status, '❓')

        print(
            f"      {status_emoji} {step.id}: {step.description} ({step.agent_type})"
        )

    print()


def show_usage_example():
    """Show code example for using PlannerAgent."""
    print("💡 Usage Example:")
    print(
        """
   from openhands.core.config import AgentConfig, LLMConfig
   from openhands.llm.llm_registry import LLMRegistry
   from openhands.agenthub.planner_agent import PlannerAgent
   from openhands.controller.state.state import State
   from openhands.events.action import MessageAction

   # Configure
   llm_config = LLMConfig(
       model="claude-sonnet-4-5",
       api_key="your-api-key"
   )
   agent_config = AgentConfig(agent_name="PlannerAgent", llm_config=llm_config)

   # Create agent
   llm_registry = LLMRegistry()
   agent = PlannerAgent(agent_config, llm_registry)

   # Create state with user message
   state = State()
   state.history.append(MessageAction(content="Add a contact form"))

   # Run agent step
   action = agent.step(state)
   print(f"Agent action: {action}")

   # The agent will:
   # 1. Analyze the request
   # 2. Create a plan
   # 3. Delegate to specialized agents
   # 4. Refine based on feedback
   # 5. Complete the task
"""
    )


def main():
    """Main test function."""
    print('=' * 70)
    print('PlannerAgent Test & Inspection')
    print('=' * 70)
    print()

    # 1. Verify registration
    if not verify_registration():
        print('⚠️  Cannot proceed - PlannerAgent not registered')
        return

    # 2. Inspect agent
    inspect_planner_agent()

    # 3. Show tools
    show_planning_tools()

    # 4. Show example plan
    show_example_plan()

    # 5. Show usage
    show_usage_example()

    # 6. Summary
    print('=' * 70)
    print('✅ PlannerAgent is ready to use!')
    print()
    print('Next steps:')
    print('  1. Set your LLM API key: export LLM_API_KEY=your-key')
    print('  2. Run with CLI: python -m openhands.core.main --agent-name PlannerAgent')
    print('  3. Or integrate into your code (see example above)')
    print()
    print('📚 Documentation:')
    print('  - Design: openhands/agenthub/planner_agent/DESIGN.md')
    print('  - Usage: openhands/agenthub/planner_agent/README.md')
    print('  - Examples: openhands/agenthub/planner_agent/EXAMPLE.md')
    print('  - Testing: test_planner_agent.md')
    print('=' * 70)


if __name__ == '__main__':
    main()
