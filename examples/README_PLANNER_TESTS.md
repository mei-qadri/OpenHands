# PlannerAgent Testing Examples

This directory contains ready-to-run scripts for testing the PlannerAgent on specific repositories with specific queries.

## Quick Start

### Option 1: Bash Script (Easiest)

```bash
# 1. Set your API key
export LLM_API_KEY=your-anthropic-or-openai-key

# 2. Edit the script to set your repository and task
nano test_planner_on_repo.sh

# 3. Run it
./test_planner_on_repo.sh
```

### Option 2: Python Script

```bash
# 1. Set your API key
export LLM_API_KEY=your-api-key

# 2. Run with defaults (tests on OpenHands itself)
python quick_test_planner.py

# 3. Or specify custom repository and task
python quick_test_planner.py /path/to/repo "Your task here"
```

### Option 3: Direct CLI Command

```bash
python -m openhands.core.main \
  --agent-name PlannerAgent \
  --directory /path/to/your/repo \
  --task "Add unit tests for the authentication module" \
  --llm-model claude-sonnet-4-5 \
  --llm-api-key $LLM_API_KEY
```

## Available Scripts

### 1. `test_planner_on_repo.sh`
- **Purpose**: Complete bash script with validation and reporting
- **Features**:
  - Checks repository exists
  - Validates API key
  - Shows git status before/after
  - Saves conversation history
  - Displays diff summary

**Edit these variables:**
```bash
REPO_PATH="/home/user/OpenHands"
TASK="Your task description here"
LLM_MODEL="claude-sonnet-4-5"
```

### 2. `quick_test_planner.py`
- **Purpose**: Python script for programmatic testing
- **Features**:
  - Shows agent initialization
  - Displays plan status every 5 iterations
  - Shows final plan summary
  - Can be used as a library

**Usage:**
```bash
# Default test
python quick_test_planner.py

# Custom repository
python quick_test_planner.py /path/to/repo

# Custom repository and task
python quick_test_planner.py /path/to/repo "Fix the login bug"
```

**Edit these constants in the file:**
```python
DEFAULT_REPO = "/home/user/OpenHands"
DEFAULT_TASK = "Your task here"
LLM_MODEL = "claude-sonnet-4-5"
```

### 3. `inspect_planner_agent.py`
- **Purpose**: Inspection without requiring API key
- **Features**:
  - Shows file structure
  - Lists available tools
  - Displays example plan
  - No API calls made

**Usage:**
```bash
python inspect_planner_agent.py
```

## Example Tasks to Try

### Simple (5-10 minutes)
```bash
# Documentation
"Add docstrings to all public methods in the PlannerAgent class"

# Simple feature
"Add a logger statement when a plan is created"

# Code cleanup
"Remove unused imports from the plan.py file"
```

### Medium (20-30 minutes)
```bash
# Testing
"Add unit tests for the PlanStep.is_ready_to_execute method"

# Feature
"Add a method to export the plan to JSON format"

# Refactoring
"Refactor the plan update logic to use a state machine pattern"
```

### Complex (1-2 hours)
```bash
# Full feature
"Add support for parallel execution of independent plan steps"

# Integration
"Add integration tests that test PlannerAgent with mock sub-agents"

# Research + Implementation
"Research and implement the best approach for plan visualization"
```

## Environment Variables

```bash
# Required
export LLM_API_KEY=your-api-key

# Optional
export LLM_MODEL=claude-sonnet-4-5  # or gpt-4, gpt-4-turbo
export LOG_LEVEL=DEBUG              # Enable debug logging
export MAX_ITERATIONS=50            # Override max iterations
```

## What You'll See

When you run these scripts, you'll see:

1. **Initialization**
   ```
   🚀 Initializing PlannerAgent...
   ✅ Agent initialized with 6 tools
   ```

2. **Plan Creation**
   ```
   [PlannerAgent] Created plan with 5 steps
   Steps:
   1. Analyze codebase (CodeActAgent)
   2. Implement feature (CodeActAgent)
   ...
   ```

3. **Execution Progress**
   ```
   [Iteration 3/30]
   Action type: AgentDelegateAction
   Delegating to CodeActAgent...
   ```

4. **Plan Updates**
   ```
   📋 Current Plan Status:
   Progress: 3/5 steps completed
   ```

5. **Completion**
   ```
   ✅ PlannerAgent completed the task!
   Final Summary: Successfully added unit tests...
   ```

## Troubleshooting

### "ModuleNotFoundError: No module named 'openhands'"
**Solution:**
```bash
cd /home/user/OpenHands
pip install -e .
```

### "LLM_API_KEY environment variable not set"
**Solution:**
```bash
# For Anthropic (Claude)
export LLM_API_KEY=sk-ant-...

# For OpenAI (GPT)
export LLM_API_KEY=sk-...
```

### "Repository not found"
**Solution:** Use absolute path:
```bash
REPO_PATH="$(pwd)/my-repo"  # Get absolute path
```

### Agent seems stuck
**Solution:** Enable verbose logging:
```bash
export LOG_LEVEL=DEBUG
python quick_test_planner.py
```

## Tips for Effective Testing

### Start Simple
Begin with a simple, well-defined task to verify the system works.

### Watch the Plan
Pay attention to how the plan is structured and how it evolves.

### Check Iterations
If it takes many iterations, the task might be too complex or ambiguous.

### Review Changes
After completion, review the actual code changes made:
```bash
git diff
```

### Save History
Use `--save-history` to preserve the conversation for analysis:
```bash
--save-history test_$(date +%Y%m%d_%H%M%S).json
```

## Next Steps

After running these tests:

1. **Try different task types** - features, bugs, refactoring, research
2. **Test on different repositories** - React apps, Python APIs, etc.
3. **Measure performance** - time, iterations, success rate
4. **Compare with CodeActAgent** - run same task with both agents
5. **Extend the agent** - add new tools, improve prompts

## Documentation

- **Full Testing Guide**: `../TESTING_WITH_REPOSITORY.md`
- **PlannerAgent README**: `../openhands/agenthub/planner_agent/README.md`
- **Design Document**: `../openhands/agenthub/planner_agent/DESIGN.md`
- **Usage Examples**: `../openhands/agenthub/planner_agent/EXAMPLE.md`

Happy testing! 🚀
