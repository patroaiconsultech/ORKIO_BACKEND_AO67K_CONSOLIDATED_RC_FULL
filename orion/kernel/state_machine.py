from __future__ import annotations

from enum import Enum


class CycleState(str, Enum):
    IDLE = "IDLE"
    OBSERVING = "OBSERVING"
    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    ENGINEERING = "ENGINEERING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    REVIEW_READY = "REVIEW_READY"
    LEARNING = "LEARNING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class InvalidTransition(RuntimeError):
    pass


class StateMachine:
    TRANSITIONS = {
        (CycleState.IDLE, "START"): CycleState.OBSERVING,
        (CycleState.OBSERVING, "EVIDENCE_COLLECTED"): CycleState.UNDERSTANDING,
        (CycleState.UNDERSTANDING, "DIAGNOSIS_COMPLETED"): CycleState.PLANNING,
        (CycleState.PLANNING, "PROPOSAL_CREATED"): CycleState.AWAITING_APPROVAL,
        (CycleState.AWAITING_APPROVAL, "HUMAN_APPROVAL_GRANTED"): CycleState.ENGINEERING,
        (CycleState.ENGINEERING, "PATCH_GENERATED"): CycleState.EXECUTING,
        (CycleState.EXECUTING, "PATCH_EXECUTED"): CycleState.VALIDATING,
        (CycleState.VALIDATING, "VALIDATION_PASSED"): CycleState.REVIEW_READY,
        (CycleState.REVIEW_READY, "OUTCOME_READY"): CycleState.LEARNING,
        (CycleState.LEARNING, "OUTCOME_RECORDED"): CycleState.COMPLETED,
    }

    def transition(self, current: CycleState, event: str) -> CycleState:
        key = (current, event)
        if key not in self.TRANSITIONS:
            raise InvalidTransition(f"invalid_transition:{current.value}:{event}")
        return self.TRANSITIONS[key]
