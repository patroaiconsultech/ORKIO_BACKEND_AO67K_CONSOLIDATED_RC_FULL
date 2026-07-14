from __future__ import annotations

from runtime.agent_turn_context import (
    resolve_agent_turn_context,
    stream_turn_owner_from_contract,
)


def test_orion_selection_locks_turn_ownership() -> None:
    ctx = resolve_agent_turn_context(
        "orion",
        route_family="governed_evolution_pipeline",
    )

    assert ctx.requested_agent == "orion"
    assert ctx.orchestrator_agent == "orkio"
    assert ctx.turn_owner == "orion"
    assert ctx.display_agent == "orion"
    assert ctx.technical_lead == "orion"
    assert ctx.ownership_locked is True
    assert ctx.agent_id == "orion"
    assert ctx.agent_name == "Orion"


def test_default_governed_flow_keeps_orkio_as_owner() -> None:
    ctx = resolve_agent_turn_context(
        None,
        route_family="governed_evolution_pipeline",
    )

    assert ctx.requested_agent == "orkio"
    assert ctx.orchestrator_agent == "orkio"
    assert ctx.turn_owner == "orkio"
    assert ctx.display_agent == "orkio"
    assert ctx.technical_lead == "orion"
    assert ctx.ownership_locked is False
    assert ctx.agent_id == "orkio"
    assert ctx.agent_name == "Orkio"


def test_context_payload_is_explicit_and_serializable() -> None:
    payload = resolve_agent_turn_context(
        "orion",
        route_family="governed_evolution_pipeline",
    ).to_routing_payload()

    assert payload["requested_agent"] == "orion"
    assert payload["orchestrator_agent"] == "orkio"
    assert payload["turn_owner"] == "orion"
    assert payload["display_agent"] == "orion"
    assert payload["ownership_locked"] is True
    assert payload["agent_id"] == "orion"
    assert payload["agent_name"] == "Orion"


def test_stream_owner_uses_destination_contract_before_public_guard() -> None:
    owner = stream_turn_owner_from_contract(
        visible_agent="orion",
        target_agent_slug="orion",
        requested_agent_names=["Orion"],
        route_plan={"requested_agent": "Orion", "resolved_agent": "Orion"},
    )

    assert owner == "orion"
    ctx = resolve_agent_turn_context(
        owner,
        route_family="governed_evolution_pipeline",
    )
    assert ctx.ownership_locked is True
    assert ctx.agent_id == "orion"
    assert ctx.agent_name == "Orion"


def test_stream_owner_can_fall_back_to_route_plan_resolution() -> None:
    owner = stream_turn_owner_from_contract(
        route_plan={"requested_agent": "Orion", "resolved_agent": "Orion"},
    )

    assert owner == "orion"


def test_stream_owner_is_empty_without_explicit_agent_contract() -> None:
    owner = stream_turn_owner_from_contract(
        visible_agent=None,
        target_agent_slug=None,
        requested_agent_names=[],
        route_plan={"route_family": "general"},
    )

    assert owner is None
