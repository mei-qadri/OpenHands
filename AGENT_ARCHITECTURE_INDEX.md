# OpenHands Agent Architecture - Complete Documentation Index

This index provides comprehensive documentation for understanding and building agents in OpenHands, with specific focus on creating a PlannerAgent scaffold.

## Documentation Files

### 1. PLANNER_AGENT_ARCHITECTURE.md (842 lines)
**Comprehensive technical guide to the entire OpenHands agent architecture**

Contents:
- Executive summary of core components
- Agent base classes and 6 current implementations
- Runtime and controller system (1391-line AgentController)
- Event-driven architecture details
- State management and multi-agent patterns
- Tools and function calling system
- Memory and condensation mechanisms
- Configuration patterns
- Complete execution flow diagrams
- Design patterns and key concepts

**Best For**: Understanding the full system, deep dives, reference documentation

### 2. PLANNER_AGENT_GUIDE.md (300+ lines)
**Focused implementation guide for building a PlannerAgent**

Contents:
- PlannerAgent overview and key concepts
- Inheritance strategy options
- Core components to implement (planning, delegation, tracking)
- Step loop implementation
- Response parsing for planning actions
- System prompt strategy with examples
- Directory structure template
- Agent registration pattern
- Delegation pattern details
- State flow diagrams
- Special considerations (budget, memory, errors)
- Testing strategy
- Common pitfalls and troubleshooting

**Best For**: Building PlannerAgent, practical implementation, code examples

---

## Quick Navigation

### By Topic

**Agent Architecture**
- Base class definition: PLANNER_AGENT_ARCHITECTURE.md - Section 1
- Implementations: PLANNER_AGENT_ARCHITECTURE.md - Section 1.2
- Registration pattern: PLANNER_AGENT_ARCHITECTURE.md - Section 1.3

**Execution System**
- AgentController loop: PLANNER_AGENT_ARCHITECTURE.md - Section 2.1
- Runtime system: PLANNER_AGENT_ARCHITECTURE.md - Section 2.2
- State management: PLANNER_AGENT_ARCHITECTURE.md - Section 2.3

**Communication**
- Event-driven arch: PLANNER_AGENT_ARCHITECTURE.md - Section 3.1
- Action-observation cycle: PLANNER_AGENT_ARCHITECTURE.md - Section 3.2
- Message construction: PLANNER_AGENT_ARCHITECTURE.md - Section 3.3

**Multi-Agent Patterns**
- Delegation system: PLANNER_AGENT_ARCHITECTURE.md - Section 6.1
- State sharing: PLANNER_AGENT_ARCHITECTURE.md - Section 6.2
- Terminology: PLANNER_AGENT_ARCHITECTURE.md - Section 6.3

**Implementation Guide**
- Inheritance: PLANNER_AGENT_GUIDE.md - Section 1
- Core components: PLANNER_AGENT_GUIDE.md - Section 2
- Step loop: PLANNER_AGENT_GUIDE.md - Section 3
- Response parsing: PLANNER_AGENT_GUIDE.md - Section 4
- System prompt: PLANNER_AGENT_GUIDE.md - Section 5
- Configuration: PLANNER_AGENT_GUIDE.md - Section 6

---

## Key Architecture Concepts

### 1. Agent
- **What**: Autonomous unit that processes tasks using LLM reasoning + tools
- **Interface**: Must implement `step(state: State) -> Action`
- **Registry**: Agents registered by name for runtime loading
- **Location**: `/openhands/controller/agent.py`

### 2. AgentController
- **What**: Orchestrates agent execution, manages state, handles events
- **Key Method**: `_step()` - calls `agent.step()` and manages action execution
- **Key Method**: `on_event()` - handles incoming events from event stream
- **Supports**: Delegation, security analysis, confirmation, stuck detection
- **Location**: `/openhands/controller/agent_controller.py` (1391 lines)

### 3. EventStream
- **What**: Central pub-sub event bus for all system communication
- **Usage**: Actions and observations added here
- **Subscribers**: AGENT_CONTROLLER, RUNTIME, SERVER, MEMORY, etc.
- **Pattern**: Add event → Subscribers notified → Callbacks triggered
- **Location**: `/openhands/events/stream.py`

### 4. State
- **What**: Execution state with history, metrics, control flags
- **Shared**: In multi-agent scenarios, iteration_flag and budget_flag shared
- **Hierarchy**: Each delegate gets new State with incremented delegate_level
- **Persistence**: Saved after each step for session recovery
- **Location**: `/openhands/controller/state/state.py`

### 5. Runtime
- **What**: Sandboxed execution environment (Docker, Kubernetes, Local, etc.)
- **Role**: Executes CmdRunAction, FileEditAction, BrowseAction, etc.
- **Returns**: Observations (CmdOutputObservation, FileReadObservation, etc.)
- **Location**: `/openhands/runtime/base.py`

### 6. Tools
- **What**: LLM function definitions (OpenAI compatible format)
- **Usage**: Agent gets list of tools, LLM can call them
- **Parsing**: Tool calls converted to Actions via `response_to_actions()`
- **Types**: Bash, Python, file ops, browser, planning, delegation, etc.
- **Location**: `/openhands/agenthub/*/tools/`

### 7. Delegation
- **Pattern**: Agent returns `AgentDelegateAction(agent_type, inputs)`
- **Effect**: Controller creates new AgentController with new agent
- **Sharing**: Shared iteration_flag, budget_flag, metrics
- **Result**: Returns `AgentDelegateObservation` with subtask result
- **Nesting**: Delegates can spawn further delegates (multi-level)

### 8. Message Flow
- **Input**: `User → MessageAction → EventStream`
- **Processing**: `Controller.on_event() → agent.step(state) → Action`
- **Execution**: `Runtime processes Action → Observation`
- **Output**: `Observation → EventStream → UI`
- **Loop**: Repeats until AgentFinishAction

---

## PlannerAgent Specific Architecture

### What Makes PlannerAgent Different

1. **Primary Responsibility**: Orchestration, not execution
2. **Tool Set**: Plan creation, delegation, progress tracking, not bash/file ops
3. **LLM Interaction**: Fewer calls, more strategic
4. **State Management**: Plan-based (track subtasks) vs linear (CodeActAgent)
5. **Delegation**: Heavy usage to delegate actual work to specialists

### Core Flow

```
User Request
    ↓
PlannerAgent.step()
    ↓
├─ If no plan: LLM creates plan, returns CreatePlanAction
├─ If plan exists: LLM picks next subtask, returns AgentDelegateAction
│   ↓
│   (Controller spawns delegate, they execute)
│   ↓
│   PlannerAgent resumes with AgentDelegateObservation
│   ↓
│   Update plan progress
│   ↓
│   Return next AgentDelegateAction
│   
└─ When all subtasks done: Return AgentFinishAction with results
```

### Key Implementation Points

1. **Inheritance**: `class PlannerAgent(Agent):`
2. **Tools**: Custom tools for planning and delegation
3. **Prompt**: Teaches LLM about planning, available agents, decision rules
4. **step()**: Manages plan state, delegates work, tracks progress
5. **response_to_actions()**: Converts planning decisions to actions

---

## Current Agent Types Reference

| Agent | Inherits From | Purpose | Best For |
|-------|---------------|---------|----------|
| **CodeActAgent** | Agent | General code execution | Most tasks |
| **LocAgent** | CodeActAgent | Lines-of-code analysis | Code metrics |
| **ReadOnlyAgent** | CodeActAgent | Safe exploration | Reading only |
| **BrowsingAgent** | Agent | Web navigation | Web research |
| **VisualBrowsingAgent** | Agent | Vision-based browsing | Visual tasks |
| **DummyAgent** | Agent | Deterministic testing | Testing |
| **PlannerAgent** (new) | Agent | Task orchestration | Complex workflows |

---

## File Reference Guide

### Core Architecture Files
- `/openhands/controller/agent.py` - Agent base class (184 lines)
- `/openhands/controller/agent_controller.py` - Execution orchestrator (1391 lines)
- `/openhands/controller/state/state.py` - State definition (200+ lines)
- `/openhands/events/stream.py` - Event bus (400+ lines)
- `/openhands/runtime/base.py` - Runtime base (1000+ lines)

### Agent Examples
- `/openhands/agenthub/codeact_agent/` - Full implementation example (300+ lines)
- `/openhands/agenthub/browsing_agent/` - Specialized agent example
- `/openhands/agenthub/readonly_agent/` - Constrained agent example

### Tools & Response Parsing
- `/openhands/agenthub/codeact_agent/tools/` - Tool implementations
- `/openhands/agenthub/codeact_agent/function_calling.py` - Response parsing
- `/openhands/events/action/` - Action definitions

### Configuration & Memory
- `/openhands/core/config/agent_config.py` - Agent configuration (150+ lines)
- `/openhands/memory/conversation_memory.py` - Event-to-message conversion
- `/openhands/memory/condenser/` - History condensation

### Server/Session
- `/openhands/server/session/agent_session.py` - Session management
- `/openhands/server/conversation_manager/` - Task management

---

## Implementation Roadmap

### Phase 1: Understand (Reading)
1. Read PLANNER_AGENT_ARCHITECTURE.md sections 1-3
2. Study CodeActAgent implementation
3. Understand State and EventStream

### Phase 2: Design
1. Define PlannerAgent's tools
2. Plan system prompt content
3. Design plan representation (data structure)
4. Map delegation strategy

### Phase 3: Implement (Reference PLANNER_AGENT_GUIDE.md)
1. Create agent class, inherit from Agent
2. Define tools in tools/ subdirectory
3. Write system_prompt.j2
4. Implement step() method
5. Implement response_to_actions()
6. Register agent in __init__.py

### Phase 4: Test
1. Unit tests for plan creation
2. Integration tests with mock delegates
3. E2E tests with real agents
4. Delegation chain tests

### Phase 5: Integrate
1. Add configuration section
2. Enable in web UI
3. Test with real user workflows
4. Optimize prompts based on results

---

## Common Questions

**Q: Should PlannerAgent inherit from CodeActAgent?**
A: Not necessarily. Direct inheritance from Agent is cleaner since PlannerAgent's tools are very different. Could inherit if you need CodeActAgent's capabilities as fallback.

**Q: How does PlannerAgent track plan progress?**
A: Store plan in agent memory (pending_actions queue), update based on AgentDelegateObservation results in state.history.

**Q: Can delegates spawn further delegates?**
A: Yes! CodeActAgent delegates could spawn BrowsingAgent, which could spawn something else. No depth limit (but budget_flag applies across all).

**Q: How are shared metrics handled?**
A: iteration_flag and budget_flag are passed as references to delegates. Both parent and delegates see same totals. Useful for fairness across all agents.

**Q: What if a subtask fails?**
A: AgentDelegateObservation contains agent_state (FINISHED, ERROR, REJECTED, etc.). PlannerAgent can detect failure and retry, reassign, or report to user.

**Q: Can PlannerAgent modify plan mid-execution?**
A: Yes! If a delegate returns unexpected result, PlannerAgent can create revised plan in next step().

---

## Key Takeaways

1. **OpenHands is event-driven**: Central EventStream, subscribers react to events
2. **Step loop is core**: `agent.step(state)` called repeatedly, returns Action
3. **State is shared**: In delegation, parent and child share metrics/budget
4. **Actions drive everything**: Agent returns Action → Controller adds to stream → Runtime executes → Observation returned
5. **Delegation is powerful**: Enables multi-agent workflows with minimal coordination logic
6. **Tools are flexible**: Define any tool as OpenAI-compatible function definition

---

## Support Resources

For specific code examples, see:
- PLANNER_AGENT_GUIDE.md - Practical code templates
- CodeActAgent implementation - Real working example
- This document - Architecture overview

For system deep-dive, see:
- PLANNER_AGENT_ARCHITECTURE.md - Complete technical guide
- Source code comments in referenced files
- test/ directory for usage examples

---

Generated: 2025-11-17
OpenHands Version: Latest (as of exploration date)
