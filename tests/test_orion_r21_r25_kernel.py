import pytest

from orion.kernel.event_bus import EventBus
from orion.kernel.state_machine import CycleState, InvalidTransition, StateMachine


def test_state_machine_happy_path():
    machine = StateMachine()
    state = CycleState.IDLE
    for event in (
        "START",
        "EVIDENCE_COLLECTED",
        "DIAGNOSIS_COMPLETED",
        "PROPOSAL_CREATED",
        "HUMAN_APPROVAL_GRANTED",
        "PATCH_GENERATED",
        "PATCH_EXECUTED",
        "VALIDATION_PASSED",
        "OUTCOME_READY",
        "OUTCOME_RECORDED",
    ):
        state = machine.transition(state, event)
    assert state is CycleState.COMPLETED


def test_invalid_transition_is_deterministic():
    with pytest.raises(InvalidTransition, match="invalid_transition"):
        StateMachine().transition(CycleState.IDLE, "DEPLOY")


def test_event_bus_preserves_cycle_order():
    from orion.contracts.models import OrionEvent
    bus = EventBus()
    first = OrionEvent("A", "cycle-1", "corr-1", "test", {})
    second = OrionEvent("B", "cycle-1", "corr-1", "test", {})
    bus.publish(first)
    bus.publish(second)
    assert [event.event_type for event in bus.audit_trail("cycle-1")] == ["A", "B"]
