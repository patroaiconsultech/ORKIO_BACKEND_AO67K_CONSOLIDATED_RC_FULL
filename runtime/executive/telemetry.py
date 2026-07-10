from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional


def _hash(value: Any) -> Optional[str]:
    text = str(value or "").strip()
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def build_safe_trace_payload(
    *,
    trace_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    intent: Optional[str] = None,
    response_origin: Optional[str] = None,
    score: Optional[int] = None,
    missing_outputs=None,
    retry_count: int = 0,
    stream_started: bool = False,
) -> Dict[str, Any]:
    return {
        "trace_id": str(trace_id or "")[:96] or None,
        "thread_id_hash": _hash(thread_id),
        "intent": str(intent or "")[:96] or None,
        "response_origin": str(response_origin or "")[:96] or None,
        "score": int(score) if score is not None else None,
        "missing_outputs": [str(x)[:64] for x in list(missing_outputs or [])[:16]],
        "retry_count": int(retry_count or 0),
        "stream_started": bool(stream_started),
    }
