from __future__ import annotations

from typing import Any

from evolution.proposal_engine.approval import ProposalApprovalWorkflow
from evolution.proposal_engine.conflicts import ProposalConflictDetector
from evolution.proposal_engine.ranking import ProposalRanker


class ProposalEngineBundleService:
    """OEP-005.x modular bundle facade."""

    def __init__(self) -> None:
        self.ranker = ProposalRanker()
        self.conflicts = ProposalConflictDetector()
        self.workflow = ProposalApprovalWorkflow()

    def evaluate(self, proposals: list[dict[str, Any]]) -> dict[str, Any]:
        ranked = self.ranker.rank(proposals)
        conflicts = self.conflicts.detect(ranked)
        return {
            "ranked": ranked,
            "conflicts": conflicts,
            "proposal_only": True,
            "requires_human_approval": True,
        }
