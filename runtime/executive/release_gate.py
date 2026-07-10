from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .contracts import ExecutiveReleaseResult
from .retry_policy import retry_is_safe

try:
    from ..quality import ao70_validate_response
except Exception:
    ao70_validate_response = None


def evaluate_response_for_release(
    *,
    request_text: Any,
    candidate_text: Any,
    response_control: Optional[str] = None,
    preflight: Optional[Dict[str, Any]] = None,
    response_origin: str = "provider",
    stream_started: bool = False,
    retry_enabled: bool = True,
    retry_count: int = 0,
    retry_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
) -> Dict[str, Any]:
    text = str(candidate_text or "").strip()
    applies = bool((preflight or {}).get("applies"))

    if not applies or not callable(ao70_validate_response):
        return ExecutiveReleaseResult(
            version=str((preflight or {}).get("version") or "AO72_EXECUTIVE_ENGINE_RC1_V1"),
            applies=applies,
            release=True,
            final_text=text,
            score=100,
            reason="not_applicable" if not applies else "validator_unavailable_fail_open",
        ).to_dict()

    validation = ao70_validate_response(
        request_text,
        text,
        response_control=response_control,
    )

    if bool(validation.get("passed")):
        return ExecutiveReleaseResult(
            version=str((preflight or {}).get("version")),
            applies=True,
            release=True,
            final_text=text,
            score=int(validation.get("score") or 0),
            missing_outputs=list(validation.get("missing_items") or []),
            reason="quality_threshold_met",
            validation=validation,
        ).to_dict()

    if retry_is_safe(
        applies=True,
        passed=False,
        retry_enabled=retry_enabled,
        retry_count=retry_count,
        stream_started=stream_started,
        candidate_text=text,
    ) and callable(retry_callback):
        revised = retry_callback(validation)
        revised_text = str(revised or "").strip()
        if revised_text:
            revised_validation = ao70_validate_response(
                request_text,
                revised_text,
                response_control=response_control,
            )
            # Release the best complete candidate after a single bounded retry.
            use_retry = (
                bool(revised_validation.get("passed"))
                or int(revised_validation.get("score") or 0) >= int(validation.get("score") or 0)
            )
            if use_retry:
                return ExecutiveReleaseResult(
                    version=str((preflight or {}).get("version")),
                    applies=True,
                    release=True,
                    final_text=revised_text,
                    score=int(revised_validation.get("score") or 0),
                    missing_outputs=list(revised_validation.get("missing_items") or []),
                    retry_performed=True,
                    retry_count=1,
                    reason="released_after_single_retry",
                    validation=revised_validation,
                ).to_dict()

    # Fail open to preserve production availability, but expose quality state.
    return ExecutiveReleaseResult(
        version=str((preflight or {}).get("version")),
        applies=True,
        release=True,
        final_text=text,
        score=int(validation.get("score") or 0),
        missing_outputs=list(validation.get("missing_items") or []),
        reason="released_fail_open_after_quality_check",
        validation=validation,
    ).to_dict()
