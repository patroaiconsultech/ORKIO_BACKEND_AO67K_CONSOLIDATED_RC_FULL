from __future__ import annotations

"""EOS-06 Executive Intelligence context envelope.

Pure and readonly by design: no provider, database, network, filesystem, or
execution side effects. It converts existing institutional signals into a
bounded context contract for Orkio without treating declarations as evidence.
"""

from typing import Any, Dict, Iterable, List, Optional


EOS06_VERSION = "EOS06_EXECUTIVE_INTELLIGENCE_FOUNDATION_V1"
DEFAULT_MISSION = (
    "Conduzir pessoas e organizacoes da ambiguidade a decisoes robustas, "
    "roadmaps executaveis e resultados mensuraveis com evidencia, governanca "
    "e aprovacao humana para mudancas estruturais."
)


def _clean(value: Any, limit: int = 240) -> str:
    return " ".join(str(value or "").split()).strip()[:limit]


def _string_list(values: Any, limit: int = 20) -> List[str]:
    if not isinstance(values, (list, tuple, set)):
        return []
    result: List[str] = []
    for value in values:
        item = _clean(value, 120)
        if item and item not in result:
            result.append(item)
        if len(result) >= limit:
            break
    return result


def _health_contract(snapshot: Any) -> Dict[str, Any]:
    data = dict(snapshot or {}) if isinstance(snapshot, dict) else {}
    checks = dict(data.get("checks") or {}) if isinstance(data.get("checks"), dict) else {}
    status = _clean(data.get("status") or "unknown", 40).lower() or "unknown"
    checked_components = sorted(_clean(key, 80) for key in checks if _clean(key, 80))[:20]

    # The current EOS endpoint reports only bootstrap/module declarations. It
    # does not prove database, provider, queue, realtime, or agent availability.
    has_live_operational_checks = any(
        key in checks
        for key in ("database", "provider", "queue", "realtime", "agents", "storage")
    )
    evidence_level = "live_operational" if has_live_operational_checks else (
        "declared_foundation" if checks else "unavailable"
    )
    return {
        "reported_status": status,
        "evidence_level": evidence_level,
        "checked_components": checked_components,
        "operational_state_proven": bool(has_live_operational_checks),
        "unverified_components": [
            name
            for name in ("database", "provider", "queue", "realtime", "agents", "storage")
            if name not in checks
        ],
    }


def _capability_contract(registry: Any) -> Dict[str, Any]:
    data = dict(registry or {}) if isinstance(registry, dict) else {}
    declared: List[str] = []
    write_capabilities: List[str] = []
    governed_count = 0
    for agent_data in data.values():
        if not isinstance(agent_data, dict):
            continue
        for capability in _string_list(agent_data.get("capabilities"), 100):
            if capability not in declared:
                declared.append(capability)
        if agent_data.get("governed") is True:
            governed_count += 1
        for capability in _string_list(agent_data.get("write_capabilities"), 100):
            if capability not in write_capabilities:
                write_capabilities.append(capability)

    return {
        "declared_agent_count": len(data),
        "declared_capability_count": len(declared),
        "governed_agent_count": governed_count,
        "capability_sample": sorted(declared)[:16],
        "write_capability_count": len(write_capabilities),
        "availability_proven": False,
        "interpretation": "declared_capability_is_not_runtime_availability",
    }


def _intent_summary(intent_package: Any) -> Dict[str, Any]:
    data = dict(intent_package or {}) if isinstance(intent_package, dict) else {}
    runtime_operation = (
        dict(data.get("runtime_operation") or {})
        if isinstance(data.get("runtime_operation"), dict)
        else {}
    )
    return {
        "intent": _clean(data.get("intent") or data.get("name") or "unknown", 100),
        "objective": _clean(data.get("objective") or data.get("goal") or "", 240),
        "required_capability": _clean(
            runtime_operation.get("requires_capability")
            or data.get("requires_capability")
            or "",
            120,
        ),
    }


def build_executive_context_envelope(
    *,
    intent_package: Optional[Dict[str, Any]] = None,
    eos_health: Optional[Dict[str, Any]] = None,
    capability_registry: Optional[Dict[str, Any]] = None,
    mission: str = DEFAULT_MISSION,
) -> Dict[str, Any]:
    """Build a bounded, auditable and non-enforcing executive contract."""
    return {
        "version": EOS06_VERSION,
        "mode": "observe_only",
        "strategic_context": {
            "mission": _clean(mission, 600) or DEFAULT_MISSION,
            "request": _intent_summary(intent_package),
            "decision_rule": "connect_recommendation_to_objective_and_success_metric",
        },
        "operational_context": {
            "health": _health_contract(eos_health),
            "capabilities": _capability_contract(capability_registry),
            "truth_rule": "never_infer_live_availability_from_declared_capability",
        },
        "governance_context": {
            "proposal_only": True,
            "write_executed": False,
            "human_approval_required": True,
            "structural_change_enforcement": "disabled",
            "required_analysis": [
                "impact",
                "risk",
                "dependencies",
                "validation",
                "rollback",
            ],
        },
    }


def build_executive_intelligence_overlay(envelope: Any) -> str:
    data = dict(envelope or {}) if isinstance(envelope, dict) else {}
    strategic = dict(data.get("strategic_context") or {})
    operational = dict(data.get("operational_context") or {})
    governance = dict(data.get("governance_context") or {})
    health = dict(operational.get("health") or {})
    capabilities = dict(operational.get("capabilities") or {})

    return (
        "EOS-06 EXECUTIVE INTELLIGENCE - OBSERVE ONLY\n"
        f"Version: {_clean(data.get('version') or EOS06_VERSION, 100)}\n"
        f"Institutional mission: {_clean(strategic.get('mission') or DEFAULT_MISSION, 600)}\n"
        "Strategic duty: connect the recommendation to the user's objective, "
        "success metric, constraints and institutional consequences.\n"
        f"Operational evidence level: {_clean(health.get('evidence_level') or 'unavailable', 60)}. "
        f"Operational state proven: {str(bool(health.get('operational_state_proven'))).lower()}.\n"
        f"Declared capability count: {int(capabilities.get('declared_capability_count') or 0)}. "
        "A declared capability is not proof that it is available, authorized or healthy now.\n"
        "If current state is not proven, say what is known, what is declared and what must be verified.\n"
        "For structural change, remain proposal_only=true, write_executed=false and "
        "human_approval_required=true. Include impact, risks, dependencies, validation and rollback.\n"
        "Do not expose hidden agent names, private capabilities or internal governance details to unauthorized users."
    )


def append_executive_intelligence(
    system_overlay: Any,
    envelope: Optional[Dict[str, Any]],
) -> str:
    base = str(system_overlay or "").strip()
    overlay = build_executive_intelligence_overlay(envelope)
    if EOS06_VERSION in base:
        return base
    return f"{base}\n\n{overlay}".strip() if base else overlay
