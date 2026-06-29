from __future__ import annotations
from typing import Any
from .proposal_models import Proposal

class ProposalBuilder:
    def build(self, analysis: dict[str, Any]) -> Proposal:
        objective = str(analysis["objective"])
        return Proposal(
            title=f"Proposal: {objective[:80]}",
            summary="Deterministic proposal generated from structured ORKIO knowledge. This package is proposal-only and requires human approval.",
            recommendation=f"Review the available evidence and approve, reject, or request refinement for: {objective}",
            evidence=list(analysis["evidence"]),
            risks=list(analysis.get("risks") or []),
            confidence=float(analysis.get("confidence", 0.0)),
            source_documents=list(analysis.get("source_documents") or []),
            metadata={"oep": "005", "engine": "proposal_engine_foundation"},
        )
