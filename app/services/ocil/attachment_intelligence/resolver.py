from __future__ import annotations

from typing import Iterable, List

from ..contracts import AttachmentResolutionContract


def _normalized_unique(values: Iterable[str] | None) -> List[str]:
    result: List[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def resolve_attachments(
    *,
    message_id: str,
    thread_id: str,
    current_attachment_ids: Iterable[str] | None,
    historical_attachment_ids: Iterable[str] | None,
    explicit_historical_context_requested: bool,
) -> AttachmentResolutionContract:
    current_ids = _normalized_unique(current_attachment_ids)
    historical_ids = _normalized_unique(historical_attachment_ids)

    if not explicit_historical_context_requested:
        historical_ids = []

    if current_ids:
        reason = "current_message_binding"
        evidence_required = True
        cache_invalidated = True
    elif historical_ids:
        reason = "explicit_historical_context"
        evidence_required = True
        cache_invalidated = False
    else:
        reason = "no_attachment"
        evidence_required = False
        cache_invalidated = False

    return AttachmentResolutionContract(
        message_id=message_id,
        thread_id=thread_id,
        current_attachment_ids=current_ids,
        historical_attachment_ids=historical_ids,
        explicit_historical_context_requested=explicit_historical_context_requested,
        selection_reason=reason,
        context_isolated=True,
        cache_invalidated=cache_invalidated,
        evidence_required=evidence_required,
    )
