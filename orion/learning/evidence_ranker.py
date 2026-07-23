from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RankedHypothesis:
    statement: str
    current_evidence_score: float
    historical_context_score: float
    final_score: float
    snapshot_id: str

class EvidenceRanker:
    """Current evidence always dominates historical context."""

    def rank(self, statement: str, *, current_score: float, historical_score: float, snapshot_id: str) -> RankedHypothesis:
        current = min(1.0, max(0.0, current_score))
        historical = min(1.0, max(0.0, historical_score))
        final = min(1.0, current * 0.8 + historical * 0.2)
        return RankedHypothesis(statement, current, historical, final, snapshot_id)
