# RTB-07 — Realtime document bridge helpers
# Future-safe helper for routes/realtime.py. It keeps document-context injection
# out of the route/root file.

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from .document_context_service import build_thread_document_context


def append_realtime_document_context_to_instructions(
    base_instructions: str,
    *,
    db: Session,
    org: str,
    thread_id: Optional[str],
    query: str = "documento anexado",
    max_chars: int = 12000,
) -> tuple[str, Dict[str, Any]]:
    """Return instructions enriched with authorized thread document context.

    Does not raise on missing/empty context. Routes can call this before minting
    a Realtime session client secret.
    """
    base = str(base_instructions or "").strip()
    if not thread_id:
        return base, {"context_available": False, "reason": "missing_thread_id"}

    try:
        ctx = build_thread_document_context(
            db,
            org=org,
            thread_id=str(thread_id),
            query=query or "documento anexado",
            top_k=8,
        )
    except Exception as exc:
        return base, {"context_available": False, "reason": "service_error", "error_type": exc.__class__.__name__}

    block = str(ctx.get("context_block") or ctx.get("file_context_block") or "").strip()
    if not block:
        return base, {**ctx, "context_available": False}

    if max_chars and len(block) > max_chars:
        block = block[:max_chars].rstrip() + "\n\n[...contexto documental truncado para Realtime...]"

    overlay = (
        "DOCUMENT CONTEXT FOR THIS REALTIME SESSION — READONLY.\n"
        "The following evidence comes from files attached to this authorized thread. "
        "Use it when the user asks about the uploaded document. Do not claim the document "
        "is unavailable while this block is present.\n\n"
        f"{block}"
    )
    enriched = f"{base}\n\n{overlay}".strip() if base else overlay
    return enriched, {**ctx, "context_available": True}
