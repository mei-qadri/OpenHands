# Testing the PlannerAgent

## Quick Start Guide

### Option 1: Using OpenHands CLI

1. **Set up your environment:**
   ```bash
   # Make sure you're in the OpenHands directory
   cd /home/user/OpenHands

   # Install dependencies (if not already installed)
   pip install -e .
   ```

2. **Configure your LLM API key:**
   ```bash
   # Add to .env file
   echo "LLM_API_KEY=your-api-key-here" >> .env
   echo "LLM_MODEL=claude-sonnet-4-5" >> .env  # or gpt-4, etc.
   ```

3. **Run OpenHands with PlannerAgent:**
   ```bash
   # Method 1: Using CLI with agent flag
   python -m openhands.core.main \
     --agent-name PlannerAgent \
     --llm-model claude-sonnet-4-5 \
     --task "Add a contact form to the homepage"

   # Method 2: Interactive mode
   python -m openhands.core.main --agent-name PlannerAgent
   ```

### Option 2: Using Python Script

Create a test script:

```python
# test_planner.py
import asyncio
from openhands.core.config import AgentConfig, LLMConfig
from openhands.llm.llm_registry import LLMRegistry
from openhands.agenthub.planner_agent import PlannerAgent
from openhands.controller.state.state import State
from openhands.events.action import MessageAction
from openhands.events.event import EventSource

async def test_planner_agent():
    # Configure LLM
    llm_config = LLMConfig(
        model="claude-sonnet-4-5",  # or "gpt-4", etc.
        api_key="your-api-key-here"
    )

    # Configure Agent
    agent_config = AgentConfig(
        agent_name="PlannerAgent",
        llm_config=llm_config
    )

    # Create LLM registry and agent
    llm_registry = LLMRegistry()
    agent = PlannerAgent(agent_config, llm_registry)

    # Create initial state
    state = State()

    # Add user message
    user_message = MessageAction(
        content="Add a simple contact form to the homepage with name, email, and message fields"
    )
    user_message._source = EventSource.USER
    state.history.append(user_message)

    # Get agent's first step
    print("Starting PlannerAgent...")
    action = agent.step(state)
    print(f"Action: {action}")

    # Continue stepping through the agent's actions
    # In a real system, you'd process observations and continue the loop

if __name__ == "__main__":
    asyncio.run(test_planner_agent())
```

Run it:
```bash
python test_planner.py
```

### Option 3: Using OpenHands Web UI

1. **Start the OpenHands server:**
   ```bash
   make run
   ```

2. **Open browser:**
   ```
   http://localhost:3000
   ```

3. **Select PlannerAgent:**
   - In the UI, go to Settings
   - Select "PlannerAgent" from the agent dropdown
   - Start a conversation

## Good Test Queries

### Beginner (Simple Planning)
```
"Add a contact form to the homepage"
"Fix the broken login button"
"Add dark mode to the application"
```

### Intermediate (Multi-Step)
```
"Add user authentication with JWT tokens"
"Create a blog feature with markdown support"
"Implement a search functionality for the product catalog"
```

### Advanced (Complex Coordination)
```
"Refactor the authentication system to use OAuth2"
"Add a dashboard with analytics and charts"
"Implement a CI/CD pipeline for the project"
```

### Research + Implementation
```
"Research and implement the best practice for caching in this application"
"Add a real-time notification system using WebSockets"
"Migrate the database from MySQL to PostgreSQL"
```

## What to Observe

When testing, watch for:

### 1. Plan Creation
The agent should create a structured plan like:
```
Created execution plan for: [goal]

Steps:
1. Analyze current codebase (using CodeActAgent)
2. Research best practices (using BrowsingAgent)
3. Implement feature (using CodeActAgent)
4. Write tests (using CodeActAgent)
5. Verify functionality (using CodeActAgent)
```

### 2. Delegation
Look for delegation messages:
```
Delegating step analyze_stack to CodeActAgent
```

### 3. Plan Updates
Watch for plan refinements:
```
Updated plan - Step 'analyze_stack' marked as completed
```

### 4. Thinking Process
The agent should show reasoning:
```
I am thinking...: The user wants to add a contact form.
This requires understanding the frontend framework first.
```

## Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
python -m openhands.core.main --agent-name PlannerAgent
```

### View Current Plan
If you want to see the plan at any point, the agent responds to:
```
"What's the current plan?"
"Show me the plan status"
```

### Check Agent Registration
Verify PlannerAgent is registered:
```python
python -c "from openhands.controller.agent import Agent; print(Agent.list_agents())"
```

Should show: `['CodeActAgent', 'DummyAgent', 'BrowsingAgent', 'PlannerAgent', ...]`

## Expected Behavior

### Successful Flow
1. ✅ Agent receives user query
2. ✅ Creates a structured plan with steps
3. ✅ Delegates first step to appropriate agent
4. ✅ Receives observation from sub-agent
5. ✅ Updates plan with results
6. ✅ Continues with next steps
7. ✅ Refines plan if needed
8. ✅ Completes when all steps done

### What Success Looks Like
```
[PlannerAgent] Created plan with 5 steps: Add contact form to homepage
[PlannerAgent] Delegating step analyze_stack to CodeActAgent
[CodeActAgent] Found React 18 application
[PlannerAgent] Updated plan - Step 'analyze_stack' status: completed
[PlannerAgent] Delegating step create_component to CodeActAgent
[CodeActAgent] Created ContactForm component
[PlannerAgent] Updated plan - Step 'create_component' status: completed
...
[PlannerAgent] All steps completed successfully
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'openhands'"
**Solution:** Install OpenHands in development mode:
```bash
pip install -e .
```

### Problem: "Agent 'PlannerAgent' not found"
**Solution:** Make sure the registration is working:
```bash
python -c "from openhands.agenthub import planner_agent; print('Success')"
```

### Problem: LLM not generating tool calls
**Solution:**
- Make sure you're using a model that supports function calling
- Recommended: claude-sonnet-4-5, gpt-4, gpt-4-turbo
- Check API key is valid

### Problem: Agent doesn't create plans
**Solution:**
- Check the system prompt is loaded correctly
- Verify tools are registered: `print(agent.tools)`
- Enable debug logging to see LLM responses

## Sample Test Session

Here's a complete test you can run:

```bash
# 1. Create test query file
cat > test_query.txt << 'EOF'
Add a simple contact form to the homepage with the following:
- Name field (required)
- Email field (required, with validation)
- Message textarea (required)
- Submit button
- Basic styling to match the existing page
EOF

# 2. Run PlannerAgent
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --task "$(cat test_query.txt)" \
  --llm-model claude-sonnet-4-5 \
  --max-iterations 20
```

## Evaluating Performance

Good indicators that PlannerAgent is working well:

✅ **Planning Quality**
- Breaks task into logical steps
- Identifies correct agents for each step
- Includes necessary verification/testing steps

✅ **Adaptation**
- Refines plan when encountering issues
- Adds steps when discovering new requirements
- Handles failures gracefully

✅ **Efficiency**
- Doesn't create unnecessary steps
- Respects dependencies properly
- Completes tasks successfully

✅ **Transparency**
- Clear plan descriptions
- Visible reasoning process
- Documented refinements

## Next Steps

After testing:

1. **Try different task types:**
   - Feature implementation
   - Bug fixes
   - Refactoring
   - Research tasks

2. **Test edge cases:**
   - Tasks that fail midway
   - Tasks requiring plan refinement
   - Tasks needing multiple agent types

3. **Benchmark performance:**
   - Compare vs. CodeActAgent on same task
   - Measure success rate
   - Track iteration counts

4. **Extend functionality:**
   - Add new planning tools
   - Improve system prompt
   - Add parallel execution (future)

Happy testing! 🚀
