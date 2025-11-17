"""Plan data structures for the PlannerAgent."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepStatus(str, Enum):
    """Status of a plan step."""

    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    BLOCKED = 'blocked'


@dataclass
class PlanStep:
    """Represents a single step in an execution plan.

    Attributes:
        id: Unique identifier for the step
        description: Human-readable description of what this step does
        agent_type: The type of agent to use (e.g., 'CodeActAgent')
        inputs: Input parameters for the agent
        status: Current status of the step
        result: Result or output from executing this step
        error: Error message if the step failed
        dependencies: List of step IDs that must complete before this one
        created_at: When this step was created
        started_at: When this step started execution
        completed_at: When this step completed
    """

    id: str
    description: str
    agent_type: str
    inputs: dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    result: str | None = None
    error: str | None = None
    dependencies: list[str] = field(default_factory=list)
    created_at: int = 0  # Event ID
    started_at: int | None = None
    completed_at: int | None = None

    def is_ready_to_execute(self, completed_steps: set[str]) -> bool:
        """Check if this step is ready to execute.

        Args:
            completed_steps: Set of step IDs that have been completed

        Returns:
            True if all dependencies are satisfied and step is pending
        """
        if self.status != StepStatus.PENDING:
            return False

        return all(dep_id in completed_steps for dep_id in self.dependencies)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'description': self.description,
            'agent_type': self.agent_type,
            'inputs': self.inputs,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'dependencies': self.dependencies,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PlanStep':
        """Create PlanStep from dictionary."""
        return cls(
            id=data['id'],
            description=data['description'],
            agent_type=data['agent_type'],
            inputs=data.get('inputs', {}),
            status=StepStatus(data.get('status', 'pending')),
            result=data.get('result'),
            error=data.get('error'),
            dependencies=data.get('dependencies', []),
            created_at=data.get('created_at', 0),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
        )


@dataclass
class Refinement:
    """Represents a refinement made to the plan.

    Attributes:
        iteration: Which iteration this refinement was made
        reason: Why this refinement was made
        changes: Description of what changed
        event_id: Event ID when this refinement was made
    """

    iteration: int
    reason: str
    changes: str
    event_id: int


@dataclass
class ExecutionPlan:
    """Represents the complete execution plan.

    Attributes:
        goal: The overall goal of the plan
        steps: List of plan steps
        context: Additional context (repository info, analysis results, etc.)
        iteration: Current iteration number (increments on refinement)
        refinements: History of plan refinements
        created_at: When the plan was created (event ID)
        updated_at: When the plan was last updated (event ID)
    """

    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    iteration: int = 0
    refinements: list[Refinement] = field(default_factory=list)
    created_at: int = 0
    updated_at: int = 0

    def get_step(self, step_id: str) -> PlanStep | None:
        """Get a step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_completed_steps(self) -> set[str]:
        """Get set of completed step IDs."""
        return {step.id for step in self.steps if step.status == StepStatus.COMPLETED}

    def get_next_steps(self) -> list[PlanStep]:
        """Get list of steps that are ready to execute."""
        completed = self.get_completed_steps()
        return [step for step in self.steps if step.is_ready_to_execute(completed)]

    def get_pending_steps(self) -> list[PlanStep]:
        """Get all pending steps."""
        return [step for step in self.steps if step.status == StepStatus.PENDING]

    def get_in_progress_steps(self) -> list[PlanStep]:
        """Get all in-progress steps."""
        return [step for step in self.steps if step.status == StepStatus.IN_PROGRESS]

    def get_failed_steps(self) -> list[PlanStep]:
        """Get all failed steps."""
        return [step for step in self.steps if step.status == StepStatus.FAILED]

    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        if not self.steps:
            return False
        return all(step.status == StepStatus.COMPLETED for step in self.steps)

    def has_failures(self) -> bool:
        """Check if any steps have failed."""
        return any(step.status == StepStatus.FAILED for step in self.steps)

    def add_step(self, step: PlanStep) -> None:
        """Add a new step to the plan."""
        self.steps.append(step)

    def add_refinement(self, reason: str, changes: str, event_id: int) -> None:
        """Add a refinement record."""
        self.iteration += 1
        self.refinements.append(
            Refinement(
                iteration=self.iteration, reason=reason, changes=changes, event_id=event_id
            )
        )
        self.updated_at = event_id

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'goal': self.goal,
            'steps': [step.to_dict() for step in self.steps],
            'context': self.context,
            'iteration': self.iteration,
            'refinements': [
                {
                    'iteration': r.iteration,
                    'reason': r.reason,
                    'changes': r.changes,
                    'event_id': r.event_id,
                }
                for r in self.refinements
            ],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ExecutionPlan':
        """Create ExecutionPlan from dictionary."""
        steps = [PlanStep.from_dict(step_data) for step_data in data.get('steps', [])]
        refinements = [
            Refinement(
                iteration=r['iteration'],
                reason=r['reason'],
                changes=r['changes'],
                event_id=r['event_id'],
            )
            for r in data.get('refinements', [])
        ]

        return cls(
            goal=data['goal'],
            steps=steps,
            context=data.get('context', {}),
            iteration=data.get('iteration', 0),
            refinements=refinements,
            created_at=data.get('created_at', 0),
            updated_at=data.get('updated_at', 0),
        )

    def get_summary(self) -> str:
        """Get a human-readable summary of the plan."""
        total = len(self.steps)
        completed = len([s for s in self.steps if s.status == StepStatus.COMPLETED])
        in_progress = len([s for s in self.steps if s.status == StepStatus.IN_PROGRESS])
        failed = len([s for s in self.steps if s.status == StepStatus.FAILED])
        pending = len([s for s in self.steps if s.status == StepStatus.PENDING])

        summary = f"Plan: {self.goal}\n"
        summary += f"Progress: {completed}/{total} steps completed\n"
        if in_progress > 0:
            summary += f"  {in_progress} in progress\n"
        if failed > 0:
            summary += f"  {failed} failed\n"
        if pending > 0:
            summary += f"  {pending} pending\n"
        summary += f"Iterations: {self.iteration}\n"

        return summary
