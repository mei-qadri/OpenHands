# Testing PlannerAgent with a Specific Repository and Query

## Quick Start - Test on a Repository

### Method 1: Using OpenHands CLI (Recommended)

```bash
# Basic syntax
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --directory /path/to/your/repository \
  --task "Your task description here"

# Example 1: Test on OpenHands itself
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --directory /home/user/OpenHands \
  --task "Add unit tests for the PlannerAgent class" \
  --llm-model claude-sonnet-4-5 \
  --llm-api-key your-api-key

# Example 2: Test on a React app
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --directory /path/to/my-react-app \
  --task "Add a dark mode toggle to the settings page" \
  --llm-model gpt-4 \
  --llm-api-key your-openai-key

# Example 3: Bug fix on existing repo
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --directory /path/to/your/project \
  --task "Fix the memory leak in the data processing module" \
  --max-iterations 30
```

### Method 2: Using Environment Variables

```bash
# Set up environment
export WORKSPACE_BASE=/path/to/your/repository
export LLM_MODEL=claude-sonnet-4-5
export LLM_API_KEY=your-api-key

# Run with task
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --task "Refactor the authentication system to use OAuth2"
```

### Method 3: Using Configuration File

Create a config file `planner_test_config.toml`:

```toml
[core]
workspace_base = "/path/to/your/repository"
agent_name = "PlannerAgent"
max_iterations = 50

[llm]
model = "claude-sonnet-4-5"
api_key = "your-api-key-here"

[agent]
# Any agent-specific configs
```

Then run:
```bash
python -m openhands.core.main --config planner_test_config.toml --task "Your task here"
```

### Method 4: Programmatic with Specific Repository

Create `test_on_repo.py`:

```python
#!/usr/bin/env python3
import os
from openhands.core.config import AgentConfig, LLMConfig, AppConfig
from openhands.llm.llm_registry import LLMRegistry
from openhands.agenthub.planner_agent import PlannerAgent
from openhands.controller.state.state import State
from openhands.events.action import MessageAction
from openhands.events.event import EventSource

# Configuration
REPO_PATH = "/path/to/your/repository"
TASK = "Add input validation to the user registration form"

def test_planner_on_repo():
    # Change to repository directory
    os.chdir(REPO_PATH)

    # Configure LLM
    llm_config = LLMConfig(
        model="claude-sonnet-4-5",
        api_key=os.getenv("LLM_API_KEY")
    )

    # Configure Agent
    agent_config = AgentConfig(
        agent_name="PlannerAgent",
        llm_config=llm_config
    )

    # Create agent
    llm_registry = LLMRegistry()
    agent = PlannerAgent(agent_config, llm_registry)

    # Create initial state with user task
    state = State()
    user_message = MessageAction(content=TASK)
    user_message._source = EventSource.USER
    state.history.append(user_message)

    print(f"Testing PlannerAgent on: {REPO_PATH}")
    print(f"Task: {TASK}")
    print("-" * 70)

    # Run agent step by step
    max_iterations = 30
    for i in range(max_iterations):
        print(f"\nIteration {i + 1}/{max_iterations}")

        # Get next action from agent
        action = agent.step(state)
        print(f"Action: {action}")

        # Add action to history
        state.history.append(action)

        # Check if agent is done
        from openhands.events.action import AgentFinishAction
        if isinstance(action, AgentFinishAction):
            print("\n✅ Agent completed the task!")
            print(f"Final thought: {action.final_thought}")
            break

        # In a real scenario, you'd execute the action and get an observation
        # For this test, we're just showing the flow

    # Show final plan if available
    if agent.current_plan:
        print("\n" + "=" * 70)
        print("Final Plan Summary:")
        print(agent.current_plan.get_summary())

if __name__ == "__main__":
    test_planner_on_repo()
```

Run it:
```bash
export LLM_API_KEY=your-api-key
python test_on_repo.py
```

## Complete Example: Testing on a Sample Repository

Let's test on a real repository with a concrete task:

```bash
# 1. Clone a sample repository (or use your own)
cd /tmp
git clone https://github.com/example/sample-react-app
cd sample-react-app

# 2. Run PlannerAgent with a specific task
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --directory /tmp/sample-react-app \
  --task "Add a search functionality to filter the product list. \
         It should search by product name and category, \
         update results in real-time as the user types, \
         and be accessible from the main products page." \
  --llm-model claude-sonnet-4-5 \
  --llm-api-key sk-ant-... \
  --max-iterations 50 \
  --verbose
```

## What You'll See During Execution

### Phase 1: Repository Analysis
```
[PlannerAgent] Analyzing repository structure...
[PlannerAgent] Found React application with:
  - src/components/ProductList.jsx
  - src/pages/Products.jsx
  - Backend API at src/api/
```

### Phase 2: Plan Creation
```
[PlannerAgent] Created execution plan for: Add search functionality

Steps:
1. Analyze current ProductList component (CodeActAgent)
2. Design search state management (CodeActAgent)
3. Implement search input UI (CodeActAgent)
4. Add filtering logic (CodeActAgent)
5. Connect to backend API if needed (CodeActAgent)
6. Add tests (CodeActAgent)
7. Verify functionality (CodeActAgent)
```

### Phase 3: Step-by-Step Execution
```
[PlannerAgent] Delegating step 'analyze_component' to CodeActAgent
[CodeActAgent] Reading src/components/ProductList.jsx...
[CodeActAgent] Component uses useState, receives products as props
[PlannerAgent] Updated plan - step 'analyze_component' completed

[PlannerAgent] Delegating step 'implement_search' to CodeActAgent
[CodeActAgent] Adding search input and filter logic...
[CodeActAgent] Created SearchBar component
[PlannerAgent] Updated plan - step 'implement_search' completed
...
```

### Phase 4: Completion
```
[PlannerAgent] All steps completed!
Summary: Successfully added real-time search functionality.
  - Created SearchBar component
  - Added filtering logic to ProductList
  - Implemented case-insensitive search
  - All tests passing
```

## Useful Command-Line Options

```bash
# Enable verbose logging to see everything
--verbose

# Increase iteration limit for complex tasks
--max-iterations 100

# Use specific LLM model
--llm-model claude-sonnet-4-5
--llm-model gpt-4-turbo
--llm-model gpt-4o

# Set workspace directory
--directory /path/to/repo
--workspace-base /path/to/repo

# Save conversation history
--save-history output.json

# Resume from previous run
--resume-from output.json
```

## Example Tasks by Repository Type

### For a React/Frontend Repository:
```bash
# UI Enhancement
--task "Add a modal dialog for user profile editing"

# State Management
--task "Migrate from Redux to Zustand for state management"

# Accessibility
--task "Add ARIA labels and keyboard navigation to the dashboard"

# Testing
--task "Add comprehensive unit tests for the authentication flow"
```

### For a Python/Backend Repository:
```bash
# API Development
--task "Add a REST API endpoint for exporting user data to CSV"

# Database
--task "Add database migration to support multi-tenancy"

# Performance
--task "Optimize the data processing pipeline to reduce memory usage"

# Security
--task "Add rate limiting to all API endpoints"
```

### For a Full-Stack Repository:
```bash
# Feature Development
--task "Add real-time notifications using WebSockets"

# Integration
--task "Integrate Stripe payment processing for subscriptions"

# Deployment
--task "Set up CI/CD pipeline with GitHub Actions"
```

## Monitoring the Agent's Progress

### View the Current Plan
While the agent is running, you can check its plan state programmatically:

```python
# In your test script
if agent.current_plan:
    print("\n📋 Current Plan:")
    for step in agent.current_plan.steps:
        status_icon = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'failed': '❌'
        }.get(step.status.value, '❓')
        print(f"{status_icon} {step.id}: {step.description}")
```

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
python -m openhands.core.main --agent-name PlannerAgent ...
```

### Watch Files Being Modified
```bash
# In another terminal, watch the repository
watch -n 2 'git status --short'
```

## Testing Strategy: Start Simple, Then Complex

### 1. Simple Test (5-10 minutes)
```bash
--task "Add a comment to explain what the main() function does"
```
This tests basic planning with minimal steps.

### 2. Medium Test (20-30 minutes)
```bash
--task "Add input validation to the registration form with error messages"
```
This tests multi-step planning and refinement.

### 3. Complex Test (1-2 hours)
```bash
--task "Add a complete user authentication system with login, signup, \
       password reset, and email verification"
```
This tests full planning, multi-agent coordination, and adaptation.

## Example: Complete Test Session

```bash
#!/bin/bash
# complete_test.sh - Full PlannerAgent test

# Configuration
export REPO_PATH="/path/to/your/repo"
export LLM_API_KEY="your-api-key"
export LLM_MODEL="claude-sonnet-4-5"

# Navigate to repo
cd "$REPO_PATH"

# Show initial state
echo "📂 Repository: $REPO_PATH"
echo "🌲 Git status:"
git status --short

# Define task
TASK="Add a search bar to the product listing page that filters products \
in real-time as the user types. Include tests."

# Run PlannerAgent
echo ""
echo "🤖 Starting PlannerAgent..."
echo "📝 Task: $TASK"
echo ""

python -m openhands.core.main \
  --agent-name PlannerAgent \
  --directory "$REPO_PATH" \
  --task "$TASK" \
  --llm-model "$LLM_MODEL" \
  --llm-api-key "$LLM_API_KEY" \
  --max-iterations 50 \
  --verbose \
  --save-history planner_test_$(date +%Y%m%d_%H%M%S).json

# Show what changed
echo ""
echo "📊 Changes made:"
git status --short
git diff --stat
```

Make it executable and run:
```bash
chmod +x complete_test.sh
./complete_test.sh
```

## Troubleshooting

### Issue: "Cannot find repository"
**Solution:** Make sure the path is absolute:
```bash
--directory "$(pwd)/my-repo"  # Use full path
```

### Issue: "Agent stuck in loop"
**Solution:** Increase max iterations or simplify the task:
```bash
--max-iterations 100
```

### Issue: "Plan not adapting"
**Solution:** Enable verbose logging to see the agent's reasoning:
```bash
--verbose
export LOG_LEVEL=DEBUG
```

## Expected Results

After running PlannerAgent on your repository, you should see:

✅ **A structured plan** with logical steps
✅ **Delegations** to appropriate agents (CodeActAgent, BrowsingAgent)
✅ **Progress updates** as each step completes
✅ **Plan refinements** if the agent discovers new requirements
✅ **Modified files** in your repository
✅ **A summary** of what was accomplished

The key advantage of PlannerAgent is that you'll see the **thinking process** - not just the final result!

---

Now you're ready to test PlannerAgent on any repository with any task! 🚀
