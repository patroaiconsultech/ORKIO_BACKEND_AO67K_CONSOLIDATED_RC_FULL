from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class KnowledgeSearchResult:
    id: str
    title: str
    content: str
    tags: list[str]
    created_at: str | None = None


class KnowledgeService:
    """Application service for Knowledge Vault operations.

    OEP-003.1 rule: no chat/realtime/frontend coupling.
    """

    def __init__(self, repository: Any) -> None:
        self._repository = repository

    def add_document(
        self,
        title: str,
        content: str,
        tags: list[str] | None = None,
    ) -> dict:
        title = (title or "").strip()
        content = (content or "").strip()

        if not title:
            raise ValueError("knowledge document title is required")
        if not content:
            raise ValueError("knowledge document content is required")

        clean_tags = [t.strip() for t in (tags or []) if t and t.strip()]
        return self._repository.add(title=title, content=content, tags=clean_tags)

    def search(self, query: str) -> list[dict]:
        query = (query or "").strip()
        if not query:
            return []
        return self._repository.search(query=query)

    def list_documents(self) -> list[dict]:
        if hasattr(self._repository, "list_all"):
            return self._repository.list_all()
        return []
