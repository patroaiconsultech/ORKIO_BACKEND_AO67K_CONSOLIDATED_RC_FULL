from __future__ import annotations

from typing import Any

from evolution.knowledge_vault import KnowledgeVault


class KnowledgeRepository:
    def __init__(self, vault: KnowledgeVault | None = None) -> None:
        self._vault = vault or KnowledgeVault()

    def add(self, title: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        doc = self._vault.add_document(title=title, content=content, tags=tags or [])
        return {
            "id": getattr(doc, "document_id", getattr(doc, "id", None)),
            "document_id": getattr(doc, "document_id", getattr(doc, "id", None)),
            "title": getattr(doc, "title", title),
            "content": getattr(doc, "content", content),
            "tags": getattr(doc, "tags", tags or []),
            "created_at": getattr(doc, "created_at", None),
        }

    def list(self) -> list[dict[str, Any]]:
        docs = self._vault.list_documents()
        return [
            {
                "id": getattr(d, "document_id", getattr(d, "id", None)),
                "document_id": getattr(d, "document_id", getattr(d, "id", None)),
                "title": getattr(d, "title", ""),
                "content": getattr(d, "content", ""),
                "tags": getattr(d, "tags", []),
                "created_at": getattr(d, "created_at", None),
            }
            for d in docs
        ]

    def search(self, query: str) -> list[dict[str, Any]]:
        results = self._vault.search(query=query)
        return [
            {
                "id": getattr(r, "document_id", None),
                "document_id": getattr(r, "document_id", None),
                "chunk_id": getattr(r, "chunk_id", None),
                "title": getattr(r, "title", ""),
                "content": getattr(r, "text", getattr(r, "content", "")),
                "text": getattr(r, "text", getattr(r, "content", "")),
                "score": getattr(r, "score", 0),
                "tags": getattr(r, "tags", []),
            }
            for r in results
        ]


InMemoryKnowledgeRepository = KnowledgeRepository
