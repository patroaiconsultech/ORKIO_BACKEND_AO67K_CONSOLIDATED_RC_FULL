from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agent_evolution_map.router import AgentEvolutionMapRouterDeps, build_agent_evolution_map_router
from app.agent_evolution_map.service import AgentEvolutionMapService


def _admin():
    return {"id": "admin-1", "org_slug": "tenant-a"}

def _org(admin, header):
    return header or admin["org_slug"]

def _client(monkeypatch=None):
    app = FastAPI()
    app.include_router(build_agent_evolution_map_router(AgentEvolutionMapRouterDeps(
        require_admin_access=_admin, get_request_org=_org, now_ts=lambda: 1700000000)))
    return TestClient(app)

def test_snapshot_has_policy_fingerprint_and_health():
    snapshot = AgentEvolutionMapService(now_fn=lambda: 1700000000).get_snapshot("orkio", org_slug="tenant-a")
    assert snapshot is not None
    assert len(snapshot.snapshot_fingerprint) == 64
    assert len(snapshot.policy_resolution.resolved_fingerprint) == 64
    assert snapshot.health.status in {"green", "yellow", "red", "unknown"}
    assert snapshot.write_executed is False

def test_summary_is_read_only():
    response = _client().get("/api/admin/evolution/agents/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["aggregate"]["agent_count"] >= 1
    assert payload["aggregate"]["write_executed"] is False

def test_evidence_endpoint():
    response = _client().get("/api/admin/evolution/agents/orkio/evidence")
    assert response.status_code == 200
    assert response.json()["count"] >= 3

def test_stream_disabled_by_default(monkeypatch):
    monkeypatch.delenv("AGENT_EVOLUTION_MAP_STREAM_ENABLED", raising=False)
    response = _client().get("/api/admin/evolution/agents/stream")
    assert response.status_code == 404
    assert response.json()["detail"] == "AGENT_EVOLUTION_MAP_STREAM_DISABLED"
