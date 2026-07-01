from __future__ import annotations

from typing import Dict, List

from .schema import KnowledgeItem


class InMemoryKnowledgeStore:
    """Temporary store for Phase 2A.

    Production persistence should be added later behind this interface.
    """

    def __init__(self) -> None:
        self._items: Dict[str, KnowledgeItem] = {}

    def upsert(self, item: KnowledgeItem) -> KnowledgeItem:
        self._items[item.item_id] = item
        return item

    def all(self) -> List[KnowledgeItem]:
        return list(self._items.values())

    def find_by_category(self, category: str) -> List[KnowledgeItem]:
        return [item for item in self._items.values() if item.category == category]

    def search_text(self, query: str) -> List[KnowledgeItem]:
        q = query.lower()
        return [item for item in self._items.values() if q in item.content.lower()]
