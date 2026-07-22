from __future__ import annotations

from typing import Iterable

from ..contracts import AttachmentResolutionContract, ExecutionProfileContract


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}


def _looks_like_image(attachment_ids: Iterable[str]) -> bool:
    for attachment_id in attachment_ids:
        lowered = attachment_id.lower()
        if any(lowered.endswith(ext) for ext in _IMAGE_EXTENSIONS):
            return True
    return False


def resolve_execution_profile(
    *,
    requested_agent: str,
    attachment_contract: AttachmentResolutionContract,
    user_intent: str,
) -> ExecutionProfileContract:
    selected_agent = (requested_agent or "orion").strip().lower()
    intent = (user_intent or "").lower()
    current_ids = attachment_contract.current_attachment_ids

    if current_ids and _looks_like_image(current_ids):
        return ExecutionProfileContract(
            requested_agent=requested_agent,
            selected_agent=selected_agent,
            execution_profile="vision_grounded",
            required_capabilities=["vision", "evidence_registry"],
            vision_required=True,
            lite_allowed=False,
            fallback_allowed=False,
            selection_reason="current_message_contains_image",
        )

    if current_ids:
        return ExecutionProfileContract(
            requested_agent=requested_agent,
            selected_agent=selected_agent,
            execution_profile="document_grounded",
            required_capabilities=[
                "document_extraction",
                "attachment_binding",
                "evidence_registry",
            ],
            document_grounding_required=True,
            lite_allowed=False,
            fallback_allowed=False,
            selection_reason="current_message_contains_document",
        )

    if any(term in intent for term in ("proposal_only", "dry-run", "dry run", "governança")):
        return ExecutionProfileContract(
            requested_agent=requested_agent,
            selected_agent=selected_agent,
            execution_profile="governed",
            required_capabilities=["proposal_builder", "decision_receipt"],
            lite_allowed=False,
            fallback_allowed=False,
            selection_reason="governed_evolution_intent",
        )

    return ExecutionProfileContract(
        requested_agent=requested_agent,
        selected_agent=selected_agent,
        execution_profile="standard",
        required_capabilities=["chat"],
        lite_allowed=True,
        fallback_allowed=True,
        selection_reason="default_standard",
    )
