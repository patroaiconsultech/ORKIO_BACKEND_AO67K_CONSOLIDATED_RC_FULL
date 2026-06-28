from __future__ import annotations

from evolution.knowledge_manifest import KnowledgeManifest
from evolution.knowledge_repository import KnowledgeRepository
from evolution.knowledge_service import KnowledgeService
from evolution.knowledge_vault import KnowledgeVault


def create_knowledge_service() -> KnowledgeService:
    vault = KnowledgeVault()
    manifest = KnowledgeManifest()
    repository = KnowledgeRepository(vault=vault, manifest=manifest)
    return KnowledgeService(repository=repository)


knowledge = create_knowledge_service()
