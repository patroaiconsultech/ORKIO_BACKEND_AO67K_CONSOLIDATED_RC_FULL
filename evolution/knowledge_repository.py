from __future__ import annotations

from typing import Any

from evolution.knowledge_governance import apply_knowledge_governance
from evolution.knowledge_manifest import KnowledgeManifest, KnowledgeManifestEntry
from evolution.knowledge_vault import KnowledgeVault


class KnowledgeRepository:
    def __init__(
        self,
        vault: KnowledgeVault | None = None,
        manifest: KnowledgeManifest | None = None,
    ) -> None:
        self._vault = vault or KnowledgeVault()
        self._manifest = manifest or KnowledgeManifest()

    def add(self, title: str, content: str, tags: list[str] | None = None) -> dict[str, Any]:
        doc = self._vault.add_document(title=title, content=content, tags=tags or [])
        payload = {
            "id": getattr(doc, "document_id", getattr(doc, "id", None)),
            "document_id": getattr(doc, "document_id", getattr(doc, "id", None)),
            "title": getattr(doc, "title", title),
            "content": getattr(doc, "content", content),
            "tags": getattr(doc, "tags", tags or []),
            "created_at": getattr(doc, "created_at", None),
        }
        payload = apply_knowledge_governance(payload)

        entry = KnowledgeManifestEntry(
            document_id=payload["document_id"],
            title=payload["title"],
            tags=payload["tags"],
            source=getattr(doc, "source", "manual"),
            scope=getattr(doc, "scope", "general"),
            metadata=getattr(doc, "metadata", {}) or {},
        )
        self._manifest.register(entry)
        return payload

    def list(self) -> list[dict[str, Any]]:
        docs = self._vault.list_documents()
        return [
            apply_knowledge_governance(
                {
                    "id": getattr(d, "document_id", getattr(d, "id", None)),
                    "document_id": getattr(d, "document_id", getattr(d, "id", None)),
                    "title": getattr(d, "title", ""),
                    "content": getattr(d, "content", ""),
                    "tags": getattr(d, "tags", []),
                    "created_at": getattr(d, "created_at", None),
                }
            )
            for d in docs
        ]

    def search(self, query: str) -> list[dict[str, Any]]:
        results = self._vault.search(query=query)
        return [
            apply_knowledge_governance(
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
            )
            for r in results
        ]

    def manifest_entries(self) -> list[dict[str, Any]]:
        return self._manifest.list_entries()

    def validate_manifest(self) -> bool:
        return self._manifest.validate_all()


InMemoryKnowledgeRepository = KnowledgeRepository
