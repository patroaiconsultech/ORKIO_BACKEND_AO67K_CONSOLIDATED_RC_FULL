# ORKIO_HF_LOWERED_01_CHAT_STREAM_SPECIALIST_READONLY_GUARD
# Extracted guard for AO42C specialist readonly audit routing.
#
# PURPOSE
# Keep app/main.py acting as a thin hook while moving the mention/readonly
# routing predicate into a small runtime module.
#
# SAFETY
# - No writes.
# - No network calls.
# - No proposal creation.
# - No side effects.
# - Prevents NameError caused by stale local variable `lowered` inside main.py.

from __future__ import annotations

from typing import Any


SPECIALIST_MENTION_MARKERS = ("@orion", "@chris", "@orkio")


def normalize_chat_text(value: Any) -> str:
    """Return a safe lowercase text for lightweight router predicates."""
    return str(value or "").strip().lower()


def should_run_specialist_readonly_audit(
    *,
    readonly_audit: bool,
    normalized_text: Any = "",
) -> bool:
    """Decide whether AO42C specialist readonly audit fast-path should run.

    This replaces the inline main.py expression that referenced an undefined
    variable named `lowered`.

    The function intentionally requires `readonly_audit=True` and an explicit
    specialist @mention. It does not broaden routing behavior.
    """
    if not readonly_audit:
        return False

    lowered = normalize_chat_text(normalized_text)
    if not lowered:
        return False

    return any(marker in lowered for marker in SPECIALIST_MENTION_MARKERS)


__all__ = [
    "SPECIALIST_MENTION_MARKERS",
    "normalize_chat_text",
    "should_run_specialist_readonly_audit",
]
