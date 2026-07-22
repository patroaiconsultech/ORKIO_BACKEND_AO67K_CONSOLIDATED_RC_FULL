from app.agent_evolution_map.service import AgentEvolutionMapService


def test_list_snapshots_is_read_only_and_contains_canonical_agents():
    service = AgentEvolutionMapService(now_fn=lambda: 1700000000)
    snapshots = service.list_snapshots(org_slug="tenant-a")

    ids = {item.agent.agent_id for item in snapshots}
    assert "orkio" in ids
    assert "chris" in ids
    assert all(item.write_executed is False for item in snapshots)
    assert all(item.governance["read_only"] is True for item in snapshots)
    assert all(item.governance["tenant_scope"] == "tenant-a" for item in snapshots)


def test_snapshot_composes_capabilities_and_evidence():
    service = AgentEvolutionMapService(now_fn=lambda: 1700000000)
    snapshot = service.get_snapshot("orkio", org_slug="tenant-a")

    assert snapshot is not None
    assert snapshot.agent.display_name == "Orkio"
    assert snapshot.metrics["declared_capabilities"] == len(snapshot.capabilities)
    assert snapshot.metrics["declared_capabilities"] > 0
    assert snapshot.freshness_seconds == 0
    assert len(snapshot.evidence) >= 3


def test_unknown_agent_returns_none():
    service = AgentEvolutionMapService(now_fn=lambda: 1700000000)
    assert service.get_snapshot("does-not-exist", org_slug="tenant-a") is None
