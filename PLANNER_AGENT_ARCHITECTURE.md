# OpenHands Agent Architecture Guide

## Executive Summary

OpenHands is a sophisticated multi-agent system with a hierarchical architecture. The core components work together to:
1. **Agents** - Autonomous units that execute tasks using LLM reasoning and tools
2. **AgentController** - Orchestrates agent execution, state management, and delegation
3. **Runtime** - Provides sandboxed environment for safe task execution
4. **EventStream** - Central event-driven communication hub
5. **State** - Maintains conversation history, metrics, and multi-agent context

The system supports both single-agent and multi-agent workflows through a delegation pattern.

---

## 1. AGENT BASE CLASSES AND ARCHITECTURE

### 1.1 Agent Base Class
**Location**: `/home/user/OpenHands/openhands/controller/agent.py`

```
Agent (Abstract Base Class)
├── Abstract Methods:
│   └── step(state: State) -> Action
│
├── Core Properties:
│   ├── name: str (from class name)
│   ├── config: AgentConfig
│   ├── llm: LLM instance
│   ├── llm_registry: LLMRegistry
│   ├── tools: list[ChatCompletionToolParam]
│   ├── mcp_tools: dict[str, ChatCompletionToolParam]
│   └── complete: bool
│
├── Class Registry:
│   ├── _registry: dict[str, type[Agent]]
│   ├── register(name, agent_cls) -> None
│   ├── get_cls(name) -> type[Agent]
│   └── list_agents() -> list[str]
│
├── Key Methods:
│   ├── __init__(config, llm_registry)
│   ├── step(state) -> Action (Abstract)
│   ├── reset() -> None
│   ├── get_system_message() -> SystemMessageAction | None
│   ├── set_mcp_tools(mcp_tools) -> None
│   └── response_to_actions(response) -> list[Action] (optional override)
│
└── Sandbox Plugins:
    └── sandbox_plugins: list[PluginRequirement]
```

### 1.2 Agent Implementations

**CodeActAgent** (Base implementation)
- Path: `/home/user/OpenHands/openhands/agenthub/codeact_agent/codeact_agent.py`
- VERSION: '2.2'
- Key Features:
  - Unified code action space (bash, Python, browser)
  - Conversation memory with event condensation
  - Tool-based function calling
  - Support for multiple model types
  - LLM-based or ACI-based file editing

**LocAgent** (Lines of Code specialized)
- Path: `/home/user/OpenHands/openhands/agenthub/loc_agent/loc_agent.py`
- Inherits from: CodeActAgent
- Customization: Uses loc_agent-specific function calling and tools

**ReadOnlyAgent** (Safety-focused)
- Path: `/home/user/OpenHands/openhands/agenthub/readonly_agent/readonly_agent.py`
- Inherits from: CodeActAgent
- Limitations: Only read-only tools (grep, glob, view, think, finish, web_read)
- Use Case: Safe codebase exploration without modifications

**BrowsingAgent** (Web-focused)
- Path: `/home/user/OpenHands/openhands/agenthub/browsing_agent/browsing_agent.py`
- Inherits from: Agent (direct)
- Key Features:
  - Uses BrowserGym for web interaction
  - High-level action space for web navigation
  - Accessibility tree-based page understanding

**VisualBrowsingAgent** (Vision-enabled)
- Path: `/home/user/OpenHands/openhands/agenthub/visualbrowsing_agent/visualbrowsing_agent.py`
- Vision-based web browsing

**DummyAgent** (Testing)
- Path: `/home/user/OpenHands/openhands/agenthub/dummy_agent/agent.py`
- Deterministic action sequences for e2e testing

### 1.3 Agent Registration Pattern

```python
# In agent __init__.py files:
from openhands.agenthub.codeact_agent.codeact_agent import CodeActAgent
from openhands.controller.agent import Agent

Agent.register('CodeActAgent', CodeActAgent)
```

---

## 2. RUNTIME AND CONTROLLER SYSTEM

### 2.1 AgentController - Main Orchestrator
**Location**: `/home/user/OpenHands/openhands/controller/agent_controller.py` (1391 lines)

**Responsibilities**:
- Manage agent execution loop
- Handle event stream subscriptions
- Manage state and state transitions
- Control flow (iterations, budget limits)
- Delegate management (multi-agent support)
- Security analysis and confirmation handling

**Key Attributes**:
```
AgentController
├── id: str (session ID)
├── agent: Agent (the controlled agent)
├── event_stream: EventStream
├── state: State (shared execution state)
├── state_tracker: StateTracker
├── confirmation_mode: bool
├── parent: AgentController | None (for delegates)
├── delegate: AgentController | None (current child agent)
├── _stuck_detector: StuckDetector
├── _replay_manager: ReplayManager
└── security_analyzer: SecurityAnalyzer | None
```

**Core Loop**:
1. `step()` → Creates async task → `_step_with_exception_handling()`
2. `_step_with_exception_handling()` → Catches exceptions → `_step()`
3. `_step()` → Core execution:
   - Check state validity
   - Run control flags (iteration/budget limits)
   - Call `agent.step(state)` to get Action
   - Handle security analysis
   - Add action to event stream
4. `on_event()` → Handles incoming events:
   - Routes to delegate if active
   - Calls `_on_event()` if not
   - Determines if agent should step

**Execution Flow**:
```
User Message (MessageAction)
    ↓
event_stream.add_event()
    ↓
controller.on_event() [callback]
    ↓
should_step() check
    ↓
_step()
    ↓
agent.step(state) → Action
    ↓
security analysis
    ↓
event_stream.add_event(action)
    ↓
Runtime executes action → Observation
    ↓
event_stream.add_event(observation)
    ↓
controller.on_event() [callback]
    ↓
Repeat or finish
```

### 2.2 Runtime Base Class
**Location**: `/home/user/OpenHands/openhands/runtime/base.py`

**Purpose**: Provides sandboxed execution environment

**Key Implementations**:
- DockerRuntime: Container-based execution
- RemoteRuntime: Remote machine execution
- LocalRuntime: Local development
- KubernetesRuntime: Kubernetes-based
- CLIRuntime: Command-line interface

**Runtime Capabilities**:
- Bash shell access
- Browser interaction
- File system operations
- Git operations
- Environment variable management
- MCP (Model Context Protocol) integration
- Security analysis hooks

### 2.3 State Management
**Location**: `/home/user/OpenHands/openhands/controller/state/state.py`

**State Class**:
```
State
├── Identification:
│   ├── session_id: str
│   ├── user_id: str | None
│   └── delegate_level: int (0 = root, increases for sub-agents)
│
├── Control:
│   ├── agent_state: AgentState (LOADING, RUNNING, PAUSED, FINISHED, ERROR, etc.)
│   ├── iteration_flag: IterationControlFlag (shared across agents)
│   ├── budget_flag: BudgetControlFlag (shared, USD-based)
│   ├── confirmation_mode: bool
│   └── last_error: str
│
├── History & Events:
│   ├── history: list[Event]
│   ├── start_id: int (first event in this subtask)
│   ├── end_id: int (last event in this subtask)
│   └── view: list[Event] (filtered view for LLM context)
│
├── Metrics:
│   ├── metrics: Metrics (shared global metrics)
│   ├── parent_metrics_snapshot: dict (parent's metrics at delegation time)
│   └── parent_iteration: int
│
└── Data:
    ├── inputs: dict (initial task inputs)
    ├── outputs: dict (final task outputs)
    └── conversation_stats: ConversationStats
```

**Key State Methods**:
- `get_agent_state()` - Current execution state
- `get_local_step()` - Iteration count for current subtask
- `to_llm_metadata()` - Metadata for LLM
- Save/restore for session persistence

---

## 3. AGENT COMMUNICATION AND STATE HANDLING

### 3.1 Event-Driven Architecture
**Location**: `/home/user/OpenHands/openhands/events/stream.py`

**EventStream Pattern**:
- Central event bus for all system communication
- Thread-safe queue-based processing
- Multiple subscriber types (AGENT_CONTROLLER, RUNTIME, SERVER, etc.)
- Persistent event storage

**Event Subscribers**:
```
EventStreamSubscriber
├── AGENT_CONTROLLER (listens for all events, triggers agent steps)
├── RUNTIME (listens for actions, executes them)
├── SERVER (sends events to UI)
├── MEMORY (updates conversation memory)
├── RESOLVER (handles special events)
└── TEST (for testing)
```

**Event Subscription**:
```python
# Controller subscribes to event stream
event_stream.subscribe(
    EventStreamSubscriber.AGENT_CONTROLLER, 
    controller.on_event, 
    controller.id
)

# When events occur:
event_stream.add_event(action, EventSource.AGENT)
# Triggers: controller.on_event(action) callback
```

### 3.2 Action-Observation Cycle
**Location**: `/home/user/OpenHands/openhands/events/action/` and `observation/`

**Action Flow**:
```
Agent.step(state)
    ↓
returns Action:
├── CmdRunAction(command)
├── IPythonRunCellAction(code)
├── FileReadAction(path)
├── FileWriteAction(path, content)
├── FileEditAction(path, edits)
├── BrowseURLAction(url) / BrowseInteractiveAction(actions)
├── MessageAction(content)
├── AgentFinishAction(outputs)
├── AgentDelegateAction(agent, inputs)
├── AgentThinkAction(thought)
└── ... (20+ action types)
    ↓
added to EventStream
    ↓
Runtime executes action
    ↓
returns Observation:
├── CmdOutputObservation(output, exit_code)
├── FileReadObservation(content)
├── FileWriteObservation(success)
├── BrowserOutputObservation(content)
├── ErrorObservation(error)
├── NullObservation() (for completed actions)
└── ... (10+ observation types)
    ↓
added to EventStream
    ↓
Agent sees observation in state.history
    ↓
Next agent.step() uses observation
```

### 3.3 Message Construction for LLM
**Location**: `/home/user/OpenHands/openhands/agenthub/codeact_agent/codeact_agent.py`

**Process**:
1. `_get_messages(events, initial_user_message)` → list[Message]
2. ConversationMemory processes events
3. Converts Actions/Observations to Messages
4. Handles role alternation (user/assistant/tool)
5. Applies prompt caching (Anthropic)
6. Adds system message if missing

---

## 4. CURRENT AGENT TYPES AND RESPONSIBILITIES

| Agent | Purpose | Inheritance | Tools | Use Case |
|-------|---------|-------------|-------|----------|
| **CodeActAgent** | General-purpose code execution | Agent | bash, Python, file edit, browser, think, finish | Default for most tasks |
| **LocAgent** | Lines-of-code focused tasks | CodeActAgent | loc-specific tools | Code metrics, analysis |
| **ReadOnlyAgent** | Safe codebase exploration | CodeActAgent | grep, glob, view, think, finish | Reading without changes |
| **BrowsingAgent** | Web navigation & information retrieval | Agent | web browsing, high-level navigation | Web tasks |
| **VisualBrowsingAgent** | Vision-based web interaction | Agent | visual page analysis, clicking | Visual web tasks |
| **DummyAgent** | Deterministic test execution | Agent | predefined sequences | Testing |

---

## 5. HOW USER QUERIES ARE PROCESSED

### 5.1 Entry Point: User Message
**Location**: `/home/user/OpenHands/openhands/server/session/agent_session.py`

```
User Types Query in UI
    ↓
/message API endpoint (conversation.py)
    ↓
MessageAction created with source=USER
    ↓
event_stream.add_event(MessageAction, EventSource.USER)
    ↓
controller.on_event() callback triggered
    ↓
should_step() returns True (user message detected)
    ↓
controller._step() called
    ↓
state.history updated with user message
    ↓
agent.step(state) processes entire conversation history
```

### 5.2 Agent Processing
1. **Get Latest History**:
   - Retrieves all events from event_stream
   - Builds conversation view
   - Applies memory condensation if needed

2. **Prepare LLM Input**:
   - Format events as messages
   - Include system prompt (SystemMessageAction)
   - Add available tools (bash, editor, browser, etc.)
   - Apply token limits

3. **LLM Completion**:
   ```python
   response = self.llm.completion(
       messages=messages,
       tools=tools,
       extra_body={'metadata': state.to_llm_metadata(...)}
   )
   ```

4. **Parse Response**:
   - `response_to_actions(response)` converts tool calls to Actions
   - Handles multiple actions in single response
   - Validates tool names and arguments

5. **Return Action**:
   - Single action returned per agent.step()
   - Can be queued in pending_actions for multiple tool calls

---

## 6. MULTI-AGENT AND HIERARCHICAL PATTERNS

### 6.1 Agent Delegation System
**Location**: `/home/user/OpenHands/openhands/controller/agent_controller.py` (lines 742-803)

**Delegation Flow**:
```
Parent Agent
    ↓
agent.step() returns AgentDelegateAction(agent_name, inputs)
    ↓
controller._handle_action(AgentDelegateAction)
    ↓
controller.start_delegate(AgentDelegateAction)
    ↓
Creates new AgentController (is_delegate=True)
├── Creates new Agent instance of specified type
├── Creates new State with:
│   ├── delegate_level += 1
│   ├── Shared iteration_flag and budget_flag
│   ├── Shared global metrics
│   └── start_id pointing to current event
└── Sets parent/delegate relationship
    ↓
Delegate agent processes task
    ↓
Delegate returns AgentFinishAction or AgentRejectAction
    ↓
controller.end_delegate()
    ↓
Adds AgentDelegateObservation to stream
    ↓
Parent agent resumes and continues
```

### 6.2 Multi-Agent State Sharing
```
Root Agent (LEVEL 0)
├── iteration_flag (shared) - global iteration counter
├── budget_flag (shared) - shared token/cost budget
├── metrics (shared) - global task metrics
└── parent_metrics_snapshot - metrics when delegation started

Delegate Agent (LEVEL 1)
├── iteration_flag (same reference as parent)
├── budget_flag (same reference as parent)
├── metrics (same reference as parent)
├── parent_metrics_snapshot (captures parent state)
└── Can spawn own delegates (LEVEL 2+)
```

### 6.3 Terminology
- **Task**: Full conversation between OpenHands system and user
- **Subtask**: Conversation between one agent and user/other agents
- **Delegate Level**: 0 = root, 1+ = sub-agents
- **Global Iteration**: Counter shared across all agents
- **Local Iteration**: Counter within a subtask

---

## 7. TOOLS AND FUNCTION CALLING

### 7.1 Tool Structure
**Location**: `/home/user/OpenHands/openhands/agenthub/codeact_agent/tools/`

**Built-in Tools**:
```
bash.py              - CmdRunAction (bash command execution)
ipython.py           - IPythonRunCellAction (Python code)
browser.py           - BrowseInteractiveAction (web browsing)
str_replace_editor.py - FileEditAction (ACI-based editing)
llm_based_edit.py    - FileEditAction (LLM-based editing)
task_tracker.py      - TaskTrackingAction (planning & task management)
think.py             - AgentThinkAction (reasoning logging)
finish.py            - AgentFinishAction (task completion)
condensation_request.py - CondensationRequestAction (memory management)
```

### 7.2 Function Calling Implementation
**Location**: `/home/user/OpenHands/openhands/agenthub/codeact_agent/function_calling.py`

```python
def response_to_actions(response: ModelResponse, 
                        mcp_tool_names: list[str]) -> list[Action]:
    """Convert LLM response to Actions"""
    
    # For each tool_call in response.choices[0].message.tool_calls:
    #   1. Parse arguments as JSON
    #   2. Validate tool name exists
    #   3. Create appropriate Action type
    #   4. Set security_risk if provided
    #   5. Combine with thought from model
    #   6. Return list of Actions
```

### 7.3 Tool Definition Format (OpenAI compatible)
```python
ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Execute a bash command",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "..."},
                "timeout": {"type": "integer"},
                ...
            },
            "required": ["command"]
        }
    }
}
```

---

## 8. MEMORY AND CONDENSATION

### 8.1 Conversation Memory
**Location**: `/home/user/OpenHands/openhands/memory/conversation_memory.py`

**Purpose**: 
- Converts events to LLM messages
- Manages message role alternation
- Handles token limits
- Applies prompt caching

**Processing**:
```
raw_events (State.history)
    ↓
ConversationMemory.process_events()
    ↓
Convert Actions/Observations to Messages
    ↓
Ensure proper role sequence (user→assistant→tool→...)
    ↓
Truncate if needed
    ↓
Apply prompt caching markers
    ↓
list[Message] for LLM
```

### 8.2 History Condensation
**Location**: `/home/user/OpenHands/openhands/memory/condenser/`

**When Used**:
- LLM context window exceeded
- Explicitly requested via CondensationRequestAction
- Configured in agent config

**Types**:
- ConversationWindowCondenserConfig (default)
- NoOpCondenser (no condensation)

**Effect**:
- Summarizes old events
- Keeps recent events intact
- Reduces token count
- Maintains task context

---

## 9. CONFIGURATION AND INITIALIZATION

### 9.1 Agent Configuration
**Location**: `/home/user/OpenHands/openhands/core/config/agent_config.py`

```python
class AgentConfig(BaseModel):
    # Tool enabling
    enable_browsing: bool = True
    enable_llm_editor: bool = False
    enable_editor: bool = True
    enable_cmd: bool = True
    enable_think: bool = True
    enable_finish: bool = True
    enable_jupyter: bool = True
    enable_condensation_request: bool = False
    enable_plan_mode: bool = True
    
    # System prompt
    system_prompt_filename: str = 'system_prompt.j2'
    
    # Memory & context
    enable_history_truncation: bool = True
    condenser: CondenserConfig = ConversationWindowCondenserConfig()
    
    # Model routing
    model_routing: ModelRoutingConfig = ModelRoutingConfig()
    
    # Specialized
    enable_mcp: bool = True
    enable_som_visual_browsing: bool = True
    disabled_microagents: list[str] = []
```

### 9.2 Agent Initialization
```python
# In AgentSession.start():
agent = Agent.get_cls(agent_name)(
    config=agent_config,
    llm_registry=llm_registry
)

controller = AgentController(
    agent=agent,
    event_stream=event_stream,
    conversation_stats=conversation_stats,
    iteration_delta=max_iterations,
    budget_per_task_delta=max_budget,
    ...
)

controller.step()  # Start the loop
```

---

## 10. KEY DESIGN PATTERNS

### 10.1 Plugin System
Agents declare sandbox plugins needed:
```python
class CodeActAgent(Agent):
    sandbox_plugins = [
        AgentSkillsRequirement(),  # Python functions
        JupyterRequirement(),      # IPython support
    ]
```

### 10.2 MCP (Model Context Protocol) Integration
- Dynamic tool addition at runtime
- Tools can be registered from external servers
- `set_mcp_tools()` method on agents
- Validated against agent capabilities

### 10.3 Security Analysis
- Optional SecurityAnalyzer component
- Analyzes actions for risks (HIGH, LOW, UNKNOWN)
- Can require user confirmation
- Integrated into step() execution

### 10.4 State Tracker
- Persists state to disk (pickle + base64)
- Saves after each step
- Enables session recovery
- Tracks metrics and history

---

## 11. EXECUTION FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentSession Start                         │
│  (server/session/agent_session.py)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Create EventStream        │
        │  Create LLMRegistry        │
        │  Create AgentController    │
        └────────────────┬───────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  controller.step()                  │
        │  (async event loop created)        │
        └────────────────┬───────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────┐
    │        User sends message via UI              │
    │  event_stream.add_event(MessageAction)        │
    └────────────────────┬──────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────────┐
    │  controller.on_event() triggered                   │
    │  [AgentController is subscribed to event_stream]  │
    └────────────────────┬───────────────────────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   Check: should_step(event)?   │
         │   (is this a step-triggering  │
         │    event type?)                │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼────────────────────────────┐
         │   YES → _step_with_exception_handling()   │
         └───────────────┬────────────────────────────┘
                         │
         ┌───────────────▼───────────────────────┐
         │   Check agent state = RUNNING?        │
         │   Check no pending action?            │
         │   Check iteration/budget limits       │
         └───────────────┬───────────────────────┘
                         │
         ┌───────────────▼─────────────────────────────┐
         │   action = agent.step(state)                │
         │   [Agent processes history + LLM call]     │
         └───────────────┬─────────────────────────────┘
                         │
         ┌───────────────▼───────────────────┐
         │   Security analysis & confirmation │
         │   (if needed)                      │
         └───────────────┬───────────────────┘
                         │
         ┌───────────────▼──────────────────────────┐
         │   event_stream.add_event(action)         │
         │   [Add to event stream & storage]       │
         └───────────────┬──────────────────────────┘
                         │
         ┌───────────────▼────────────────────────────┐
         │   Runtime executes action                  │
         │   (bash, file ops, browser, etc.)          │
         │   Creates Observation                     │
         └───────────────┬────────────────────────────┘
                         │
         ┌───────────────▼──────────────────────┐
         │   event_stream.add_event(observation) │
         │   [Observation added to stream]       │
         └───────────────┬──────────────────────┘
                         │
         ┌───────────────▼──────────────────────┐
         │   controller.on_event() triggered   │
         │   (for observation)                  │
         │   [Loop back to should_step check]  │
         └───────────────┬──────────────────────┘
                         │
         ┌───────────────▼──────────────────────┐
         │   Continue cycling OR                │
         │   AgentFinishAction detected        │
         │   → Set state to FINISHED            │
         │   → End loop                         │
         └──────────────────────────────────────┘
```

---

## 12. BUILDING A PLANNER-AGENT SCAFFOLD

### Checklist for New Agent Implementation:

1. **Create Agent Class**
   - Inherit from `Agent` or specialized agent (e.g., `CodeActAgent`)
   - Implement `step(state)` method
   - Define `sandbox_plugins` if needed
   - Override `_get_tools()` to customize tool set

2. **Define Tools**
   - Create tool definitions in `tools/` subdirectory
   - Return `list[ChatCompletionToolParam]` from tool definition
   - Implement `response_to_actions()` to parse LLM responses

3. **Create Prompts**
   - Add `system_prompt.j2` template
   - Use Jinja2 for dynamic content
   - Consider `system_prompt_long_horizon.j2` for plan-based agents

4. **Handle Responses**
   - Implement `response_to_actions(response)` method
   - Convert tool calls to appropriate Action types
   - Handle security risks and error cases

5. **Register Agent**
   - Create `__init__.py` with registration:
     ```python
     from openhands.controller.agent import Agent
     from openhands.agenthub.your_agent.your_agent import YourAgent
     
     Agent.register('YourAgent', YourAgent)
     ```

6. **Configure in Config**
   - Add agent-specific configuration section
   - Enable/disable tools as needed
   - Set custom system prompt filename

7. **Test Integration**
   - Verify agent loads via `Agent.get_cls('YourAgent')`
   - Test with dummy tasks
   - Verify state persistence
   - Test delegation (if supporting)

---

## 13. KEY FILES TO UNDERSTAND

| Purpose | File | Lines |
|---------|------|-------|
| Agent Base Class | `/openhands/controller/agent.py` | 184 |
| Agent Controller Loop | `/openhands/controller/agent_controller.py` | 1391 |
| Runtime Base | `/openhands/runtime/base.py` | 1000+ |
| State Definition | `/openhands/controller/state/state.py` | 200+ |
| Event Stream | `/openhands/events/stream.py` | 400+ |
| CodeActAgent | `/openhands/agenthub/codeact_agent/codeact_agent.py` | 300+ |
| Function Calling | `/openhands/agenthub/codeact_agent/function_calling.py` | 250+ |
| Agent Config | `/openhands/core/config/agent_config.py` | 150+ |
| Conversation Memory | `/openhands/memory/conversation_memory.py` | 200+ |

---

## 14. IMPORTANT CONCEPTS

**Event Source**:
- `AGENT`: Action from agent
- `USER`: Action from user
- `ENVIRONMENT`: Observation from runtime

**Agent State**:
- `LOADING`: Initial state
- `RUNNING`: Actively executing
- `PAUSED`: Paused for user input
- `AWAITING_USER_CONFIRMATION`: Action awaiting approval
- `FINISHED`: Task completed successfully
- `ERROR`: Error occurred
- `REJECTED`: Agent rejected task

**Control Flags**:
- **IterationControlFlag**: Limits iterations with increase amounts
- **BudgetControlFlag**: Limits USD cost of LLM calls

**Message Format**:
- System message first (from SystemMessageAction)
- Alternating user/assistant/tool roles
- Each role can have multiple messages
- Tool responses paired with tool calls

---

## Summary

OpenHands provides a robust, extensible multi-agent framework with:
- Clean agent abstraction for customization
- Event-driven orchestration for decoupling
- Hierarchical delegation for multi-agent workflows  
- Rich state management for session persistence
- Flexible tool/plugin system for capabilities
- Security controls for safe execution

The architecture supports everything from simple single-agent tasks to complex multi-agent workflows with delegation.
