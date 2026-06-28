from __future__ import annotations

from evolution.knowledge_repository import KnowledgeRepository
from evolution.knowledge_service import KnowledgeService
from evolution.knowledge_vault import KnowledgeVault


def create_knowledge_service() -> KnowledgeService:
    vault = KnowledgeVault()
    repository = KnowledgeRepository(vault=vault)
    return KnowledgeService(repository=repository)


knowledge = create_knowledge_service()
