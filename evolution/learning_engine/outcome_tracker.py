from __future__ import annotations

from evolution.learning_engine.outcome_models import OutcomeRecord


class OutcomeTracker:
    def __init__(self) -> None:
        self._outcomes: dict[str, OutcomeRecord] = {}

    def record_outcome(
        self,
        proposal_id: str,
        status: str,
        score: float,
        feedback: str = "",
        metadata: dict | None = None,
    ) -> dict:
        record = OutcomeRecord(
            proposal_id=proposal_id,
            status=status,
            score=float(score),
            feedback=feedback,
            metadata=metadata or {},
        )
        self._outcomes[record.outcome_id] = record
        return record.to_dict()

    def list_outcomes(self) -> list[dict]:
        return [record.to_dict() for record in self._outcomes.values()]

    def get_by_proposal(self, proposal_id: str) -> list[dict]:
        return [
            record.to_dict()
            for record in self._outcomes.values()
            if record.proposal_id == proposal_id
        ]

    def average_score(self) -> float:
        records = list(self._outcomes.values())
        if not records:
            return 0.0
        return sum(float(record.score) for record in records) / len(records)
