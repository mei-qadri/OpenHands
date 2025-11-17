#!/bin/bash
# Test PlannerAgent on a Specific Repository
# Usage: ./test_planner_on_repo.sh

set -e  # Exit on error

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# Repository to test on (use absolute path)
REPO_PATH="/home/user/OpenHands"  # Change this to your repository

# Task to execute
TASK="Add comprehensive docstrings to the PlannerAgent class methods"

# LLM Configuration
LLM_MODEL="${LLM_MODEL:-claude-sonnet-4-5}"  # or gpt-4, gpt-4-turbo, etc.
LLM_API_KEY="${LLM_API_KEY:-}"  # Set via environment variable

# Execution limits
MAX_ITERATIONS=50
VERBOSE=true

# ============================================================================
# VALIDATION
# ============================================================================

echo "=================================================="
echo "PlannerAgent Repository Test"
echo "=================================================="
echo ""

# Check if repository exists
if [ ! -d "$REPO_PATH" ]; then
    echo "❌ Error: Repository not found at $REPO_PATH"
    exit 1
fi

# Check if API key is set
if [ -z "$LLM_API_KEY" ]; then
    echo "❌ Error: LLM_API_KEY environment variable not set"
    echo ""
    echo "Please set your API key:"
    echo "  export LLM_API_KEY=your-api-key"
    echo ""
    exit 1
fi

# Navigate to repository
cd "$REPO_PATH"
echo "📂 Repository: $REPO_PATH"
echo "🌲 Current git status:"
git status --short || echo "  (Not a git repository)"
echo ""

# ============================================================================
# DISPLAY CONFIGURATION
# ============================================================================

echo "⚙️  Configuration:"
echo "  Repository: $REPO_PATH"
echo "  LLM Model: $LLM_MODEL"
echo "  Max Iterations: $MAX_ITERATIONS"
echo "  Verbose: $VERBOSE"
echo ""
echo "📝 Task:"
echo "  $TASK"
echo ""

# Confirm before proceeding
read -p "Proceed with test? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Test cancelled."
    exit 0
fi

# ============================================================================
# RUN PLANNER AGENT
# ============================================================================

echo ""
echo "🚀 Starting PlannerAgent..."
echo "=================================================="
echo ""

# Build command
CMD="python -m openhands.core.main"
CMD="$CMD --agent-name PlannerAgent"
CMD="$CMD --directory $REPO_PATH"
CMD="$CMD --task \"$TASK\""
CMD="$CMD --llm-model $LLM_MODEL"
CMD="$CMD --llm-api-key $LLM_API_KEY"
CMD="$CMD --max-iterations $MAX_ITERATIONS"

if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

# Save history with timestamp
HISTORY_FILE="planner_test_$(date +%Y%m%d_%H%M%S).json"
CMD="$CMD --save-history $HISTORY_FILE"

# Execute
echo "Running: $CMD"
echo ""

eval $CMD

# ============================================================================
# SHOW RESULTS
# ============================================================================

echo ""
echo "=================================================="
echo "✅ Test Completed!"
echo "=================================================="
echo ""

# Show changes
echo "📊 Changes made to repository:"
git status --short || echo "(Not a git repository)"
echo ""

if [ -f "$HISTORY_FILE" ]; then
    echo "💾 Conversation history saved to: $HISTORY_FILE"
    echo ""
fi

# Show diff summary
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "📈 Diff summary:"
    git diff --stat
    echo ""

    echo "To see full changes:"
    echo "  git diff"
    echo ""
    echo "To commit changes:"
    echo "  git add ."
    echo "  git commit -m \"[PlannerAgent] $TASK\""
fi

echo "=================================================="
