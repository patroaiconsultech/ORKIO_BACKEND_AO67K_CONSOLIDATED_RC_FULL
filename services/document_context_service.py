# RTB-07 — Modular thread document context service
# Centralizes file/thread document retrieval so app/main.py and realtime routes
# remain roots/orchestrators instead of storing document logic inline.

from __future__ import annotations

import os
import re
import unicodedata
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import File, FileText, FileChunk, Message

logger = logging.getLogger(__name__)


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _dedupe_nonempty(items: Optional[Iterable[Any]] = None) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in list(items or []):
        value = _safe_str(item)
        if not value or value in seen:
            continue
        out.append(value)
        seen.add(value)
    return out


def _max_context_chars(default: int = 12000) -> int:
    try:
        value = int(os.getenv("FILE_CONTEXT_MAX_CHARS", str(default)) or str(default))
    except Exception:
        value = default
    return max(1200, min(value, 30000))


def _normalize_search(value: Any) -> str:
    text = _safe_str(value)
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.lower()).strip()


def _query_terms(query: Any) -> List[str]:
    normalized = _normalize_search(query)
    if not normalized:
        return []
    stop = {
        "para", "por", "com", "que", "uma", "uns", "das", "dos", "de", "do", "da", "no", "na", "nos", "nas",
        "the", "and", "for", "with", "from", "what", "who", "how", "meu", "minha", "curriculo", "currículo",
        "documento", "arquivo", "anexo", "anexado", "experiencia", "experiência", "resumo", "resuma", "fale",
    }
    words = re.findall(r"[\wÀ-ÿ]{4,}", normalized, flags=re.UNICODE)
    out = []
    for word in words:
        if word in stop or word in out:
            continue
        out.append(word)
    return out[:12]


def _excerpt_around_query(raw_text: str, query: Any, *, max_chars: int = 2500) -> str:
    text = _safe_str(raw_text)
    if not text:
        return ""

    max_chars = max(800, min(int(max_chars or 2500), 6000))
    normalized_text = _normalize_search(text)
    terms = _query_terms(query)

    # Prefer the earliest relevant direct term hit. This makes questions such as
    # "Companhia Hipotecaria Piratini" retrieve the CV section even when chunks
    # or embeddings are not yet available.
    best_pos: Optional[int] = None
    for term in terms:
        pos = normalized_text.find(term)
        if pos >= 0 and (best_pos is None or pos < best_pos):
            best_pos = pos

    if best_pos is None:
        excerpt = text[:max_chars].strip()
        if len(text) > len(excerpt):
            excerpt += "\n\n[...trecho inicial truncado...]"
        return excerpt

    start = max(0, best_pos - int(max_chars * 0.35))
    end = min(len(text), start + max_chars)
    # Try to start/end on whitespace boundaries for readability.
    if start > 0:
        left = text.rfind("\n", 0, start + 80)
        if left > 0 and left >= start - 500:
            start = left + 1
    if end < len(text):
        right = text.find("\n", max(start, end - 80), min(len(text), end + 500))
        if right > end:
            end = right

    excerpt = text[start:end].strip()
    prefix = "[...trecho anterior omitido...]\n" if start > 0 else ""
    suffix = "\n[...trecho posterior omitido...]" if end < len(text) else ""
    return f"{prefix}{excerpt}{suffix}".strip()


def get_thread_chat_file_ids(
    db: Session,
    *,
    org: str,
    thread_id: str,
    max_files: int = 8,
) -> List[str]:
    """Return files safely associated with the given thread.

    Accepted associations:
    - files.scope_thread_id == thread_id
    - files.thread_id == thread_id
    - files.origin_thread_id == thread_id, when present in model/schema
    - ORKIO_EVENT:file_id stored in system messages of the thread
    """
    thread_id = _safe_str(thread_id)
    org = _safe_str(org)
    if not thread_id or not org:
        return []

    limit = max(1, int(max_files or 8))
    out: List[str] = []
    seen = set()

    def _add_file_id(value: Any) -> None:
        file_id = _safe_str(value)
        if not file_id or file_id in seen or len(out) >= limit:
            return
        try:
            f = db.get(File, file_id)
            if f is not None and _safe_str(getattr(f, "org_slug", "")) != org:
                return
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
            return
        out.append(file_id)
        seen.add(file_id)

    def _query_by_column(column_name: str) -> None:
        if len(out) >= limit:
            return
        col = getattr(File, column_name, None)
        if col is None:
            return
        try:
            rows = (
                db.execute(
                    select(File.id)
                    .where(File.org_slug == org, col == thread_id)
                    .order_by(File.created_at.desc())
                    .limit(limit)
                )
                .all()
            )
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
            return
        for row in rows or []:
            try:
                _add_file_id(row[0])
            except Exception:
                pass

    for column_name in ("scope_thread_id", "thread_id", "origin_thread_id"):
        _query_by_column(column_name)

    if len(out) >= limit:
        return out[:limit]

    try:
        msg_rows = (
            db.execute(
                select(Message.content)
                .where(Message.org_slug == org, Message.thread_id == thread_id)
                .order_by(Message.created_at.desc())
                .limit(120)
            )
            .all()
        )
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        msg_rows = []

    import json
    for row in msg_rows or []:
        content = _safe_str(row[0] if isinstance(row, (tuple, list)) else row)
        if "ORKIO_EVENT:" not in content:
            continue
        raw = content.split("ORKIO_EVENT:", 1)[1].strip()
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        _add_file_id(payload.get("file_id"))
        if len(out) >= limit:
            break

    return out[:limit]


def _file_label(db: Session, file_id: str) -> str:
    try:
        f = db.get(File, file_id)
        return _safe_str(getattr(f, "filename", "")) or file_id
    except Exception:
        return file_id


def _latest_file_text(db: Session, *, org: str, file_id: str) -> str:
    try:
        ft = (
            db.execute(
                select(FileText)
                .where(FileText.org_slug == org, FileText.file_id == file_id)
                .order_by(FileText.created_at.desc())
                .limit(1)
            )
            .scalars()
            .first()
        )
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        ft = None
    return _safe_str(getattr(ft, "text", "")) if ft is not None else ""


def _chunk_citations(
    db: Session,
    *,
    org: str,
    file_id: str,
    filename: str,
    top_k: int = 6,
) -> List[Dict[str, Any]]:
    try:
        chunks = (
            db.execute(
                select(FileChunk)
                .where(FileChunk.org_slug == org, FileChunk.file_id == file_id)
                .order_by(FileChunk.idx.asc())
                .limit(max(1, int(top_k or 6)))
            )
            .scalars()
            .all()
        )
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        chunks = []

    out: List[Dict[str, Any]] = []
    for chunk in chunks or []:
        content = _safe_str(getattr(chunk, "content", ""))
        if not content:
            continue
        out.append({
            "file_id": file_id,
            "filename": filename,
            "content": content,
            "score": 0.0,
            "idx": getattr(chunk, "idx", None),
            "source": "file_chunk",
        })
    return out


def _fulltext_citation(
    db: Session,
    *,
    org: str,
    file_id: str,
    filename: str,
    query: Any,
    max_chars: int,
) -> Optional[Dict[str, Any]]:
    text = _latest_file_text(db, org=org, file_id=file_id)
    if not text:
        return None
    excerpt = _excerpt_around_query(text, query, max_chars=max_chars)
    if not excerpt:
        return None
    return {
        "file_id": file_id,
        "filename": filename,
        "content": excerpt,
        "score": 0.0,
        "idx": 0,
        "source": "file_text_query_excerpt",
        "extracted_chars": len(text),
    }


def rag_fallback_recent_chunks(
    db: Session,
    org: str,
    file_ids: Sequence[str],
    top_k: int = 6,
    *,
    query: Any = "",
) -> List[Dict[str, Any]]:
    """Return useful context even when keyword retrieval misses.

    Priority:
    1. FileText excerpt around query terms.
    2. FileChunk excerpts.
    3. Initial FileText excerpt.
    """
    ids = _dedupe_nonempty(list(file_ids or []))
    if not ids:
        return []

    out: List[Dict[str, Any]] = []
    per_file_chars = max(1400, min(int(_max_context_chars() / max(1, min(len(ids), 4))), 5000))

    for fid in ids[:4]:
        filename = _file_label(db, fid)
        full = _fulltext_citation(db, org=org, file_id=fid, filename=filename, query=query, max_chars=per_file_chars)
        if full:
            out.append(full)
            continue
        chunks = _chunk_citations(db, org=org, file_id=fid, filename=filename, top_k=top_k)
        if chunks:
            out.extend(chunks[: max(1, int(top_k or 6))])
            continue
    return out[: max(1, int(top_k or 6))]


def build_file_context_block(citations: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    files_used: List[str] = []
    evidence_blocks: List[str] = []
    evidence_count = 0

    for c in list(citations or []):
        try:
            filename = _safe_str(c.get("filename") or c.get("file_id") or "")
        except Exception:
            filename = ""
        if filename:
            files_used.append(filename)

        content = ""
        for key in ("content", "text", "excerpt", "chunk_text", "summary"):
            try:
                content = _safe_str(c.get(key))
            except Exception:
                content = ""
            if content:
                break
        if not content:
            continue

        evidence_count += 1
        label = filename or f"arquivo_{evidence_count}"
        source = _safe_str(c.get("source"))
        source_line = f"Fonte técnica: {source}\n" if source else ""
        evidence_blocks.append(f"[Arquivo: {label}]\n{source_line}{content}")

    files_used = _dedupe_nonempty(files_used)
    max_chars = _max_context_chars()
    raw_context = "\n\n".join(evidence_blocks).strip()
    if max_chars and len(raw_context) > max_chars:
        raw_context = raw_context[:max_chars].rstrip() + "\n\n[...contexto de arquivo truncado...]"

    file_context_block = ""
    if raw_context:
        file_context_block = (
            "DOCUMENTOS ANEXADOS À THREAD — CONTEXTO AUTORIZADO:\n"
            f"{raw_context}\n\n"
            "Instruções: use evidências concretas destes documentos. "
            "Não diga que não consegue acessar o anexo enquanto este bloco estiver presente. "
            "Se as evidências forem insuficientes, diga exatamente o que está confirmado e o que segue pendente."
        )

    return {
        "files_used": files_used,
        "file_context_block": file_context_block,
        "context_block": file_context_block,
        "file_context_injected": bool(file_context_block),
        "context_available": bool(file_context_block),
        "file_context_chars": len(file_context_block),
        "context_chars": len(file_context_block),
        "file_evidence_required": bool(files_used),
        "file_evidence_count": evidence_count,
    }



def _file_exists_in_org(db: Session, *, org: str, file_id: str) -> bool:
    fid = _safe_str(file_id)
    if not fid:
        return False
    try:
        f = db.get(File, fid)
        return bool(f is not None and _safe_str(getattr(f, "org_slug", "")) == _safe_str(org))
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        return False


def _file_context_diagnostic(db: Session, *, org: str, file_id: str) -> Dict[str, Any]:
    fid = _safe_str(file_id)
    out: Dict[str, Any] = {
        "file_id": fid,
        "filename": "",
        "exists": False,
        "mime_type": "",
        "extraction_failed": None,
        "has_file_text": False,
        "file_text_chars": 0,
        "chunk_count": 0,
    }
    if not fid:
        return out

    try:
        f = db.get(File, fid)
        if f is not None and _safe_str(getattr(f, "org_slug", "")) == _safe_str(org):
            out["exists"] = True
            out["filename"] = _safe_str(getattr(f, "filename", "")) or fid
            out["mime_type"] = _safe_str(getattr(f, "mime_type", ""))
            out["extraction_failed"] = bool(getattr(f, "extraction_failed", False))
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass

    try:
        text = _latest_file_text(db, org=org, file_id=fid)
        out["has_file_text"] = bool(text)
        out["file_text_chars"] = len(text or "")
    except Exception:
        pass

    try:
        out["chunk_count"] = int(
            db.execute(
                select(FileChunk.id)
                .where(FileChunk.org_slug == org, FileChunk.file_id == fid)
                .limit(500)
            ).rowcount or 0
        )
    except Exception:
        # SQLAlchemy rowcount is not reliable for SELECT across drivers; retry with materialized rows.
        try:
            rows = db.execute(
                select(FileChunk.id)
                .where(FileChunk.org_slug == org, FileChunk.file_id == fid)
                .limit(500)
            ).all()
            out["chunk_count"] = len(rows or [])
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
    return out


def load_thread_document_citations(
    db: Session,
    *,
    org: str,
    thread_id: str,
    query: str,
    top_k: int = 8,
    preferred_file_id: Optional[str] = None,
    strict_preferred_file_id: bool = False,
) -> Dict[str, Any]:
    """Load document citations for a thread.

    RTB-08 important behavior:
    When preferred_file_id is provided with strict_preferred_file_id=True, this
    function must NOT fall back to older documents in the same thread. The prior
    RTB-07 behavior could attach DOCX context after a PDF upload failed, making
    Orkio answer from the old DOCX while the user asked about the new PDF.
    """
    thread_file_ids = get_thread_chat_file_ids(db, org=org, thread_id=thread_id, max_files=12)
    preferred = _safe_str(preferred_file_id)
    preferred_in_thread = bool(preferred and preferred in set(thread_file_ids))
    preferred_exists = _file_exists_in_org(db, org=org, file_id=preferred) if preferred else False

    if preferred:
        if strict_preferred_file_id:
            # Strict means: only the selected upload may provide context.
            # If it is not associated with this thread, return no context.
            file_ids = [preferred] if preferred_in_thread else []
        else:
            if preferred_in_thread:
                file_ids = [preferred] + [fid for fid in thread_file_ids if fid != preferred]
            else:
                file_ids = list(thread_file_ids)
    else:
        file_ids = list(thread_file_ids)

    citations: List[Dict[str, Any]] = []
    retrieval_error: Optional[str] = None
    if file_ids:
        try:
            citations = rag_fallback_recent_chunks(
                db,
                org,
                file_ids,
                top_k=max(1, int(top_k or 8)),
                query=query,
            )
        except Exception as e:
            logger.exception("RTB08_DOCUMENT_FALLBACK_FAILED thread_id=%s preferred=%s", thread_id, preferred)
            retrieval_error = e.__class__.__name__
            try:
                db.rollback()
            except Exception:
                pass
            citations = []

        if not citations and not strict_preferred_file_id:
            try:
                from ..retrieval import keyword_retrieve
                citations = keyword_retrieve(
                    db,
                    org_slug=org,
                    query=query or "documento anexado",
                    top_k=max(1, int(top_k or 8)),
                    file_ids=file_ids,
                )
            except Exception as e:
                retrieval_error = e.__class__.__name__
                try:
                    db.rollback()
                except Exception:
                    pass
                citations = []

    ctx = build_file_context_block(citations)
    preferred_diag = _file_context_diagnostic(db, org=org, file_id=preferred) if preferred else {}

    if preferred and strict_preferred_file_id and not ctx.get("context_available"):
        logger.warning(
            "RTB08_DOCUMENT_CONTEXT_STRICT_EMPTY thread_id=%s file_id=%s in_thread=%s exists=%s diag=%s",
            thread_id,
            preferred,
            preferred_in_thread,
            preferred_exists,
            preferred_diag,
        )

    return {
        "file_ids": file_ids,
        "thread_file_ids": thread_file_ids,
        "preferred_file_id": preferred or None,
        "strict_preferred_file_id": bool(strict_preferred_file_id),
        "preferred_file_in_thread": bool(preferred_in_thread),
        "preferred_file_exists": bool(preferred_exists),
        "preferred_file_diagnostic": preferred_diag,
        "retrieval_error": retrieval_error,
        "citations": citations,
        "files_used": list(ctx.get("files_used") or []),
        "file_context_block": str(ctx.get("file_context_block") or ""),
        "context_block": str(ctx.get("context_block") or ""),
        "file_context_injected": bool(ctx.get("file_context_injected")),
        "context_available": bool(ctx.get("context_available")),
        "file_context_chars": int(ctx.get("file_context_chars") or 0),
        "context_chars": int(ctx.get("context_chars") or 0),
        "file_evidence_count": int(ctx.get("file_evidence_count") or 0),
    }


def build_thread_document_context(
    db: Session,
    *,
    org: str,
    thread_id: str,
    query: str = "",
    top_k: int = 8,
    preferred_file_id: Optional[str] = None,
    strict_preferred_file_id: bool = False,
) -> Dict[str, Any]:
    """Public service entrypoint for chat, realtime and debug endpoints."""
    data = load_thread_document_citations(
        db,
        org=org,
        thread_id=thread_id,
        query=query or "documento anexado",
        top_k=top_k,
        preferred_file_id=preferred_file_id,
        strict_preferred_file_id=strict_preferred_file_id,
    )
    return {
        "ok": True,
        "thread_id": thread_id,
        **data,
        "diagnostic": {
            "service": "document_context_service",
            "version": "RTB-08",
            "file_count": len(list(data.get("file_ids") or [])),
            "thread_file_count": len(list(data.get("thread_file_ids") or [])),
            "citation_count": len(list(data.get("citations") or [])),
            "context_available": bool(data.get("context_available")),
            "preferred_file_id": data.get("preferred_file_id"),
            "strict_preferred_file_id": bool(data.get("strict_preferred_file_id")),
            "preferred_file_in_thread": bool(data.get("preferred_file_in_thread")),
            "preferred_file_diagnostic": data.get("preferred_file_diagnostic") or {},
        },
    }
