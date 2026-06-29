from __future__ import annotations

import hashlib
import re


def normalize_conversation_text(text: str) -> str:
    """Normalize conversation text for deterministic idempotency hashing."""
    normalized = (text or "").strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def make_idempotency_key(text: str, *, prefix: str = "conv") -> str:
    """Return a stable key for a normalized conversation payload."""
    normalized = normalize_conversation_text(text)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}_{digest}"
