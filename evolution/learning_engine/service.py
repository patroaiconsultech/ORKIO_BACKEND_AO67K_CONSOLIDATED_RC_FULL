from __future__ import annotations

from typing import Any

from evolution.learning_engine.memory import LearningMemory


class LearningService:
    """
    Public service facade for OEP-006.1.

    Keeps the learning layer decoupled from proposal execution and chat runtime.
    """

    def __init__(self, memory: LearningMemory | None = None) -> None:
        self._memory = memory or LearningMemory()

    def record_experience(
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
        return self._memory.add_record(
            source_type=source_type,
            source_id=source_id,
            title=title,
            summary=summary,
            outcome=outcome,
            score=score,
            lessons=lessons,
            tags=tags,
            metadata=metadata,
        )

    def list_experiences(self) -> list[dict[str, Any]]:
        return self._memory.list_records()

    def find_by_source(self, source_id: str) -> list[dict[str, Any]]:
        return self._memory.find_by_source(source_id)

    def summarize_learning(self) -> dict[str, Any]:
        return self._memory.summarize()


learning_service = LearningService()
