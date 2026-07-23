from __future__ import annotations

from typing import Any


def resolve_document_agent(turn_context: Any, fallback_agent: str = "orkio") -> str:
    """Use the immutable turn owner for document work."""
    owner = str(getattr(turn_context, "turn_owner", "") or "").strip().lower()
    requested = str(getattr(turn_context, "requested_agent", "") or "").strip().lower()

    if owner:
        return owner
    if requested:
        return requested
    return fallback_agent
