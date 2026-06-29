"""
OEP-003 — Knowledge Vault

Backend-only foundation for structured knowledge storage, indexing and search.

Design constraints:
- No runtime/chat/realtime/voice integration.
- No external dependencies.
- No automatic production writes.
- Safe defaults: proposal_only=True, write_executed=False,
  human_approval_required=True.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple
from uuid import uuid4


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ0-9_]{2,}", re.UNICODE)


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [token.lower() for token in _TOKEN_RE.findall(text)]


@dataclass
class KnowledgeDocument:
    title: str
    content: str
    source: str = "manual"
    scope: str = "general"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    document_id: str = field(default_factory=lambda: _new_id("kdoc"))
    created_at: str = field(default_factory=_utcnow)
    updated_at: str = field(default_factory=_utcnow)
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True


@dataclass
class KnowledgeChunk:
    document_id: str
    text: str
    chunk_index: int
    tokens: List[str]
    source: str = "manual"
    scope: str = "general"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_id: str = field(default_factory=lambda: _new_id("kchunk"))
    created_at: str = field(default_factory=_utcnow)


@dataclass
class KnowledgeSearchResult:
    document_id: str
    chunk_id: str
    title: str
    text: str
    score: float
    source: str
    scope: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeVault:
    """
    Small, deterministic Knowledge Vault.

    It intentionally starts with an in-memory index plus optional JSON snapshot
    persistence. This keeps OEP-003 safe and decoupled while preparing the
    contract for future embeddings/vector search.
    """

    def __init__(
        self,
        storage_path: Optional[str | Path] = None,
        *,
        chunk_size: int = 180,
        chunk_overlap: int = 30,
    ) -> None:
        if chunk_size < 20:
            raise ValueError("chunk_size must be >= 20")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

        self.storage_path = Path(storage_path) if storage_path else None
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents: Dict[str, KnowledgeDocument] = {}
        self.chunks: Dict[str, KnowledgeChunk] = {}
        self._inverted_index: Dict[str, Dict[str, int]] = {}

        if self.storage_path and self.storage_path.exists():
            self.load()

    def add_document(
        self,
        *,
        title: str,
        content: str,
        source: str = "manual",
        scope: str = "general",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeDocument:
        if not title or not title.strip():
            raise ValueError("title is required")
        if not content or not content.strip():
            raise ValueError("content is required")

        document = KnowledgeDocument(
            title=title.strip(),
            content=content.strip(),
            source=source,
            scope=scope,
            tags=list(tags or []),
            metadata=dict(metadata or {}),
        )
        self.documents[document.document_id] = document
        self._index_document(document)

        return document

    def get_document(self, document_id: str) -> Optional[KnowledgeDocument]:
        return self.documents.get(document_id)

    def list_documents(self, *, scope: Optional[str] = None) -> List[KnowledgeDocument]:
        docs = list(self.documents.values())
        if scope:
            docs = [doc for doc in docs if doc.scope == scope]
        return sorted(docs, key=lambda doc: doc.created_at)

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        scope: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[KnowledgeSearchResult]:
        if limit <= 0:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        requested_tags = set(tags or [])
        total_chunks = max(len(self.chunks), 1)
        scored: List[Tuple[float, KnowledgeChunk]] = []

        for chunk in self.chunks.values():
            if scope and chunk.scope != scope:
                continue
            if requested_tags and not requested_tags.intersection(set(chunk.tags)):
                continue

            token_counts: Dict[str, int] = {}
            for token in chunk.tokens:
                token_counts[token] = token_counts.get(token, 0) + 1

            score = 0.0
            for token in query_tokens:
                tf = token_counts.get(token, 0)
                if not tf:
                    continue
                doc_freq = len(self._inverted_index.get(token, {})) or 1
                idf = math.log((1 + total_chunks) / (1 + doc_freq)) + 1
                score += (1 + math.log(tf)) * idf

            # Small exact phrase boost without depending on embeddings.
            if query.lower().strip() in chunk.text.lower():
                score += 2.5

            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)

        results: List[KnowledgeSearchResult] = []
        for score, chunk in scored[:limit]:
            doc = self.documents[chunk.document_id]
            results.append(
                KnowledgeSearchResult(
                    document_id=doc.document_id,
                    chunk_id=chunk.chunk_id,
                    title=doc.title,
                    text=chunk.text,
                    score=round(score, 6),
                    source=chunk.source,
                    scope=chunk.scope,
                    tags=list(chunk.tags),
                    metadata=dict(chunk.metadata),
                )
            )
        return results

    def snapshot(self, *, write_executed: bool = False) -> Dict[str, Any]:
        return {
            "schema": "oep003_knowledge_vault_v1",
            "generated_at": _utcnow(),
            "proposal_only": True,
            "write_executed": bool(write_executed),
            "human_approval_required": True,
            "documents": [asdict(doc) for doc in self.list_documents()],
            "chunks": [asdict(chunk) for chunk in self.chunks.values()],
        }

    def save(self) -> None:
        if not self.storage_path:
            raise ValueError("storage_path is not configured")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(self.snapshot(write_executed=True), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> None:
        if not self.storage_path:
            raise ValueError("storage_path is not configured")
        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self.documents.clear()
        self.chunks.clear()
        self._inverted_index.clear()

        for item in raw.get("documents", []):
            doc = KnowledgeDocument(**item)
            self.documents[doc.document_id] = doc

        for item in raw.get("chunks", []):
            chunk = KnowledgeChunk(**item)
            self.chunks[chunk.chunk_id] = chunk
            self._index_chunk(chunk)

    def _index_document(self, document: KnowledgeDocument) -> None:
        chunks = self._chunk_text(document.content)
        for idx, text in enumerate(chunks):
            chunk = KnowledgeChunk(
                document_id=document.document_id,
                text=text,
                chunk_index=idx,
                tokens=_tokenize(text),
                source=document.source,
                scope=document.scope,
                tags=list(document.tags),
                metadata=dict(document.metadata),
            )
            self.chunks[chunk.chunk_id] = chunk
            self._index_chunk(chunk)

    def _index_chunk(self, chunk: KnowledgeChunk) -> None:
        counts: Dict[str, int] = {}
        for token in chunk.tokens:
            counts[token] = counts.get(token, 0) + 1
        for token, count in counts.items():
            self._inverted_index.setdefault(token, {})[chunk.chunk_id] = count

    def _chunk_text(self, text: str) -> List[str]:
        tokens = text.split()
        if not tokens:
            return []

        chunks: List[str] = []
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunks.append(" ".join(tokens[start:end]))
            if end >= len(tokens):
                break
            start = max(end - self.chunk_overlap, start + 1)
        return chunks


__all__ = [
    "KnowledgeDocument",
    "KnowledgeChunk",
    "KnowledgeSearchResult",
    "KnowledgeVault",
]
