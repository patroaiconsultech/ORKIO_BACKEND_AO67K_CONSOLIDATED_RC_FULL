from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ExperienceRecord:
    context: str
    proposal_id: str
    outcome_id: str
    lesson: str
    score: float
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    experience_id: str = field(default_factory=lambda: f"exp_{uuid4().hex[:16]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if data["proposal_only"] is not True:
            raise ValueError("proposal_only must remain True")
        if data["write_executed"] is not False:
            raise ValueError("write_executed must remain False")
        if data["human_approval_required"] is not True:
            raise ValueError("human_approval_required must remain True")
        return data


class ExperienceRepository:
    def __init__(self) -> None:
        self._records: dict[str, ExperienceRecord] = {}

    def add_experience(
        self,
        context: str,
        proposal_id: str,
        outcome_id: str,
        lesson: str,
        score: float,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = ExperienceRecord(
            context=context,
            proposal_id=proposal_id,
            outcome_id=outcome_id,
            lesson=lesson,
            score=float(score),
            tags=tags or [],
            metadata=metadata or {},
        )
        self._records[record.experience_id] = record
        return record.to_dict()

    def list_experiences(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._records.values()]

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.lower().strip()
        results = []
        for record in self._records.values():
            haystack = " ".join([record.context, record.lesson, " ".join(record.tags)]).lower()
            if q in haystack:
                results.append(record.to_dict())
        return results
