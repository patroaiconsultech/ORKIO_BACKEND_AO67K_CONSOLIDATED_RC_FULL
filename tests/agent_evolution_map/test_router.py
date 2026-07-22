from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agent_evolution_map.router import (
    AgentEvolutionMapRouterDeps,
    build_agent_evolution_map_router,
)


def _admin():
    return {"id": "admin-1", "org_slug": "tenant-a"}


def _org(admin, header):
    return header or admin["org_slug"]


def build_client():
    app = FastAPI()
    app.include_router(
        build_agent_evolution_map_router(
            AgentEvolutionMapRouterDeps(
                require_admin_access=_admin,
                get_request_org=_org,
                now_ts=lambda: 1700000000,
            )
        )
    )
    return TestClient(app)


def test_list_route():
    response = build_client().get("/api/admin/evolution/agents")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert payload["write_executed"] is False


def test_agent_route_and_tenant_header():
    response = build_client().get(
        "/api/admin/evolution/agents/chris",
        headers={"x-org-slug": "tenant-b"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["agent"]["agent_id"] == "chris"
    assert payload["governance"]["tenant_scope"] == "tenant-b"


def test_unknown_agent_is_404():
    response = build_client().get("/api/admin/evolution/agents/missing")
    assert response.status_code == 404
    assert response.json()["detail"] == "AGENT_NOT_FOUND"
