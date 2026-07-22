"""Fail-closed document grounding decision for Orion responses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from .policies import DOCUMENT_EVIDENCE_GUARD_ENABLED, SHADOW_MODE


@dataclass(frozen=True)
class DocumentGroundingDecision:
    allowed: bool
    enforced: bool
    mode: str
    reason: str
    file_count: int
    evidence_count: int
    context_chars: int
    files_used: tuple[str, ...]
    grounding_score: float

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["files_used"] = list(self.files_used)
        return payload


def _safe_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _safe_str_tuple(values: Any) -> tuple[str, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return ()
    return tuple(str(value).strip() for value in values if str(value).strip())


def evaluate_document_grounding(
    document_context: Mapping[str, Any] | None,
    *,
    enabled: bool | None = None,
    shadow_mode: bool | None = None,
) -> DocumentGroundingDecision:
    """Return a deterministic decision using the existing document-context contract."""
    context = dict(document_context or {})
    enabled = DOCUMENT_EVIDENCE_GUARD_ENABLED if enabled is None else bool(enabled)
    shadow_mode = SHADOW_MODE if shadow_mode is None else bool(shadow_mode)

    file_ids = _safe_str_tuple(context.get("file_ids"))
    files_used = _safe_str_tuple(context.get("files_used"))
    citations = context.get("citations")
    citation_count = len(citations) if isinstance(citations, list) else 0

    file_count = len(file_ids)
    evidence_count = max(
        _safe_int(context.get("file_evidence_count")),
        citation_count,
    )
    context_chars = _safe_int(context.get("file_context_chars"))
    context_injected = bool(context.get("file_context_injected"))

    extraction_proven = (
        context_injected
        and evidence_count > 0
        and context_chars > 0
    )

    if extraction_proven:
        score = min(
            1.0,
            0.50
            + min(evidence_count, 8) * 0.04
            + min(context_chars, 8000) / 8000 * 0.18,
        )
        return DocumentGroundingDecision(
            allowed=True,
            enforced=enabled and not shadow_mode,
            mode="document_evidence_based",
            reason="thread_document_evidence_available",
            file_count=file_count,
            evidence_count=evidence_count,
            context_chars=context_chars,
            files_used=files_used,
            grounding_score=round(score, 4),
        )

    if file_count > 0:
        allowed = not enabled or shadow_mode
        return DocumentGroundingDecision(
            allowed=allowed,
            enforced=enabled and not shadow_mode,
            mode="document_hypothesis_only",
            reason="file_registered_without_extracted_evidence",
            file_count=file_count,
            evidence_count=evidence_count,
            context_chars=context_chars,
            files_used=files_used,
            grounding_score=0.0,
        )

    return DocumentGroundingDecision(
        allowed=not enabled or shadow_mode,
        enforced=enabled and not shadow_mode,
        mode="no_document_attached",
        reason="no_thread_scoped_file_found",
        file_count=0,
        evidence_count=0,
        context_chars=0,
        files_used=(),
        grounding_score=0.0,
    )


def build_fail_closed_overlay(decision: DocumentGroundingDecision) -> str:
    if decision.mode == "document_evidence_based":
        return (
            "ORION PREMIUM DOCUMENT GROUNDING: evidence is available. "
            "Base factual claims on retrieved excerpts, distinguish evidence from inference, "
            "and identify remaining uncertainty."
        )
    if decision.mode == "document_hypothesis_only":
        return (
            "ORION PREMIUM DOCUMENT GROUNDING — FAIL CLOSED. "
            "A file is registered, but no extracted evidence was validated. "
            "Do not summarize, describe, critique or recommend based on the filename or expected topic. "
            "State that document content is not yet available for grounded analysis."
        )
    return (
        "ORION PREMIUM DOCUMENT GROUNDING — FAIL CLOSED. "
        "No thread-scoped file was found. Do not claim document access or analysis."
    )
