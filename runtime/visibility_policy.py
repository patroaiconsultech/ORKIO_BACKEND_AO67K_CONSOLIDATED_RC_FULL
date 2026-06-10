from __future__ import annotations

"""
AO67A — Visibility Policy

Camada de visibilidade pública. Ela não decide qual conhecimento interno pode ser
consultado; apenas garante que a superfície pública continue segura e que Orkio
permaneça como condutor visível quando houver agentes internos.
"""

from typing import Any, Dict, Optional

from app.services.agent_access_policy import (
    AGENT_ACCESS_POLICY_VERSION,
    PUBLIC_VISIBLE_AGENT_ID,
    PUBLIC_VISIBLE_AGENT_NAME,
    is_internal_agent_name,
    public_visible_agent_name,
)


VISIBILITY_POLICY_VERSION = "AO67A_VISIBILITY_POLICY_V1"


def resolve_public_visible_agent(agent_name: Any = None, *, fallback: str = PUBLIC_VISIBLE_AGENT_NAME) -> str:
    if is_internal_agent_name(agent_name):
        return PUBLIC_VISIBLE_AGENT_NAME
    value = str(agent_name or "").strip()
    return value or fallback


def public_visibility_runtime_hints(
    *,
    reason: str = "public_visibility_policy",
    blocked_agent: Optional[str] = None,
    route_family: str = "public_visibility",
) -> Dict[str, Any]:
    return {
        "routing": {
            "routing_source": "visibility_policy",
            "route_applied": True,
            "execution_lifecycle": "completed",
            "route_family": route_family,
            "route_reason": reason,
            "policy_version": VISIBILITY_POLICY_VERSION,
            "agent_access_policy_version": AGENT_ACCESS_POLICY_VERSION,
            "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
            "final_speaker": PUBLIC_VISIBLE_AGENT_NAME,
            "resolved_agent": PUBLIC_VISIBLE_AGENT_NAME,
            "blocked_agent": blocked_agent,
            "write_executed": False,
            "proposal_created": False,
            "branch_created": False,
            "pr_created": False,
            "deploy_executed": False,
        }
    }


def apply_public_visibility_payload(
    payload: Dict[str, Any],
    *,
    blocked_agent: Optional[str] = None,
    reason: str = "public_visibility_policy",
) -> Dict[str, Any]:
    data = dict(payload or {})
    data["agent_id"] = PUBLIC_VISIBLE_AGENT_ID
    data["agent_name"] = PUBLIC_VISIBLE_AGENT_NAME
    data["final_speaker"] = PUBLIC_VISIBLE_AGENT_NAME
    data["visible_agent"] = PUBLIC_VISIBLE_AGENT_NAME
    data["resolved_agent"] = PUBLIC_VISIBLE_AGENT_NAME
    if blocked_agent:
        data["blocked_agent"] = blocked_agent

    hints = data.get("runtime_hints") if isinstance(data.get("runtime_hints"), dict) else {}
    routing = hints.get("routing") if isinstance(hints.get("routing"), dict) else {}
    routing.update(public_visibility_runtime_hints(reason=reason, blocked_agent=blocked_agent).get("routing", {}))
    hints["routing"] = routing
    data["runtime_hints"] = hints
    return data
