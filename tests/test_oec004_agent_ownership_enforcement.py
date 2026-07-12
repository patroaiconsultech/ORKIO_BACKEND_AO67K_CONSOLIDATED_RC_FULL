from dataclasses import dataclass

from runtime.agent_ownership_enforcement import (
    enforce_locked_payload_owner,
    resolve_persistence_owner,
    should_allow_chris_context_continuity,
)


@dataclass(frozen=True)
class Ctx:
    requested_agent: str
    turn_owner: str
    display_agent: str
    ownership_locked: bool = True


def test_orion_blocks_chris_continuity():
    allowed, reason = should_allow_chris_context_continuity(
        Ctx("orion", "orion", "orion")
    )
    assert allowed is False
    assert reason == "explicit_non_chris_owner"


def test_chris_keeps_legitimate_continuity():
    allowed, reason = should_allow_chris_context_continuity(
        Ctx("chris", "chris", "chris")
    )
    assert allowed is True
    assert reason == "explicit_chris_owner"


def test_persistence_is_rewritten_to_orion():
    agent_id, agent_name, changed = resolve_persistence_owner(
        "chris", "Chris", Ctx("orion", "orion", "orion")
    )
    assert (agent_id, agent_name, changed) == ("orion", "Orion", True)


def test_final_envelope_is_rewritten_to_orion():
    payload, changed = enforce_locked_payload_owner(
        {
            "agent_id": "chris",
            "agent_name": "Chris",
            "final_speaker": "Chris",
            "runtime_hints": {"routing": {"resolved_agent": "Orion"}},
        },
        Ctx("orion", "orion", "orion"),
    )
    assert changed is True
    assert payload["agent_id"] == "orion"
    assert payload["agent_name"] == "Orion"
    assert payload["final_speaker"] == "Orion"
    assert payload["runtime_hints"]["routing"]["ownership_locked"] is True


def test_unlocked_context_is_fail_open():
    ctx = Ctx("", "orkio", "orkio", ownership_locked=False)
    payload, changed = enforce_locked_payload_owner(
        {"agent_id": "chris", "agent_name": "Chris"}, ctx
    )
    assert changed is False
    assert payload["agent_name"] == "Chris"
