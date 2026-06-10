from __future__ import annotations

"""
AO67B — Journey Router

Classifica a jornada antes de qualquer oferta de agentes ou especialistas.
O roteador não responde ao usuário, não chama LLM e não executa especialistas.
Ele apenas produz uma decisão auditável para o Orkio Decision Mesh.
"""

from typing import Any, Dict, Iterable, List, Optional

from .hook_registry import HOOK_REGISTRY_VERSION, normalize_text, select_hooks


JOURNEY_ROUTER_VERSION = "AO67B_JOURNEY_ROUTER_V1"

_GUARD_TO_INTENT = {
    "guard.agent_catalog": "agent_catalog_request",
    "guard.internal_agent_request": "internal_agent_request",
    "guard.technical_governance": "technical_governance_request",
}

_JOURNEY_TO_INTENT = {
    "journey.institutional": "institutional_amcham_patroai",
    "journey.platform_exploration": "platform_exploration",
    "journey.professional_development": "professional_development",
    "journey.skills_mapping": "skills_mapping",
    "journey.networking": "networking",
    "journey.leadership": "leadership",
    "journey.internal_innovation": "internal_innovation",
    "journey.ai_project": "ai_project",
    "journey.entrepreneurship": "entrepreneurship",
    "journey.business_diagnostic": "business_or_project_diagnostic",
}


def _best_by_family(selected_hooks: Iterable[Dict[str, Any]], family: str) -> Optional[Dict[str, Any]]:
    hooks = [item for item in selected_hooks or [] if str(item.get("family") or "") == family]
    if not hooks:
        return None
    hooks.sort(key=lambda item: (-float(item.get("score") or 0), int(item.get("priority") or 100)))
    return hooks[0]


def route_public_journey(
    message: Any,
    *,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
    include_internal_hooks: bool = True,
) -> Dict[str, Any]:
    normalized = normalize_text(message)
    selected = select_hooks(
        normalized,
        include_internal=include_internal_hooks,
        include_guards=True,
        max_hooks=8,
    )

    guard = _best_by_family(selected, "guard")
    journey = _best_by_family(selected, "journey")

    if guard:
        primary_hook = guard
        intent = _GUARD_TO_INTENT.get(str(guard.get("hook_id") or ""), "public_guard")
        route_family = "public_guard"
        confidence = float(guard.get("score") or 0.0)
        should_answer_immediately = True
    elif journey:
        primary_hook = journey
        intent = _JOURNEY_TO_INTENT.get(str(journey.get("hook_id") or ""), "public_journey")
        route_family = "public_journey"
        confidence = float(journey.get("score") or 0.0)
        should_answer_immediately = confidence >= 0.48
    else:
        primary_hook = None
        intent = "open_conversation"
        route_family = "open_conversation"
        confidence = 0.0
        should_answer_immediately = False

    return {
        "ok": True,
        "service": "journey_router",
        "version": JOURNEY_ROUTER_VERSION,
        "hook_registry_version": HOOK_REGISTRY_VERSION,
        "normalized_message": normalized,
        "intent": intent,
        "route_family": route_family,
        "confidence": round(confidence, 3),
        "primary_hook_id": str(primary_hook.get("hook_id") or "") if primary_hook else "",
        "selected_hooks": selected,
        "should_answer_immediately": bool(should_answer_immediately),
        "visible_agent": "Orkio",
        "target_agent_slug": str(target_agent_slug or ""),
        "route_plan_present": bool(route_plan),
    }


def route_runtime_hints(route: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "routing": {
            "routing_source": "journey_router",
            "route_applied": bool(route.get("should_answer_immediately")),
            "route_family": route.get("route_family") or "open_conversation",
            "route_reason": route.get("intent") or "open_conversation",
            "policy_version": JOURNEY_ROUTER_VERSION,
            "visible_agent": "Orkio",
        },
        "journey_router": {
            "version": JOURNEY_ROUTER_VERSION,
            "intent": route.get("intent"),
            "confidence": route.get("confidence"),
            "primary_hook_id": route.get("primary_hook_id"),
            "selected_hook_ids": [
                str(item.get("hook_id") or "")
                for item in (route.get("selected_hooks") or [])
            ],
        },
    }
