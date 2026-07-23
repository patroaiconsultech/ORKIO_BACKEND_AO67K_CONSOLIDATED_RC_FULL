from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from orion.contracts.models import OrionEvent
from .event_bus import EventBus
from .state_machine import CycleState, StateMachine


@dataclass
class KernelServices:
    perception: Any
    reasoning: Any
    planning: Any
    engineering: Any
    governance: Any
    execution: Any
    validation: Any
    learning: Any


@dataclass
class CycleContext:
    repo_root: str
    objective: str
    cycle_id: str = field(default_factory=lambda: f"cycle_{uuid4().hex[:16]}")
    correlation_id: str = field(default_factory=lambda: f"corr_{uuid4().hex[:16]}")
    state: CycleState = CycleState.IDLE
    artifacts: dict[str, Any] = field(default_factory=dict)


class CognitiveKernel:
    """
    Orchestrator only. It does not write code, run shell commands, approve,
    push, merge or deploy.
    """

    def __init__(
        self,
        services: KernelServices,
        *,
        state_machine: StateMachine | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.services = services
        self.state_machine = state_machine or StateMachine()
        self.events = event_bus or EventBus()

    def _move(self, context: CycleContext, event: str, payload: dict[str, Any]) -> None:
        context.state = self.state_machine.transition(context.state, event)
        self.events.publish(OrionEvent(
            event_type=event,
            cycle_id=context.cycle_id,
            correlation_id=context.correlation_id,
            producer="orion.kernel",
            payload=payload,
        ))

    def prepare_proposal(self, context: CycleContext) -> Any:
        self._move(context, "START", {"objective": context.objective})
        evidence = self.services.perception.collect(context)
        context.artifacts["evidence"] = evidence
        self._move(context, "EVIDENCE_COLLECTED", {"count": len(evidence)})

        diagnosis = self.services.reasoning.diagnose(evidence, context)
        context.artifacts["diagnosis"] = diagnosis
        self._move(context, "DIAGNOSIS_COMPLETED", {"diagnosis_id": diagnosis.diagnosis_id})

        proposal = self.services.planning.build_proposal(diagnosis, context)
        context.artifacts["proposal"] = proposal
        self._move(context, "PROPOSAL_CREATED", {"proposal_id": proposal.proposal_id})
        return proposal
