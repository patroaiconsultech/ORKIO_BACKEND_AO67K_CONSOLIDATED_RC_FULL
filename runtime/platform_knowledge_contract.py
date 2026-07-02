from __future__ import annotations

"""ORKIO Platform Knowledge Contract.

Pure helper for future runtime integration. It does not read files, call network,
write to database or execute external actions. The data lives in YAML files under
platform_knowledge/ and should be loaded by an explicit caller when integration
is approved.
"""

from typing import Any, Dict, Iterable, Optional


VALID_CAPABILITY_STATUSES = {
    "production",
    "beta",
    "internal",
    "planned",
    "proposal",
    "deprecated",
    "unknown",
}


def normalize_status(value: Any) -> str:
    raw = str(value or "").strip().lower()
    return raw if raw in VALID_CAPABILITY_STATUSES else "unknown"


def public_capability_answer(capability: Dict[str, Any]) -> Dict[str, Any]:
    """Return a safe public answer contract for one capability object."""
    status = normalize_status(capability.get("status"))
    return {
        "id": str(capability.get("id") or "").strip(),
        "name": str(capability.get("name") or "").strip(),
        "status": status,
        "public_answer": str(capability.get("public_answer") or "").strip(),
        "evidence_level": str(capability.get("evidence_level") or "unknown").strip(),
        "limits": [
            str(item).strip()
            for item in (capability.get("limits") or [])
            if str(item).strip()
        ][:12],
        "truth_rule": "do_not_upgrade_status_without_registry_update",
    }


def classify_capability_availability(status: Any) -> str:
    status = normalize_status(status)
    if status == "production":
        return "available"
    if status == "beta":
        return "available_with_beta_caveat"
    if status == "internal":
        return "internal_only"
    if status == "planned":
        return "roadmap_not_available"
    if status == "proposal":
        return "concept_not_available"
    if status == "deprecated":
        return "not_recommended"
    return "requires_validation"
