from runtime.agent_turn_context import (
    EXPLICIT_TURN_OWNER_SLUGS,
    explicit_turn_owner_candidate,
    resolve_agent_turn_context,
    stream_turn_owner_from_contract,
)


def test_registered_explicit_agents_lock_turn_ownership():
    assert EXPLICIT_TURN_OWNER_SLUGS == frozenset(
        {"orkio", "orion", "chris", "laura"}
    )

    for slug in sorted(EXPLICIT_TURN_OWNER_SLUGS):
        context = resolve_agent_turn_context(
            slug,
            route_family="chat",
            orchestrator_agent="orkio",
        )
        assert context.requested_agent == slug
        assert context.turn_owner == slug
        assert context.display_agent == slug
        assert context.agent_id == slug
        assert context.ownership_locked is True


def test_at_prefix_is_normalized_for_explicit_selection():
    context = resolve_agent_turn_context("@Laura", route_family="chat")
    assert context.turn_owner == "laura"
    assert context.ownership_locked is True


def test_team_is_not_silently_enabled():
    context = resolve_agent_turn_context("team", route_family="chat")
    assert context.requested_agent == "team"
    assert context.turn_owner == "orkio"
    assert context.display_agent == "orkio"
    assert context.ownership_locked is False


def test_explicit_candidate_recognizes_laura_and_nested_values():
    assert explicit_turn_owner_candidate(None, ["unknown", "@Laura"]) == "laura"
    assert explicit_turn_owner_candidate("team") is None


def test_stream_contract_uses_explicit_owner():
    assert (
        stream_turn_owner_from_contract(
            route_plan={"resolved_agent": "Chris"},
            visible_agent="Laura",
        )
        == "laura"
    )
