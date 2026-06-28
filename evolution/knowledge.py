"""
Compatibility facade for OEP-003.

OEP-001 created a generic evolution/knowledge.py module in some workspaces.
This file safely exposes the OEP-003 Knowledge Vault contract while keeping a
small backwards-compatible KnowledgeBase alias.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .knowledge_vault import (
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeSearchResult,
    KnowledgeVault,
)


class KnowledgeBase(KnowledgeVault):
    """Backward-compatible alias for earlier evolution knowledge experiments."""

    def remember(
        self,
        title: str,
        content: str,
        *,
        source: str = "manual",
        scope: str = "general",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeDocument:
        return self.add_document(
            title=title,
            content=content,
            source=source,
            scope=scope,
            tags=tags,
            metadata=metadata,
        )

    def recall(self, query: str, *, limit: int = 5) -> List[KnowledgeSearchResult]:
        return self.search(query, limit=limit)


__all__ = [
    "KnowledgeBase",
    "KnowledgeVault",
    "KnowledgeDocument",
    "KnowledgeChunk",
    "KnowledgeSearchResult",
]
