from __future__ import annotations
from .models import DistillationResult

class InMemoryDistillationRepository:
    def __init__(self) -> None:
        self._results: list[DistillationResult] = []

    def add(self, result: DistillationResult) -> DistillationResult:
        result.validate_governance()
        self._results.append(result)
        return result

    def list_results(self) -> list[DistillationResult]:
        return list(self._results)
