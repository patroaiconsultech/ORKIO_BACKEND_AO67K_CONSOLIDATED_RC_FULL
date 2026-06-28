from __future__ import annotations

from evolution.knowledge_vault import KnowledgeVault
from evolution.knowledge_repository import InMemoryKnowledgeRepository
from evolution.knowledge_service import KnowledgeService
from evolution.knowledge_manifest import KNOWLEDGE_MODULE_MANIFEST


def create_knowledge_service() -> KnowledgeService:
    vault = KnowledgeVault()
    repository = InMemoryKnowledgeRepository(vault=vault)
    return KnowledgeService(repository=repository)


knowledge = create_knowledge_service()

__all__ = [
    "knowledge",
    "create_knowledge_service",
    "KnowledgeService",
    "KNOWLEDGE_MODULE_MANIFEST",
]
