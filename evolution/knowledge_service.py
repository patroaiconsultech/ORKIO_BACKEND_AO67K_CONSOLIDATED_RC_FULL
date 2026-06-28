from __future__ import annotations

from typing import Any

from evolution.knowledge_governance import validate_knowledge_governance


class KnowledgeService:
    def __init__(self, repository=None):
        if repository is None:
            from evolution.knowledge_repository import KnowledgeRepository
            repository = KnowledgeRepository()
        self._repository = repository

    def add_document(self, title: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        clean_tags = tags or []
        created = self._repository.add(title=title, content=content, tags=clean_tags)
        validate_knowledge_governance(created)
        return created

    def list_documents(self) -> list[dict[str, Any]]:
        documents = self._repository.list()
        for document in documents:
            validate_knowledge_governance(document)
        return documents

    def search(self, query: str) -> list[dict[str, Any]]:
        results = self._repository.search(query=query)
        for result in results:
            validate_knowledge_governance(result)
        return results

    def manifest_entries(self) -> list[dict[str, Any]]:
        entries = self._repository.manifest_entries()
        for entry in entries:
            validate_knowledge_governance(entry)
        return entries

    def validate_manifest(self) -> bool:
        return self._repository.validate_manifest()
