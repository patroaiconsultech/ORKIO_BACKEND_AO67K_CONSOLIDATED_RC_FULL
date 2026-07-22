from __future__ import annotations

from typing import Any

from app.runtime.agent_registry import registry_payload
from app.runtime.capability_registry import (
    get_capability_metadata,
    get_capability_registry,
)


def canonical_agent_items() -> list[dict[str, Any]]:
    payload = registry_payload(include_internal=True)
    items = payload.get("items") or []
    return [dict(item) for item in items if isinstance(item, dict)]


def capability_records(agent_id: str) -> list[dict[str, Any]]:
    registry = get_capability_registry()
    record = registry.get(agent_id) or {}
    capabilities = record.get("capabilities") or []
    result: list[dict[str, Any]] = []
    for code in sorted({str(item).strip() for item in capabilities if str(item).strip()}):
        metadata = dict(get_capability_metadata(code) or {})
        result.append(
            {
                "code": code,
                "purpose": str(metadata.get("purpose") or ""),
                "risk_level": str(metadata.get("risk_level") or "unknown"),
                "governed": bool(metadata.get("governed", True)),
                "requires_authorization": bool(
                    metadata.get("requires_authorization", False)
                ),
                "allowed_targets": [
                    str(item)
                    for item in (metadata.get("allowed_targets") or [])
                ],
                "evidence_status": "confirmed",
            }
        )
    return result


def dependency_records(agent_id: str) -> list[str]:
    registry = get_capability_registry()
    record = registry.get(agent_id) or {}
    return sorted(
        {
            str(item).strip()
            for item in (record.get("dependencies") or [])
            if str(item).strip()
        }
    )


def knowledge_summary(agent_id: str) -> dict[str, Any]:
    """Read optional AO67C knowledge metadata without making it a hard dependency."""
    profile = None
    cards: list[dict[str, Any]] = []
    hooks: list[dict[str, Any]] = []
    import_status = "confirmed"

    try:
        from app.agents.registry import (
            collect_agent_hooks,
            collect_knowledge_cards,
            get_agent_profile,
        )

        profile = get_agent_profile(agent_id, public=False)
        cards = [
            item
            for item in collect_knowledge_cards(public=False, include_internal=True)
            if str(item.get("agent_id") or "").strip().lower() == agent_id
        ]
        hooks = [
            item
            for item in collect_agent_hooks(public=False, include_internal=True)
            if str(item.get("agent_id") or "").strip().lower() == agent_id
        ]
    except (ImportError, AttributeError):
        # Some consolidated baselines carry the knowledge package but not all
        # agent exports. The map remains available and reports partial evidence.
        import_status = "partially_confirmed"

    domains: set[str] = set()
    if isinstance(profile, dict):
        for key in ("domains", "specialties", "expertise", "domain_keywords"):
            value = profile.get(key)
            if isinstance(value, list):
                domains.update(str(item).strip() for item in value if str(item).strip())

    return {
        "profile_available": bool(profile),
        "knowledge_card_count": len(cards),
        "hook_count": len(hooks),
        "domains": sorted(domains),
        "evidence_status": (
            "confirmed"
            if (profile or cards or hooks) and import_status == "confirmed"
            else import_status if import_status != "confirmed" else "not_tested"
        ),
    }
