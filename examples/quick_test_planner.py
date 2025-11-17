#!/usr/bin/env python3
"""
Corrected test script for PlannerAgent.

This demonstrates the proper way to configure and use PlannerAgent.

Usage:
    export LLM_API_KEY=your-api-key
    python examples/quick_test_planner.py [repository] [task]
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_REPO = "/home/user/OpenHands"
DEFAULT_TASK = "Add type hints to the PlannerAgent.__init__ method"
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-5")
LLM_API_KEY = os.getenv("LLM_API_KEY")


def run_planner_test(repo_path: str, task: str):
    """Run PlannerAgent on the specified repository with the given task."""

    # Validation
    if not os.path.exists(repo_path):
        print(f"❌ Error: Repository not found at {repo_path}")
        sys.exit(1)

    if not LLM_API_KEY:
        print("❌ Error: LLM_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export LLM_API_KEY=your-api-key")
        sys.exit(1)

    # Display configuration
    print("=" * 70)
    print("PlannerAgent Quick Test")
    print("=" * 70)
    print(f"\n📂 Repository: {repo_path}")
    print(f"🤖 Agent: PlannerAgent")
    print(f"🧠 LLM Model: {LLM_MODEL}")
    print(f"\n📝 Task:\n  {task}")
    print("\n" + "=" * 70)

    # Change to repository directory
    original_dir = os.getcwd()
    os.chdir(repo_path)

    # Import OpenHands components
    try:
        from openhands.agenthub.planner_agent import PlannerAgent
        from openhands.controller.state.state import State
        from openhands.core.config import AgentConfig, LLMConfig
        from openhands.core.config.openhands_config import OpenHandsConfig
        from openhands.events.action import AgentFinishAction, MessageAction
        from openhands.events.event import EventSource
        from openhands.llm.llm_registry import LLMRegistry
    except ImportError as e:
        print(f"\n❌ Error importing OpenHands: {e}")
        print("\nMake sure OpenHands is installed:")
        print("  pip install -e .")
        sys.exit(1)

    # CORRECT WAY: Create OpenHandsConfig with LLMConfig
    print("\n🚀 Initializing PlannerAgent...")

    # Step 1: Create LLM configuration
    llm_config = LLMConfig(model=LLM_MODEL, api_key=LLM_API_KEY)

    # Step 2: Create OpenHands configuration
    openhands_config = OpenHandsConfig()
    openhands_config.set_llm_config(llm_config)  # Set the default LLM config

    # Step 3: Create LLM Registry from the config
    llm_registry = LLMRegistry(config=openhands_config)

    # Step 4: Create Agent configuration (no parameters needed)
    agent_config = AgentConfig()

    # Step 5: Create the agent
    try:
        agent = PlannerAgent(config=agent_config, llm_registry=llm_registry)
        print(f"✅ Agent initialized with {len(agent.tools)} tools")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Create initial state with user message
    state = State()
    user_message = MessageAction(content=task)
    user_message._source = EventSource.USER
    state.history.append(user_message)

    # Run agent loop
    print("\n🔄 Executing agent loop...")
    print("-" * 70)

    max_iterations = 30
    for iteration in range(max_iterations):
        print(f"\n[Iteration {iteration + 1}/{max_iterations}]")

        try:
            # Get next action
            action = agent.step(state)
            action_type = action.__class__.__name__
            print(f"Action type: {action_type}")

            # Show message if available
            if hasattr(action, 'message'):
                print(f"Message: {action.message[:200]}...")

            # Add to history
            state.history.append(action)

            # Check if done
            if isinstance(action, AgentFinishAction):
                print("\n" + "=" * 70)
                print("✅ PlannerAgent completed the task!")
                print("=" * 70)
                if action.final_thought:
                    print(f"\n📊 Final Summary:\n  {action.final_thought}")

                if action.outputs:
                    print(f"\n📤 Outputs:")
                    for key, value in action.outputs.items():
                        print(f"  - {key}: {value}")
                break

            # Show current plan periodically
            if agent.current_plan and (iteration + 1) % 5 == 0:
                print("\n📋 Current Plan Status:")
                summary_lines = agent.current_plan.get_summary().split('\n')
                for line in summary_lines[:10]:  # Show first 10 lines
                    print(f"  {line}")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            import traceback

            traceback.print_exc()
            break

    else:
        print("\n⚠️  Reached maximum iterations without completion")

    # Show final plan
    if agent.current_plan:
        print("\n" + "=" * 70)
        print("📋 Final Plan:")
        print("=" * 70)
        print(agent.current_plan.get_summary())

    # Restore directory
    os.chdir(original_dir)

    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)


def main():
    """Main entry point."""
    repo_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPO
    task = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TASK

    run_planner_test(repo_path, task)


if __name__ == "__main__":
    main()
