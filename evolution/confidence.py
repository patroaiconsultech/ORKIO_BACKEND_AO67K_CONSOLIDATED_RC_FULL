from __future__ import annotations

from typing import Iterable

from .models import Evidence, Proposal

OEP_001_CONFIDENCE_ENGINE_VERSION = "OEP_001_CONFIDENCE_ENGINE_V1"

class ConfidenceEngine:
    def evidence_confidence(self, evidence: Iterable[Evidence]) -> float:
        items = list(evidence)
        if not items:
            return 0.0
        score = sum(max(0.0, min(1.0, i.confidence)) for i in items) / len(items)
        return round(min(1.0, score + min(0.15, len(items) * 0.015)), 4)

    def proposal_confidence(self, proposal: Proposal, evidence: Iterable[Evidence]) -> float:
        evidence_score = self.evidence_confidence(evidence)
        proposal_score = max(0.0, min(1.0, proposal.confidence))
        test_bonus = min(0.1, len(proposal.tests) * 0.02)
        rollback_bonus = 0.05 if proposal.rollback_plan else 0.0
        file_penalty = 0.08 if len(proposal.files) > 3 else 0.0
        return round(max(0.0, min(1.0, (evidence_score * 0.45) + (proposal_score * 0.45) + test_bonus + rollback_bonus - file_penalty)), 4)

    def risk_score(self, proposal: Proposal) -> float:
        base = {"low": 0.2, "medium": 0.5, "high": 0.75, "critical": 0.9}.get(str(proposal.risk or "medium").lower(), 0.5)
        file_penalty = min(0.2, max(0, len(proposal.files) - 2) * 0.04)
        rollback_penalty = 0.15 if not proposal.rollback_plan else 0.0
        return round(min(1.0, base + file_penalty + rollback_penalty), 4)
