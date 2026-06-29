from __future__ import annotations

from typing import Any

from evolution.knowledge_manifest import KnowledgeManifest
from evolution.knowledge_repository import KnowledgeRepository
from evolution.knowledge_service import KnowledgeService
from evolution.knowledge_vault import KnowledgeVault


def create_knowledge_service() -> KnowledgeService:
    manifest = KnowledgeManifest()
    vault = KnowledgeVault()
    repository = KnowledgeRepository(vault=vault, manifest=manifest)
    return KnowledgeService(repository=repository)


class KnowledgeEngine:
    """
    Backward-compatible facade required by EvolutionEngine.

    This preserves the old import contract:
        from evolution.knowledge import KnowledgeEngine

    The facade delegates to KnowledgeService and remains side-effect safe.
    """

    def __init__(self, service: KnowledgeService | None = None) -> None:
        self.service = service or create_knowledge_service()

    def add_document(self, title: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        return self.service.add_document(title=title, content=content, tags=tags)

    def list_documents(self) -> list[dict[str, Any]]:
        return self.service.list_documents()

    def search(self, query: str) -> list[dict[str, Any]]:
        return self.service.search(query=query)

    def list_manifest(self) -> list[dict[str, Any]]:
        return self.service.list_manifest()

    def validate_governance(self) -> bool:
        return self.service.validate_governance()


knowledge = create_knowledge_service()
