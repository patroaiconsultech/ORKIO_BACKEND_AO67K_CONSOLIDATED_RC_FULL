# RTB-08 — Modular file upload indexing service with PDF extraction hardening
# Keeps PDF/DOCX/TXT extraction and chunk creation outside app/main.py.
# Adds multi-engine PDF fallback and explicit extraction diagnostics.

from __future__ import annotations

import io
import os
import re
import time
import uuid
import logging
from typing import Any, Dict, Optional, Tuple

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


def _is_pdf(filename: str, mime_type: Optional[str]) -> bool:
    name = (filename or "").strip().lower()
    mime = (mime_type or "").strip().lower()
    return name.endswith(".pdf") or mime == "application/pdf" or mime.endswith("/pdf")


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


def _clean_extracted_text(value: Any) -> str:
    text = str(value or "")
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def _looks_like_useful_text(text: str) -> bool:
    raw = _clean_extracted_text(text)
    if len(raw) < 80:
        return False
    letters = len(re.findall(r"[A-Za-zÀ-ÿ]", raw))
    if letters < 40:
        return False
    return (letters / max(len(raw), 1)) > 0.25


def _extract_pdf_with_pypdf(raw: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""
    parts = []
    try:
        reader = PdfReader(io.BytesIO(raw))
        for page in getattr(reader, "pages", []) or []:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                continue
    except Exception:
        logger.exception("RTB08_PDF_PYPDF_FAILED")
        return ""
    return _clean_extracted_text("\n\n".join(parts))


def _extract_pdf_with_pypdf2(raw: bytes) -> str:
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except Exception:
        return ""
    parts = []
    try:
        reader = PdfReader(io.BytesIO(raw))
        for page in getattr(reader, "pages", []) or []:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                continue
    except Exception:
        logger.exception("RTB08_PDF_PYPDF2_FAILED")
        return ""
    return _clean_extracted_text("\n\n".join(parts))


def _extract_pdf_with_pdfminer(raw: bytes) -> str:
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract_text  # type: ignore
    except Exception:
        return ""
    try:
        return _clean_extracted_text(pdfminer_extract_text(io.BytesIO(raw)) or "")
    except Exception:
        logger.exception("RTB08_PDF_PDFMINER_FAILED")
        return ""


def _extract_pdf_with_pymupdf(raw: bytes) -> str:
    try:
        import fitz  # type: ignore
    except Exception:
        return ""
    parts = []
    try:
        doc = fitz.open(stream=raw, filetype="pdf")
        for page in doc:
            try:
                parts.append(page.get_text("text") or "")
            except Exception:
                continue
        try:
            doc.close()
        except Exception:
            pass
    except Exception:
        logger.exception("RTB08_PDF_PYMUPDF_FAILED")
        return ""
    return _clean_extracted_text("\n\n".join(parts))


def _extract_pdf_printable_fallback(raw: bytes) -> str:
    """Last-resort fallback for simple PDFs containing visible text in streams.

    This is intentionally conservative: it only returns text when it looks like
    human-readable content. It is not OCR and will not recover scanned PDFs.
    """
    try:
        text = raw.decode("latin-1", errors="ignore")
    except Exception:
        return ""

    candidates = re.findall(r"[\wÀ-ÿ][\wÀ-ÿ\s,.;:()/@+\-&]{30,}", text, flags=re.UNICODE)
    cleaned = []
    for item in candidates:
        item = _clean_extracted_text(item)
        # Avoid returning PDF internals only.
        if not item:
            continue
        low = item.lower()
        if any(skip in low for skip in (" obj", " endobj", " xref", "stream", "fontdescriptor", "mediabox", "catalog")):
            continue
        if len(re.findall(r"[A-Za-zÀ-ÿ]", item)) < 20:
            continue
        cleaned.append(item)
    out = "\n".join(cleaned[:60])
    return out if _looks_like_useful_text(out) else ""


def _extract_pdf_text_multiengine(filename: str, raw: bytes, mime_type: Optional[str]) -> Tuple[str, str]:
    if not _is_pdf(filename, mime_type):
        return "", ""

    engines = [
        ("pypdf", _extract_pdf_with_pypdf),
        ("PyPDF2", _extract_pdf_with_pypdf2),
        ("pdfminer.six", _extract_pdf_with_pdfminer),
        ("PyMuPDF", _extract_pdf_with_pymupdf),
        ("printable_fallback", _extract_pdf_printable_fallback),
    ]

    for name, fn in engines:
        text = ""
        try:
            text = fn(raw)
        except Exception:
            logger.exception("RTB08_PDF_ENGINE_UNEXPECTED_FAILED engine=%s filename=%s", name, filename)
            text = ""
        text = _clean_extracted_text(text)
        if _looks_like_useful_text(text):
            logger.warning(
                "RTB08_PDF_EXTRACTION_OK engine=%s filename=%s extracted_chars=%s",
                name,
                filename,
                len(text),
            )
            return text, name

    logger.warning("RTB08_PDF_EXTRACTION_EMPTY filename=%s raw_bytes=%s", filename, len(raw or b""))
    return "", ""


def extract_text_with_fallback(filename: str, raw: bytes, mime_type: Optional[str]) -> tuple[str, int, Dict[str, Any]]:
    diagnostics: Dict[str, Any] = {
        "filename": filename,
        "mime_type": mime_type,
        "is_pdf": _is_pdf(filename, mime_type),
        "engine": None,
        "fallback_engine": None,
    }

    text_content = ""
    extracted_chars = 0

    # Prefer current extractor first to preserve existing behavior for DOCX/TXT/PDF.
    try:
        text_content, extracted_chars = extract_text(filename, raw)
        text_content = _clean_extracted_text(text_content)
        if text_content:
            diagnostics["engine"] = "app.extractors.extract_text"
    except Exception:
        logger.exception("RTB08_EXTRACT_TEXT_FAILED filename=%s", filename)
        text_content, extracted_chars = "", 0

    # RTB-08: PDF needs a stronger fallback. If app extractor returns empty,
    # try all likely installed engines before admitting extraction failure.
    if not _safe_str(text_content) and _is_pdf(filename, mime_type):
        pdf_text, engine = _extract_pdf_text_multiengine(filename, raw, mime_type)
        if pdf_text:
            text_content = pdf_text
            extracted_chars = len(pdf_text)
            diagnostics["engine"] = engine
            diagnostics["fallback_engine"] = engine

    if not _safe_str(text_content):
        fallback = _fallback_plaintext_extract(filename, raw, mime_type)
        if fallback:
            text_content = _clean_extracted_text(fallback)
            extracted_chars = len(text_content)
            diagnostics["engine"] = "plaintext_fallback"
            diagnostics["fallback_engine"] = "plaintext_fallback"
            logger.warning("RTB08_EXTRACT_TEXT_FALLBACK_OK filename=%s extracted_chars=%s", filename, extracted_chars)

    text_content = _clean_extracted_text(text_content)
    diagnostics["extracted_chars"] = int(extracted_chars or len(text_content or "") or 0)
    diagnostics["has_text"] = bool(text_content)
    return text_content, int(diagnostics["extracted_chars"]), diagnostics


def create_file_chunks(db: Session, *, org: str, file_id: str, text_content: str) -> int:
    chunk_chars = int(os.getenv("RAG_CHUNK_CHARS", "1200") or "1200")
    overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "200") or "200")
    chunk_chars = max(400, min(chunk_chars, 4000))
    overlap = max(0, min(overlap, int(chunk_chars * 0.6)))

    # Idempotent re-index: clear previous chunks for this file.
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
    diagnostics: Dict[str, Any] = {}

    try:
        log.warning("RTB08_UPLOAD_INDEXING_STARTED file_id=%s filename=%s mime_type=%s", file_id, filename, mime_type)
        text_content, extracted_chars, diagnostics = extract_text_with_fallback(filename, raw, mime_type)

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
            log.warning(
                "RTB08_UPLOAD_INDEXING_DONE file_id=%s filename=%s engine=%s extracted_chars=%s chunks_created=%s",
                file_id,
                filename,
                diagnostics.get("engine"),
                extracted_chars,
                chunks_created,
            )
        else:
            extraction_failed = True
            if f is not None:
                f.extraction_failed = True
                db.add(f)
            db.commit()
            log.warning("RTB08_UPLOAD_INDEXING_EMPTY file_id=%s filename=%s diagnostics=%s", file_id, filename, diagnostics)
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
        log.exception("RTB08_UPLOAD_INDEXING_FAILED file_id=%s filename=%s", file_id, filename)

    return {
        "file_id": file_id,
        "filename": filename,
        "text": text_content,
        "extracted_chars": int(extracted_chars or len(text_content or "") or 0),
        "chunks_created": int(chunks_created or 0),
        "has_extracted_text": bool(text_content),
        "extraction_failed": bool(extraction_failed),
        "extraction_status": "extracted" if text_content else "failed",
        "diagnostics": diagnostics,
    }
