# PlannerAgent

A meta-agent for OpenHands that orchestrates complex tasks through hierarchical planning and delegation.

## Overview

The PlannerAgent is a sophisticated orchestration layer that sits above specialized agents like CodeActAgent and BrowsingAgent. It enables:

- **Hierarchical Task Decomposition**: Breaking down complex tasks into manageable steps
- **Intelligent Agent Selection**: Choosing the right specialized agent for each sub-task
- **Adaptive Planning**: Refining plans based on execution feedback
- **Explicit Reasoning**: Making the planning process transparent and debuggable

## Architecture

### Core Components

1. **PlannerAgent**: The main agent class that orchestrates execution
2. **ExecutionPlan**: Data structure representing the plan with steps and dependencies
3. **PlanStep**: Individual step with status, agent assignment, and results
4. **Planning Tools**: Functions for creating, updating, and executing plans

### Workflow

```
┌─────────────────────────────────────────────┐
│  User Query                                 │
│  "Add authentication to my web app"         │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  1. Analyze & Create Plan                   │
│  ├─ Parse user intent                       │
│  ├─ Understand repository context           │
│  └─ Break into logical steps                │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  2. Execute Steps (Loop)                    │
│  ┌────────────────────────────────────┐    │
│  │ Select next ready step             │    │
│  │         ↓                          │    │
│  │ Delegate to specialized agent      │    │
│  │         ↓                          │    │
│  │ Collect observation/feedback       │    │
│  │         ↓                          │    │
│  │ Update plan & refine if needed     │    │
│  │         ↓                          │    │
│  │ Loop until complete                │    │
│  └────────────────────────────────────┘    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  3. Return Results                          │
│  └─ Aggregate outputs                       │
│  └─ Provide summary                         │
└─────────────────────────────────────────────┘
```

## Usage

### Basic Usage

```python
from openhands.core.config import AgentConfig
from openhands.llm.llm_registry import LLMRegistry
from openhands.agenthub.planner_agent import PlannerAgent

# Create agent configuration
config = AgentConfig(
    agent_name='PlannerAgent',
    # ... other configuration options
)

# Create LLM registry
llm_registry = LLMRegistry()

# Initialize PlannerAgent
planner = PlannerAgent(config, llm_registry)

# The agent will automatically:
# 1. Analyze the user's request
# 2. Create a plan with steps
# 3. Delegate to specialized agents
# 4. Refine based on feedback
# 5. Complete the task
```

### Configuration

The PlannerAgent uses the standard OpenHands agent configuration. Key options:

```python
AgentConfig(
    agent_name='PlannerAgent',
    llm_config=LLMConfig(
        model='claude-3-sonnet',  # or other models
        api_key='your-api-key',
    ),
    # Standard agent config options...
)
```

## Planning Tools

The PlannerAgent has access to specialized tools:

### create_plan

Creates an execution plan with steps.

```json
{
  "goal": "Add user authentication",
  "steps": [
    {
      "id": "step1",
      "description": "Analyze current codebase",
      "agent_type": "CodeActAgent",
      "inputs": {"task": "Find backend framework and user models"},
      "dependencies": []
    },
    {
      "id": "step2",
      "description": "Research auth patterns",
      "agent_type": "BrowsingAgent",
      "inputs": {"task": "Research JWT authentication best practices"},
      "dependencies": []
    },
    {
      "id": "step3",
      "description": "Implement auth",
      "agent_type": "CodeActAgent",
      "inputs": {"task": "Implement JWT authentication"},
      "dependencies": ["step1", "step2"]
    }
  ]
}
```

### update_plan

Updates plan based on execution results.

```json
{
  "step_id": "step1",
  "status": "completed",
  "result": "Found Express.js with MongoDB, User model exists",
  "refinement_reason": "Step completed successfully",
  "refinement_changes": "Moving to next step"
}
```

### delegate_task

Delegates a step to a specialized agent.

```json
{
  "step_id": "step1",
  "agent_type": "CodeActAgent",
  "task": "Analyze the codebase to find the backend framework",
  "inputs": {}
}
```

### view_plan

Shows current plan status.

### finish

Marks the task as complete.

```json
{
  "summary": "Successfully added authentication with JWT tokens",
  "outputs": {
    "files_modified": ["auth.js", "routes.js"],
    "tests_passing": true
  }
}
```

## Examples

### Example 1: Code Refactoring Task

```
User: "Refactor the authentication module to use async/await"

PlannerAgent creates plan:
1. Analyze current auth code (CodeActAgent)
2. Identify callback patterns (CodeActAgent)
3. Convert to async/await (CodeActAgent)
4. Update tests (CodeActAgent)
5. Run tests and verify (CodeActAgent)

Executes each step, refines if issues arise, completes task.
```

### Example 2: Feature Implementation

```
User: "Add a dashboard with user analytics"

PlannerAgent creates plan:
1. Research dashboard libraries (BrowsingAgent)
2. Design data model for analytics (CodeActAgent)
3. Implement backend analytics endpoints (CodeActAgent)
4. Implement frontend dashboard (CodeActAgent)
5. Add visualizations (CodeActAgent)
6. Write tests (CodeActAgent)
7. Deploy and verify (CodeActAgent)

Executes steps, adapts if complications arise.
```

### Example 3: Bug Investigation

```
User: "Fix the login timeout issue"

PlannerAgent creates plan:
1. Reproduce the issue (CodeActAgent)
2. Analyze logs and code (CodeActAgent)
3. Research timeout patterns (BrowsingAgent)
4. Implement fix (CodeActAgent)
5. Test fix (CodeActAgent)
6. Verify no regressions (CodeActAgent)

Refines plan based on findings during investigation.
```

## Plan Data Structures

### PlanStep

```python
@dataclass
class PlanStep:
    id: str                    # Unique identifier
    description: str           # What this step does
    agent_type: str           # Which agent to use
    inputs: dict              # Input parameters
    status: StepStatus        # pending/in_progress/completed/failed
    result: str | None        # Result from execution
    error: str | None         # Error if failed
    dependencies: list[str]   # Prerequisites
```

### ExecutionPlan

```python
@dataclass
class ExecutionPlan:
    goal: str                 # Overall objective
    steps: list[PlanStep]     # All plan steps
    context: dict             # Additional context
    iteration: int            # Refinement count
    refinements: list[Refinement]  # History of changes
```

## Feedback Loop

The PlannerAgent implements a sophisticated feedback loop:

1. **Delegation**: Agent delegates step to specialized agent
2. **Execution**: Specialized agent executes and returns observation
3. **Analysis**: PlannerAgent analyzes the result
4. **Decision**: Based on result:
   - ✅ Success → Mark complete, move to next step
   - ❌ Failure → Analyze error, refine plan, retry or adapt
   - 🔄 Partial → Update plan with new information
5. **Refinement**: Add/modify steps based on learnings
6. **Iteration**: Continue until goal achieved

## Best Practices

### For Planning
- Start with high-level steps, refine as you learn
- Be specific about what each step should accomplish
- Consider dependencies carefully
- Plan for verification and testing

### For Delegation
- Choose the agent that best matches the task
- Provide clear, actionable descriptions
- Include relevant context
- Specify success criteria

### For Refinement
- Update the plan as soon as you learn new information
- Add steps when needed, don't try to force the original plan
- Document why you're refining (refinement_reason)
- Keep the overall goal in focus

## Comparison with CodeActAgent

| Aspect | CodeActAgent | PlannerAgent |
|--------|--------------|--------------|
| **Purpose** | Execute tasks directly | Orchestrate through planning |
| **Approach** | Linear execution | Hierarchical decomposition |
| **Complexity** | Simple to moderate tasks | Complex multi-step tasks |
| **Agents** | Single agent | Coordinates multiple agents |
| **Planning** | Implicit | Explicit and visible |
| **Adaptation** | Limited | Dynamic plan refinement |
| **Best For** | Direct implementation | Strategic coordination |

## Advanced Features

### Dependency Management

Steps can depend on other steps:

```python
PlanStep(
    id="step3",
    description="Deploy to production",
    dependencies=["step1", "step2"],  # Must complete first
    # ...
)
```

The PlannerAgent ensures dependencies are satisfied before execution.

### Iterative Refinement

Plans are refined based on feedback:

```python
# Original plan: 3 steps
# After step 1: Discovered new requirement
# → Add 2 more steps
# After step 3: Tests failed
# → Add debugging step
# Final plan: 6 steps
```

### Context Propagation

Context from earlier steps is available to later steps:

```python
ExecutionPlan(
    context={
        "framework": "Express.js",  # From step 1
        "database": "MongoDB",       # From step 1
        "auth_pattern": "JWT"        # From step 2
    }
)
```

## Debugging

### View Current Plan

The agent's current plan is available:

```python
if planner.current_plan:
    print(planner.current_plan.get_summary())
    # Shows: progress, status of each step, refinements
```

### Plan Visualization

Plans can be visualized in the UI (if implemented):
- Tree view of steps with dependencies
- Progress indicators
- Result summaries

### Logging

The PlannerAgent logs extensively:

```python
logger.info(f'Created plan with {len(steps)} steps')
logger.info(f'Delegating step {step_id} to {agent_type}')
logger.info(f'Updated plan - Step {step_id} status: {new_status}')
```

## Limitations & Future Work

### Current Limitations
- Sequential execution (no parallel step execution yet)
- No plan visualization in UI (coming soon)
- Limited error recovery strategies
- No plan templates for common tasks

### Planned Enhancements
- **Parallel Execution**: Execute independent steps concurrently
- **Plan Templates**: Reusable plans for common tasks
- **Learning**: Improve plans based on historical success
- **User Interaction**: Allow users to approve/modify plans before execution
- **Recovery Strategies**: More sophisticated error handling
- **Plan Visualization**: Interactive plan viewer in UI

## Contributing

To contribute to PlannerAgent:

1. **Add new tools**: Add to `tools/plan_tools.py`
2. **Improve prompts**: Edit `prompts/system_prompt.jinja2`
3. **Enhance planning logic**: Modify `planner_agent.py`
4. **Add tests**: Create tests in `tests/`

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/OpenHands/OpenHands/issues
- Documentation: https://docs.openhands.ai

## License

Same as OpenHands main repository.
