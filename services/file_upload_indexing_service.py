# RTB-07 — Modular file upload indexing service
# Keeps PDF/DOCX/TXT extraction and chunk creation outside app/main.py.

from __future__ import annotations

import os
import time
import uuid
import logging
from typing import Any, Dict, Optional

from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..extractors import extract_text
from ..models import File, FileText, FileChunk

logger = logging.getLogger(__name__)


def _new_id() -> str:
    return uuid.uuid4().hex


def _now_ts() -> int:
    return int(time.time())


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _fallback_plaintext_extract(filename: str, raw: bytes, mime_type: Optional[str]) -> str:
    name = (filename or "").strip().lower()
    mime = (mime_type or "").strip().lower()
    text_exts = (
        ".txt", ".md", ".markdown", ".csv", ".json", ".py", ".js", ".ts", ".jsx", ".tsx",
        ".html", ".htm", ".css", ".sql", ".xml", ".yaml", ".yml", ".log"
    )
    if not (mime.startswith("text/") or name.endswith(text_exts) or mime in {"application/json", "text/csv"}):
        return ""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(enc, errors="ignore").strip()
        except Exception:
            continue
    return ""


def extract_text_with_fallback(filename: str, raw: bytes, mime_type: Optional[str]) -> tuple[str, int]:
    text_content = ""
    extracted_chars = 0
    try:
        text_content, extracted_chars = extract_text(filename, raw)
    except Exception:
        logger.exception("RTB07_EXTRACT_TEXT_FAILED filename=%s", filename)
        text_content, extracted_chars = "", 0

    if not _safe_str(text_content):
        fallback = _fallback_plaintext_extract(filename, raw, mime_type)
        if fallback:
            text_content = fallback
            extracted_chars = len(fallback)
            logger.info("RTB07_EXTRACT_TEXT_FALLBACK_OK filename=%s extracted_chars=%s", filename, extracted_chars)

    return _safe_str(text_content), int(extracted_chars or len(_safe_str(text_content)) or 0)


def create_file_chunks(db: Session, *, org: str, file_id: str, text_content: str) -> int:
    chunk_chars = int(os.getenv("RAG_CHUNK_CHARS", "1200") or "1200")
    overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "200") or "200")
    chunk_chars = max(400, min(chunk_chars, 4000))
    overlap = max(0, min(overlap, int(chunk_chars * 0.6)))

    # Idempotent re-index: clear previous chunks/text for this file.
    try:
        db.execute(delete(FileChunk).where(FileChunk.org_slug == org, FileChunk.file_id == file_id))
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass

    text_len = len(text_content or "")
    idx = 0
    pos = 0
    created = 0
    while pos < text_len:
        end = min(text_len, pos + chunk_chars)
        chunk = (text_content[pos:end] or "").strip()
        if chunk:
            db.add(FileChunk(id=_new_id(), org_slug=org, file_id=file_id, idx=idx, content=chunk, created_at=_now_ts()))
            idx += 1
            created += 1
        if end >= text_len:
            break
        pos = max(0, end - overlap)
    return created


def index_uploaded_file_text(
    db: Session,
    *,
    org: str,
    file_id: str,
    filename: str,
    raw: bytes,
    mime_type: Optional[str] = None,
    logger_obj: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """Extract and persist FileText/FileChunk for an uploaded file.

    This function commits its own indexing transaction because upload routes in
    this codebase already commit the File row before extraction.
    """
    log = logger_obj or logger
    text_content = ""
    extracted_chars = 0
    chunks_created = 0
    extraction_failed = False

    try:
        log.info("RTB07_UPLOAD_INDEXING_STARTED file_id=%s filename=%s mime_type=%s", file_id, filename, mime_type)
        text_content, extracted_chars = extract_text_with_fallback(filename, raw, mime_type)

        # Remove old FileText for the same file if a retry happens.
        try:
            db.execute(delete(FileText).where(FileText.org_slug == org, FileText.file_id == file_id))
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

        f = db.get(File, file_id)
        if text_content:
            db.add(FileText(id=_new_id(), org_slug=org, file_id=file_id, text=text_content, extracted_chars=extracted_chars, created_at=_now_ts()))
            chunks_created = create_file_chunks(db, org=org, file_id=file_id, text_content=text_content)
            if f is not None:
                f.extraction_failed = False
                db.add(f)
            db.commit()
            log.info(
                "RTB07_UPLOAD_INDEXING_DONE file_id=%s extracted_chars=%s chunks_created=%s",
                file_id,
                extracted_chars,
                chunks_created,
            )
        else:
            extraction_failed = True
            if f is not None:
                f.extraction_failed = True
                db.add(f)
            db.commit()
            log.warning("RTB07_UPLOAD_INDEXING_EMPTY file_id=%s filename=%s", file_id, filename)
    except Exception:
        extraction_failed = True
        try:
            db.rollback()
        except Exception:
            pass
        try:
            f = db.get(File, file_id)
            if f is not None:
                f.extraction_failed = True
                db.add(f)
                db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        log.exception("RTB07_UPLOAD_INDEXING_FAILED file_id=%s filename=%s", file_id, filename)

    return {
        "file_id": file_id,
        "filename": filename,
        "text": text_content,
        "extracted_chars": int(extracted_chars or len(text_content or "") or 0),
        "chunks_created": int(chunks_created or 0),
        "has_extracted_text": bool(text_content),
        "extraction_failed": bool(extraction_failed),
        "extraction_status": "extracted" if text_content else "failed",
    }
