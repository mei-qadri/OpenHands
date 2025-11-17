"""Planning tools for the PlannerAgent."""

from litellm import ChatCompletionToolParam

# Tool for creating a new execution plan
CreatePlanTool: ChatCompletionToolParam = {
    'type': 'function',
    'function': {
        'name': 'create_plan',
        'description': (
            'Create an execution plan to accomplish the given goal. '
            'Analyze the task, break it down into steps, and assign each step to an appropriate agent. '
            'Consider dependencies between steps and ensure the plan is logical and efficient.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'goal': {
                    'type': 'string',
                    'description': 'The overall goal or objective to accomplish',
                },
                'steps': {
                    'type': 'array',
                    'description': 'List of steps to execute',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {
                                'type': 'string',
                                'description': 'Unique identifier for this step (e.g., "step1", "step2")',
                            },
                            'description': {
                                'type': 'string',
                                'description': 'Clear description of what this step should accomplish',
                            },
                            'agent_type': {
                                'type': 'string',
                                'description': (
                                    'The agent type to use for this step. '
                                    'Options: CodeActAgent (code execution, file operations), '
                                    'BrowsingAgent (web browsing, research), '
                                    'VisualBrowsingAgent (visual web browsing)'
                                ),
                                'enum': [
                                    'CodeActAgent',
                                    'BrowsingAgent',
                                    'VisualBrowsingAgent',
                                ],
                            },
                            'inputs': {
                                'type': 'object',
                                'description': 'Input parameters for the agent (e.g., {"task": "description"})',
                            },
                            'dependencies': {
                                'type': 'array',
                                'description': 'List of step IDs that must complete before this step',
                                'items': {'type': 'string'},
                            },
                        },
                        'required': ['id', 'description', 'agent_type'],
                    },
                },
                'context': {
                    'type': 'object',
                    'description': (
                        'Additional context about the task (repository structure, '
                        'relevant files, technologies used, etc.)'
                    ),
                },
            },
            'required': ['goal', 'steps'],
        },
    },
}

# Tool for updating an existing plan
UpdatePlanTool: ChatCompletionToolParam = {
    'type': 'function',
    'function': {
        'name': 'update_plan',
        'description': (
            'Update the execution plan based on feedback from completed steps. '
            'Use this to mark steps as complete/failed, add new steps, or modify existing steps. '
            'Provide a clear explanation of why the plan is being updated.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'step_id': {
                    'type': 'string',
                    'description': 'ID of the step to update',
                },
                'status': {
                    'type': 'string',
                    'description': 'New status for the step',
                    'enum': ['completed', 'failed', 'blocked', 'in_progress'],
                },
                'result': {
                    'type': 'string',
                    'description': 'Result or outcome from the step execution',
                },
                'error': {
                    'type': 'string',
                    'description': 'Error message if the step failed',
                },
                'new_steps': {
                    'type': 'array',
                    'description': 'New steps to add to the plan',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                            'description': {'type': 'string'},
                            'agent_type': {
                                'type': 'string',
                                'enum': [
                                    'CodeActAgent',
                                    'BrowsingAgent',
                                    'VisualBrowsingAgent',
                                ],
                            },
                            'inputs': {'type': 'object'},
                            'dependencies': {
                                'type': 'array',
                                'items': {'type': 'string'},
                            },
                        },
                        'required': ['id', 'description', 'agent_type'],
                    },
                },
                'refinement_reason': {
                    'type': 'string',
                    'description': 'Explain why this refinement is needed',
                },
                'refinement_changes': {
                    'type': 'string',
                    'description': 'Summary of what changed in the plan',
                },
            },
            'required': ['step_id', 'status'],
        },
    },
}

# Tool for delegating a task to a sub-agent
DelegateTaskTool: ChatCompletionToolParam = {
    'type': 'function',
    'function': {
        'name': 'delegate_task',
        'description': (
            'Delegate a specific plan step to an appropriate specialized agent. '
            'The agent will execute the step and return results. '
            'Use this after creating a plan to execute each step.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'step_id': {
                    'type': 'string',
                    'description': 'The ID of the plan step being delegated',
                },
                'agent_type': {
                    'type': 'string',
                    'description': 'The type of agent to delegate to',
                    'enum': ['CodeActAgent', 'BrowsingAgent', 'VisualBrowsingAgent'],
                },
                'task': {
                    'type': 'string',
                    'description': (
                        'Clear task description for the agent. '
                        'Be specific about what you want the agent to accomplish.'
                    ),
                },
                'inputs': {
                    'type': 'object',
                    'description': 'Additional input parameters for the agent',
                },
            },
            'required': ['step_id', 'agent_type', 'task'],
        },
    },
}

# Tool for thinking/reasoning (useful for planning)
ThinkTool: ChatCompletionToolParam = {
    'type': 'function',
    'function': {
        'name': 'think',
        'description': (
            'Record your reasoning and thought process. '
            'Use this to analyze the situation, consider options, '
            'and explain your planning decisions.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'thought': {
                    'type': 'string',
                    'description': 'Your reasoning or thought process',
                },
            },
            'required': ['thought'],
        },
    },
}

# Tool for finishing the planning task
FinishTool: ChatCompletionToolParam = {
    'type': 'function',
    'function': {
        'name': 'finish',
        'description': (
            'Mark the planning task as complete. '
            'Use this when all plan steps have been executed successfully '
            'and the overall goal has been achieved.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'summary': {
                    'type': 'string',
                    'description': 'Summary of what was accomplished',
                },
                'outputs': {
                    'type': 'object',
                    'description': 'Final outputs or results from the execution',
                },
            },
            'required': ['summary'],
        },
    },
}

# Tool for viewing the current plan
ViewPlanTool: ChatCompletionToolParam = {
    'type': 'function',
    'function': {
        'name': 'view_plan',
        'description': (
            'View the current execution plan with all steps and their status. '
            'Use this to check progress and decide on next actions.'
        ),
        'parameters': {
            'type': 'object',
            'properties': {},
        },
    },
}


def get_planner_tools() -> list[ChatCompletionToolParam]:
    """Get all tools for the PlannerAgent."""
    return [
        CreatePlanTool,
        UpdatePlanTool,
        DelegateTaskTool,
        ThinkTool,
        ViewPlanTool,
        FinishTool,
    ]
