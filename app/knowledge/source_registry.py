from __future__ import annotations

from typing import Dict, List

from .schema import KnowledgeSource


class KnowledgeSourceRegistry:
    def __init__(self) -> None:
        self._sources: Dict[str, KnowledgeSource] = {}

    def register(self, source: KnowledgeSource) -> None:
        if source.source_id in self._sources:
            raise ValueError(f"Knowledge source already registered: {source.source_id}")
        self._sources[source.source_id] = source

    def get(self, source_id: str) -> KnowledgeSource | None:
        return self._sources.get(source_id)

    def all(self) -> List[KnowledgeSource]:
        return list(self._sources.values())
