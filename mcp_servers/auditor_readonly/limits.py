"""Limit helpers for readonly MCP tools."""

from __future__ import annotations


def clamp_limit(value: int | None, default: int, maximum: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if parsed < 1:
        return 1
    return min(parsed, maximum)


def normalize_optional_text(value: str | None, max_chars: int = 160) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized[:max_chars]
