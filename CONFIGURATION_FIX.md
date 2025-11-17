# Configuration Fix for PlannerAgent

## Issue

The initial examples had incorrect configuration code. The `AgentConfig` class doesn't accept `agent_name` or `llm_config` as direct parameters.

## ❌ INCORRECT (Old Examples)

```python
# DON'T DO THIS - It will fail!
llm_config = LLMConfig(model="gpt-4", api_key="key")
agent_config = AgentConfig(
    agent_name="PlannerAgent",  # ❌ This field doesn't exist!
    llm_config=llm_config        # ❌ Should be a string, not LLMConfig object!
)
```

## ✅ CORRECT Configuration

```python
from openhands.core.config import AgentConfig, LLMConfig
from openhands.core.config.openhands_config import OpenHandsConfig
from openhands.llm.llm_registry import LLMRegistry
from openhands.agenthub.planner_agent import PlannerAgent

# Step 1: Create LLM configuration
llm_config = LLMConfig(
    model="claude-sonnet-4-5",  # or gpt-4, gpt-4-turbo, etc.
    api_key="your-api-key"
)

# Step 2: Create OpenHands configuration
openhands_config = OpenHandsConfig()
openhands_config.set_llm_config(llm_config)  # Set the default LLM config

# Step 3: Create LLM Registry from the config
llm_registry = LLMRegistry(config=openhands_config)

# Step 4: Create Agent configuration (no parameters!)
agent_config = AgentConfig()

# Step 5: Create the agent
agent = PlannerAgent(config=agent_config, llm_registry=llm_registry)
```

## Why This Pattern?

1. **OpenHandsConfig** is the top-level configuration containing:
   - Multiple LLM configs (can have different models for different purposes)
   - Multiple Agent configs (can configure different agents differently)

2. **LLMRegistry** is created from OpenHandsConfig and manages LLM instances

3. **AgentConfig** contains agent-specific settings (tools to enable, prompts, etc.)
   - The `llm_config` field is a STRING name referencing an LLM config in OpenHandsConfig
   - Not needed for basic usage - defaults to 'llm'

4. **Agent** (PlannerAgent) receives:
   - `config`: The AgentConfig
   - `llm_registry`: The registry that knows how to create LLMs

## Corrected Examples

The following files have been updated with the correct pattern:

- ✅ `examples/quick_test_planner.py` - CORRECTED
- ⚠️  `TESTING_WITH_REPOSITORY.md` - Contains old examples (use quick_test_planner.py instead)
- ⚠️  `test_planner_agent.md` - Contains old examples (use quick_test_planner.py instead)

## Quick Test to Verify

Run this to test with the correct configuration:

```bash
export LLM_API_KEY=your-api-key
python examples/quick_test_planner.py
```

If you see "✅ Agent initialized with 6 tools", the configuration is correct!

## For Reference: Agent Config Fields

Here are the actual fields in `AgentConfig` (from `openhands/core/config/agent_config.py`):

```python
class AgentConfig(BaseModel):
    cli_mode: bool = False
    llm_config: str | None = None  # ← STRING name, not LLMConfig object!
    classpath: str | None = None
    system_prompt_filename: str = "system_prompt.j2"
    enable_browsing: bool = True
    enable_llm_editor: bool = False
    enable_editor: bool = True
    enable_jupyter: bool = True
    enable_cmd: bool = True
    enable_think: bool = True
    enable_finish: bool = True
    # ... and more
```

Notice:
- No `agent_name` field!
- `llm_config` is a string, not an LLMConfig object!
- The `model_config = ConfigDict(extra='forbid')` means it rejects unknown fields

## Apology

Sorry for the confusion in the initial examples! The corrected `quick_test_planner.py` script now shows the proper configuration pattern that matches OpenHands' actual API.
