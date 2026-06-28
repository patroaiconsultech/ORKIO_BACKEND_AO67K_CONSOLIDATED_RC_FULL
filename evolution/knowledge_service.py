from __future__ import annotations

from typing import Any

from evolution.knowledge_manifest import KnowledgeManifest


class KnowledgeService:
    def __init__(self, repository=None, manifest: KnowledgeManifest | None = None):
        if repository is None:
            from evolution.knowledge_repository import KnowledgeRepository
            repository = KnowledgeRepository()
        self._repository = repository
        self._manifest = manifest or KnowledgeManifest()

    def add_document(self, title: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        clean_tags = tags or []
        created = self._repository.add(title=title, content=content, tags=clean_tags)
        manifest_entry = self._manifest.register(created)
        created["manifest"] = manifest_entry
        return created

    def list_documents(self) -> list[dict[str, Any]]:
        return self._repository.list()

    def list_manifest(self) -> list[dict[str, Any]]:
        return self._manifest.list_entries()

    def validate_governance(self) -> bool:
        return self._manifest.validate_all()

    def search(self, query: str) -> list[dict[str, Any]]:
        return self._repository.search(query=query)


    def list_manifest(self) -> list[dict]:
        return self._repository.manifest_entries()

    def validate_governance(self) -> bool:
        return self._repository.validate_manifest()
