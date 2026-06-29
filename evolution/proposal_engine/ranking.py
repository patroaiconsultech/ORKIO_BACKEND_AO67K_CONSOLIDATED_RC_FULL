from __future__ import annotations

from typing import Any


class ProposalRanker:
    """Deterministic proposal ranking for OEP-005.1."""

    def score(self, proposal: dict[str, Any]) -> float:
        confidence = float(proposal.get("confidence", 0.0) or 0.0)
        evidence_count = len(proposal.get("evidence", []) or [])
        risk_count = len(proposal.get("risks", []) or [])
        approval_bonus = 0.1 if proposal.get("requires_human_approval", True) is True else -1.0
        governance_bonus = 0.1 if proposal.get("proposal_only", True) is True else -1.0
        return round(confidence + (evidence_count * 0.05) - (risk_count * 0.03) + approval_bonus + governance_bonus, 4)

    def rank(self, proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []
        for proposal in proposals:
            item = dict(proposal)
            item["ranking_score"] = self.score(item)
            ranked.append(item)
        return sorted(ranked, key=lambda p: p.get("ranking_score", 0.0), reverse=True)
