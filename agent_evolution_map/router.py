from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from .contracts import AgentEvolutionListOut, AgentEvolutionSnapshot
from .service import AgentEvolutionMapService, CONTRACT_VERSION


@dataclass(frozen=True)
class AgentEvolutionMapRouterDeps:
    require_admin_access: Callable[..., Any]
    get_request_org: Callable[[dict[str, Any], Optional[str]], str]
    now_ts: Callable[[], int]


def _flag(name: str, default: str) -> bool:
    return str(os.getenv(name, default)).strip().lower() in {"1", "true", "yes", "on"}


def build_agent_evolution_map_router(deps: AgentEvolutionMapRouterDeps) -> APIRouter:
    router = APIRouter(prefix="/api/admin/evolution/agents", tags=["admin-agent-evolution-map"])
    service = AgentEvolutionMapService(now_fn=deps.now_ts)

    def ensure_enabled() -> None:
        if not _flag("AGENT_EVOLUTION_MAP_ENABLED", "true"):
            raise HTTPException(status_code=404, detail="AGENT_EVOLUTION_MAP_DISABLED")

    def resolve(agent_id: str, admin: dict[str, Any], x_org_slug: Optional[str]) -> tuple[str, AgentEvolutionSnapshot]:
        ensure_enabled()
        org_slug = deps.get_request_org(admin, x_org_slug)
        snapshot = service.get_snapshot(agent_id, org_slug=org_slug)
        if snapshot is None:
            raise HTTPException(status_code=404, detail="AGENT_NOT_FOUND")
        return org_slug, snapshot

    @router.get("", response_model=AgentEvolutionListOut)
    def list_agents(x_org_slug: Optional[str] = Header(default=None), admin=Depends(deps.require_admin_access)):
        ensure_enabled()
        org_slug = deps.get_request_org(admin, x_org_slug)
        items = service.list_snapshots(org_slug=org_slug)
        return AgentEvolutionListOut(
            contract_version=CONTRACT_VERSION,
            org_slug=org_slug,
            count=len(items),
            aggregate=service.aggregate(items),
            items=items,
            write_executed=False,
        )

    @router.get("/summary")
    def get_summary(x_org_slug: Optional[str] = Header(default=None), admin=Depends(deps.require_admin_access)):
        ensure_enabled()
        org_slug = deps.get_request_org(admin, x_org_slug)
        items = service.list_snapshots(org_slug=org_slug)
        return {
            "contract_version": CONTRACT_VERSION,
            "org_slug": org_slug,
            "aggregate": service.aggregate(items),
            "measured_at": deps.now_ts(),
            "write_executed": False,
        }

    @router.get("/stream")
    async def stream_agents(
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
    ):
        ensure_enabled()
        if not _flag("AGENT_EVOLUTION_MAP_STREAM_ENABLED", "false"):
            raise HTTPException(status_code=404, detail="AGENT_EVOLUTION_MAP_STREAM_DISABLED")
        org_slug = deps.get_request_org(admin, x_org_slug)
        interval = max(5, min(60, int(os.getenv("AGENT_EVOLUTION_MAP_STREAM_INTERVAL_SECONDS", "15"))))

        async def events():
            last_fingerprint = ""
            yield "event: status\ndata: " + json.dumps({"status": "connected", "contract_version": CONTRACT_VERSION}) + "\n\n"
            while True:
                if await request.is_disconnected():
                    break
                items = service.list_snapshots(org_slug=org_slug)
                aggregate = service.aggregate(items)
                fingerprint = "|".join(item.snapshot_fingerprint for item in items)
                if fingerprint != last_fingerprint:
                    payload = {
                        "contract_version": CONTRACT_VERSION,
                        "org_slug": org_slug,
                        "aggregate": aggregate,
                        "items": [item.model_dump() for item in items],
                        "write_executed": False,
                    }
                    yield "event: snapshot\ndata: " + json.dumps(payload, separators=(",", ":")) + "\n\n"
                    last_fingerprint = fingerprint
                else:
                    yield "event: heartbeat\ndata: " + json.dumps({"ts": deps.now_ts()}) + "\n\n"
                await asyncio.sleep(interval)
            yield "event: done\ndata: {}\n\n"

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/{agent_id}", response_model=AgentEvolutionSnapshot)
    @router.get("/{agent_id}/snapshot", response_model=AgentEvolutionSnapshot)
    def get_agent_snapshot(agent_id: str, x_org_slug: Optional[str] = Header(default=None), admin=Depends(deps.require_admin_access)):
        _, snapshot = resolve(agent_id, admin, x_org_slug)
        return snapshot

    @router.get("/{agent_id}/capabilities")
    def get_agent_capabilities(agent_id: str, x_org_slug: Optional[str] = Header(default=None), admin=Depends(deps.require_admin_access)):
        org_slug, snapshot = resolve(agent_id, admin, x_org_slug)
        return {"contract_version": CONTRACT_VERSION, "org_slug": org_slug, "agent_id": snapshot.agent.agent_id,
                "count": len(snapshot.capabilities), "items": [x.model_dump() for x in snapshot.capabilities], "write_executed": False}

    @router.get("/{agent_id}/gaps")
    def get_agent_gaps(agent_id: str, x_org_slug: Optional[str] = Header(default=None), admin=Depends(deps.require_admin_access)):
        org_slug, snapshot = resolve(agent_id, admin, x_org_slug)
        return {"contract_version": CONTRACT_VERSION, "org_slug": org_slug, "agent_id": snapshot.agent.agent_id,
                "count": len(snapshot.gaps), "items": [x.model_dump() for x in snapshot.gaps], "write_executed": False}

    @router.get("/{agent_id}/dependencies")
    def get_agent_dependencies(agent_id: str, x_org_slug: Optional[str] = Header(default=None), admin=Depends(deps.require_admin_access)):
        org_slug, snapshot = resolve(agent_id, admin, x_org_slug)
        return {"contract_version": CONTRACT_VERSION, "org_slug": org_slug, "agent_id": snapshot.agent.agent_id,
                "count": len(snapshot.dependencies), "items": snapshot.dependencies, "write_executed": False}

    @router.get("/{agent_id}/evidence")
    def get_agent_evidence(agent_id: str, x_org_slug: Optional[str] = Header(default=None), admin=Depends(deps.require_admin_access)):
        org_slug, snapshot = resolve(agent_id, admin, x_org_slug)
        return {"contract_version": CONTRACT_VERSION, "org_slug": org_slug, "agent_id": snapshot.agent.agent_id,
                "count": len(snapshot.evidence), "items": [x.model_dump() for x in snapshot.evidence], "write_executed": False}

    return router
