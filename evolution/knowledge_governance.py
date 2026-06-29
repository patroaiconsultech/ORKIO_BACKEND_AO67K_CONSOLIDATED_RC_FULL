from __future__ import annotations

from typing import Any


REQUIRED_GOVERNANCE = {
    "proposal_only": True,
    "write_executed": False,
    "human_approval_required": True,
}


def validate_knowledge_governance(payload: dict[str, Any]) -> bool:
    for key, expected in REQUIRED_GOVERNANCE.items():
        value = payload.get(key, expected)
        if value is not expected:
            raise ValueError(f"Knowledge governance violation: {key} must be {expected}")
    return True


def apply_knowledge_governance(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    normalized.update(REQUIRED_GOVERNANCE)
    validate_knowledge_governance(normalized)
    return normalized
