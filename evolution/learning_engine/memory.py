from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class LearningMemoryRecord:
    memory_id: str
    source_type: str
    source_id: str
    title: str
    summary: str
    outcome: str = "unknown"
    score: float = 0.0
    lessons: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LearningMemory:
    """
    OEP-006.1 Learning Memory.

    In-memory repository for approved learning records.

    This module is intentionally isolated from chat, realtime, database,
    deployment and execution pipelines. It only records governed learning
    signals for future analysis.
    """

    VALID_OUTCOMES = {"unknown", "success", "failure", "partial", "rejected"}

    def __init__(self) -> None:
        self._records: dict[str, LearningMemoryRecord] = {}

    def add_record(
        self,
        *,
        source_type: str,
        source_id: str,
        title: str,
        summary: str,
        outcome: str = "unknown",
        score: float = 0.0,
        lessons: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        outcome = (outcome or "unknown").strip().lower()
        if outcome not in self.VALID_OUTCOMES:
            raise ValueError(f"invalid learning outcome: {outcome}")

        bounded_score = max(0.0, min(1.0, float(score)))

        record = LearningMemoryRecord(
            memory_id=f"lmem_{uuid4().hex[:16]}",
            source_type=str(source_type or "unknown"),
            source_id=str(source_id or ""),
            title=str(title or "").strip(),
            summary=str(summary or "").strip(),
            outcome=outcome,
            score=bounded_score,
            lessons=list(lessons or []),
            tags=list(tags or []),
            metadata=dict(metadata or {}),
            proposal_only=True,
            write_executed=False,
            human_approval_required=True,
        )

        if not record.title:
            raise ValueError("title is required")
        if not record.summary:
            raise ValueError("summary is required")
        if not record.source_id:
            raise ValueError("source_id is required")

        self._records[record.memory_id] = record
        return record.to_dict()

    def list_records(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._records.values()]

    def find_by_source(self, source_id: str) -> list[dict[str, Any]]:
        sid = str(source_id or "")
        return [record.to_dict() for record in self._records.values() if record.source_id == sid]

    def summarize(self) -> dict[str, Any]:
        records = self.list_records()
        total = len(records)
        if total == 0:
            return {"total": 0, "average_score": 0.0, "outcomes": {}}

        outcomes: dict[str, int] = {}
        for record in records:
            outcome = record["outcome"]
            outcomes[outcome] = outcomes.get(outcome, 0) + 1

        average_score = sum(float(record["score"]) for record in records) / total
        return {
            "total": total,
            "average_score": round(average_score, 4),
            "outcomes": outcomes,
        }
