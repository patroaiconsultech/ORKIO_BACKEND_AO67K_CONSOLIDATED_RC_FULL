from __future__ import annotations

from typing import Any


def apply_knowledge_governance(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    data["proposal_only"] = True
    data["write_executed"] = False
    data["human_approval_required"] = True
    return data
