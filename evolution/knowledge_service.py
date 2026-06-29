from __future__ import annotations

from typing import Any


class KnowledgeService:
    def __init__(self, repository=None):
        if repository is None:
            from evolution.knowledge_repository import KnowledgeRepository
            repository = KnowledgeRepository()
        self._repository = repository

    def add_document(self, title: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        clean_tags = tags or []
        return self._repository.add(title=title, content=content, tags=clean_tags)

    def list_documents(self) -> list[dict[str, Any]]:
        return self._repository.list()

    def list_manifest(self) -> list[dict[str, Any]]:
        return self._repository.manifest_entries()

    def validate_governance(self) -> bool:
        return self._repository.validate_manifest()

    def search(self, query: str) -> list[dict[str, Any]]:
        return self._repository.search(query=query)
