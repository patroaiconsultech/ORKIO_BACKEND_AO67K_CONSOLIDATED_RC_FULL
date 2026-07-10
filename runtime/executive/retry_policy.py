from __future__ import annotations

from typing import Any, Dict


def retry_is_safe(
    *,
    applies: bool,
    passed: bool,
    retry_enabled: bool,
    retry_count: int,
    stream_started: bool,
    candidate_text: Any,
) -> bool:
    return bool(
        applies
        and not passed
        and retry_enabled
        and int(retry_count or 0) < 1
        and not stream_started
        and str(candidate_text or "").strip()
    )


def build_retry_context(validation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "missing_outputs": list((validation or {}).get("missing_items") or []),
        "score": int((validation or {}).get("score") or 0),
    }
