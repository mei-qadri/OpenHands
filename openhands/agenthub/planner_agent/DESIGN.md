# PlannerAgent Design Document

## Overview

The PlannerAgent is a meta-agent that orchestrates complex tasks by:
1. Analyzing user queries and repository/data context
2. Creating structured execution plans
3. Spawning specialized sub-agents to execute plan steps
4. Collecting feedback and observations from sub-agents
5. Refining plans based on feedback
6. Iterating until the task is complete

## Architecture

### Core Components

#### 1. PlannerAgent Class
- **Inherits from**: `Agent` base class
- **Responsibilities**:
  - Initialize with LLM and configuration
  - Manage plan state
  - Execute planning loop
  - Delegate to sub-agents
  - Process feedback

#### 2. Plan Data Structure
```python
@dataclass
class PlanStep:
    id: str
    description: str
    agent_type: str  # e.g., 'CodeActAgent', 'BrowsingAgent'
    inputs: dict
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    result: str | None
    dependencies: list[str]  # IDs of steps that must complete first

@dataclass
class ExecutionPlan:
    goal: str
    steps: list[PlanStep]
    context: dict  # Repository analysis, file summaries, etc.
    iteration: int
    refinements: list[str]  # History of plan changes
```

#### 3. Tools

**PlanCreationTool**
- Creates initial execution plan
- Analyzes repository structure
- Identifies required agents and steps

**PlanUpdateTool**
- Refines plan based on feedback
- Marks steps as complete/failed
- Adds new steps if needed
- Re-prioritizes steps

**DelegateTool** (wrapper around AgentDelegateAction)
- Spawns sub-agent for a plan step
- Packages inputs for sub-agent
- Tracks delegation

**FinishTool**
- Marks planning complete
- Returns final results

### Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Analyze Query & Repository                         │
│  - Parse user intent                                         │
│  - Scan repository structure                                 │
│  - Identify relevant files/modules                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Create Initial Plan                                │
│  - Break down task into steps                               │
│  - Assign agent types to steps                              │
│  - Identify dependencies                                     │
│  - Estimate complexity                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Execute Plan (Loop)                                │
│  ┌────────────────────────────────────────────────┐         │
│  │  3a. Select next step (respect dependencies)   │         │
│  │      ↓                                          │         │
│  │  3b. Delegate to appropriate agent             │         │
│  │      ↓                                          │         │
│  │  3c. Collect observation/result                │         │
│  │      ↓                                          │         │
│  │  3d. Update plan with feedback                 │         │
│  │      ↓                                          │         │
│  │  3e. Refine if needed (add/modify steps)       │         │
│  │      ↓                                          │         │
│  │  3f. Check if plan complete                    │         │
│  │      ↓                                          │         │
│  │  If not complete: goto 3a                      │         │
│  └────────────────────────────────────────────────┘         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Return Results                                     │
│  - Aggregate all step results                               │
│  - Provide summary                                           │
│  - Report success/failure                                    │
└─────────────────────────────────────────────────────────────┘
```

### State Management

The PlannerAgent maintains state through:

1. **Plan Object**: Current plan with all steps and their status
2. **Execution History**: Track of all delegations and results
3. **Context**: Repository analysis, file summaries, etc.
4. **Iteration Counter**: Number of plan refinements

### Feedback Loop

```
┌──────────────────┐
│   Plan Step      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ AgentDelegate    │───┐
│ Action           │   │
└────────┬─────────┘   │
         │             │
         ▼             │
┌──────────────────┐   │
│  Sub-Agent       │   │
│  Executes        │   │
└────────┬─────────┘   │
         │             │
         ▼             │
┌──────────────────┐   │
│  Observation     │◄──┘
│  (Result)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  PlannerAgent    │
│  Processes       │
│  Feedback        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Update Plan     │
│  - Mark complete │
│  - Add steps?    │
│  - Modify steps? │
└────────┬─────────┘
         │
         ▼
    Next Step
```

## System Prompt Design

The system prompt should:

1. **Define Role**: "You are a PlannerAgent that orchestrates complex tasks"
2. **List Available Agents**: CodeActAgent, BrowsingAgent, etc. with capabilities
3. **Explain Planning Process**: How to break down tasks
4. **Tool Usage**: When to use each tool
5. **Feedback Processing**: How to interpret observations
6. **Decision Making**: When to refine plans, when to finish

## Tool Schemas

### create_plan Tool
```json
{
  "type": "function",
  "function": {
    "name": "create_plan",
    "description": "Create an execution plan for the given task",
    "parameters": {
      "type": "object",
      "properties": {
        "goal": {
          "type": "string",
          "description": "The overall goal of the plan"
        },
        "steps": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "description": "string",
              "agent_type": "string",
              "inputs": "object",
              "dependencies": "array"
            }
          }
        },
        "context": {
          "type": "object",
          "description": "Context from repository analysis"
        }
      }
    }
  }
}
```

### update_plan Tool
```json
{
  "type": "function",
  "function": {
    "name": "update_plan",
    "description": "Update the execution plan based on feedback",
    "parameters": {
      "type": "object",
      "properties": {
        "step_id": {
          "type": "string",
          "description": "ID of the step to update"
        },
        "status": {
          "type": "string",
          "enum": ["completed", "failed", "blocked"]
        },
        "result": {
          "type": "string",
          "description": "Result or error message"
        },
        "new_steps": {
          "type": "array",
          "description": "Additional steps to add"
        },
        "refinement_note": {
          "type": "string",
          "description": "Why this refinement was made"
        }
      }
    }
  }
}
```

### delegate_task Tool
```json
{
  "type": "function",
  "function": {
    "name": "delegate_task",
    "description": "Delegate a task to a specialized agent",
    "parameters": {
      "type": "object",
      "properties": {
        "step_id": {
          "type": "string",
          "description": "The plan step ID this delegates"
        },
        "agent_type": {
          "type": "string",
          "enum": ["CodeActAgent", "BrowsingAgent", "VisualBrowsingAgent"]
        },
        "task": {
          "type": "string",
          "description": "Task description for the agent"
        },
        "inputs": {
          "type": "object",
          "description": "Inputs for the agent"
        }
      }
    }
  }
}
```

## Implementation Strategy

### Phase 1: Core Infrastructure
- [ ] Create PlannerAgent class skeleton
- [ ] Implement Plan data structures
- [ ] Create basic step() method
- [ ] Add agent registration

### Phase 2: Planning Tools
- [ ] Implement create_plan tool
- [ ] Implement update_plan tool
- [ ] Implement delegate_task tool (wraps AgentDelegateAction)
- [ ] Implement finish tool

### Phase 3: System Prompt
- [ ] Write system prompt template
- [ ] Add available agents documentation
- [ ] Add planning examples
- [ ] Add feedback processing examples

### Phase 4: Feedback Loop
- [ ] Parse observations from sub-agents
- [ ] Extract success/failure signals
- [ ] Update plan state
- [ ] Decide on refinements

### Phase 5: Testing & Integration
- [ ] Unit tests for tools
- [ ] Integration test with mock agents
- [ ] End-to-end test with real agents
- [ ] Documentation and examples

## Example Usage

```python
# User provides a query
query = "Add user authentication to my web app"

# PlannerAgent analyzes and creates plan:
# Step 1: Analyze existing codebase (CodeActAgent)
# Step 2: Research authentication patterns (BrowsingAgent)
# Step 3: Implement backend auth (CodeActAgent)
# Step 4: Implement frontend auth (CodeActAgent)
# Step 5: Write tests (CodeActAgent)

# Executes each step, collects results, refines plan as needed
```

## Benefits

1. **Hierarchical Task Decomposition**: Break complex tasks into manageable steps
2. **Specialized Agent Utilization**: Use the right agent for each sub-task
3. **Adaptive Planning**: Refine plans based on actual execution results
4. **Better Context Management**: Each sub-agent focuses on specific sub-task
5. **Explicit Reasoning**: Plans are visible and can be debugged
6. **Parallel Execution**: Independent steps can be executed concurrently (future)

## Future Enhancements

1. **Parallel Execution**: Execute independent steps concurrently
2. **Plan Visualization**: UI to show plan progress
3. **Plan Templates**: Reusable plans for common tasks
4. **Learning**: Improve plans based on historical success
5. **User Interaction**: Allow users to approve/modify plans
6. **Recovery Strategies**: Handle failures more gracefully
