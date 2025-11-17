#!/usr/bin/env python3
"""
Quick test script for PlannerAgent on a specific repository.

Usage:
    # Set your API key
    export LLM_API_KEY=your-api-key

    # Run the script
    python examples/quick_test_planner.py

    # Or with custom values
    python examples/quick_test_planner.py /path/to/repo "Your task here"
"""

import os
import sys

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# Repository path (default to current OpenHands repo)
DEFAULT_REPO = "/home/user/OpenHands"

# Default task
DEFAULT_TASK = "Add type hints to the PlannerAgent.__init__ method"

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-5")
LLM_API_KEY = os.getenv("LLM_API_KEY")

# ============================================================================
# MAIN TEST FUNCTION
# ============================================================================


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
        from openhands.core.config import AgentConfig, LLMConfig
        from openhands.llm.llm_registry import LLMRegistry
        from openhands.agenthub.planner_agent import PlannerAgent
        from openhands.controller.state.state import State
        from openhands.events.action import MessageAction, AgentFinishAction
        from openhands.events.event import EventSource
    except ImportError as e:
        print(f"\n❌ Error importing OpenHands: {e}")
        print("\nMake sure OpenHands is installed:")
        print("  pip install -e .")
        sys.exit(1)

    # Configure LLM
    llm_config = LLMConfig(model=LLM_MODEL, api_key=LLM_API_KEY)

    # Configure Agent
    agent_config = AgentConfig(agent_name="PlannerAgent", llm_config=llm_config)

    # Create agent
    print("\n🚀 Initializing PlannerAgent...")
    llm_registry = LLMRegistry()
    agent = PlannerAgent(agent_config, llm_registry)
    print(f"✅ Agent initialized with {len(agent.tools)} tools")

    # Create initial state
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
            print(f"Action type: {action.__class__.__name__}")
            print(f"Action: {action.message if hasattr(action, 'message') else action}")

            # Add to history
            state.history.append(action)

            # Check if done
            if isinstance(action, AgentFinishAction):
                print("\n" + "=" * 70)
                print("✅ PlannerAgent completed the task!")
                print("=" * 70)
                print(f"\n📊 Final Summary:")
                print(f"  {action.final_thought}")

                if action.outputs:
                    print(f"\n📤 Outputs:")
                    for key, value in action.outputs.items():
                        print(f"  - {key}: {value}")
                break

            # Show current plan if available
            if agent.current_plan and iteration % 5 == 0:
                print("\n📋 Current Plan Status:")
                print(agent.current_plan.get_summary())

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
        print("\nSteps:")
        for step in agent.current_plan.steps:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'failed': '❌',
                'blocked': '🚫',
            }.get(step.status.value, '❓')
            print(f"  {status_emoji} {step.id}: {step.description}")
            if step.result:
                print(f"      Result: {step.result[:100]}...")

    # Restore directory
    os.chdir(original_dir)

    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================


def main():
    """Main entry point."""
    # Parse command line arguments
    repo_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPO
    task = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TASK

    # Run test
    run_planner_test(repo_path, task)


if __name__ == "__main__":
    main()
