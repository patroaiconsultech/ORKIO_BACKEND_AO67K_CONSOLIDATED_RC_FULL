from __future__ import annotations

from typing import List, Optional

from .models import Proposal

OEP_001_PROPOSAL_ENGINE_VERSION = "OEP_001_PROPOSAL_ENGINE_V1"

class ProposalEngine:
    def create(
        self,
        *,
        incident_id: str,
        summary: str,
        files: List[str],
        diff_preview: str = "",
        risk: str = "medium",
        confidence: float = 0.5,
        rollback_plan: str = "",
        tests: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> Proposal:
        return Proposal(
            incident_id=incident_id,
            summary=summary,
            files=files,
            diff_preview=diff_preview,
            risk=risk,
            confidence=confidence,
            rollback_plan=rollback_plan,
            tests=tests or [],
            metadata=metadata or {},
            proposal_only=True,
            write_executed=False,
            human_approval_required=True,
            status="ready_for_review",
        )
