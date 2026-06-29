from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ProposalApprovalWorkflow:
    """Human-gated approval state machine for OEP-005.3."""

    ALLOWED = {"draft", "submitted", "approved", "rejected"}

    def submit(self, proposal: dict[str, Any]) -> dict[str, Any]:
        data = dict(proposal)
        data["status"] = "submitted"
        data["proposal_only"] = True
        data["requires_human_approval"] = True
        data["approved_by"] = None
        data["approved_at"] = None
        return data

    def approve(self, proposal: dict[str, Any], approved_by: str) -> dict[str, Any]:
        if not approved_by:
            raise ValueError("approved_by is required")
        data = dict(proposal)
        data["status"] = "approved"
        data["proposal_only"] = True
        data["requires_human_approval"] = True
        data["approved_by"] = approved_by
        data["approved_at"] = datetime.now(timezone.utc).isoformat()
        return data

    def reject(self, proposal: dict[str, Any], reason: str) -> dict[str, Any]:
        if not reason:
            raise ValueError("reason is required")
        data = dict(proposal)
        data["status"] = "rejected"
        data["proposal_only"] = True
        data["requires_human_approval"] = True
        data["rejection_reason"] = reason
        return data
