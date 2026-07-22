from __future__ import annotations

from typing import Iterable
from uuid import uuid4

from .attachment_intelligence import resolve_attachments
from .contracts import ArchitectureContract
from .execution_intelligence import resolve_execution_profile
from .feature_flags import OCILFeatureFlags
from .receipts import DecisionReceipt
from .security import authority_for_agent, evaluate_capability_boundary


def build_shadow_decision(
    *,
    message_id: str,
    thread_id: str,
    requested_agent: str,
    current_attachment_ids: Iterable[str] | None,
    historical_attachment_ids: Iterable[str] | None,
    explicit_historical_context_requested: bool,
    user_intent: str,
    trace_id: str | None = None,
) -> DecisionReceipt:
    flags = OCILFeatureFlags.from_env()
    architecture = ArchitectureContract()

    attachment = resolve_attachments(
        message_id=message_id,
        thread_id=thread_id,
        current_attachment_ids=current_attachment_ids,
        historical_attachment_ids=historical_attachment_ids,
        explicit_historical_context_requested=explicit_historical_context_requested,
    )

    execution = resolve_execution_profile(
        requested_agent=requested_agent,
        attachment_contract=attachment,
        user_intent=user_intent,
    )

    authority = authority_for_agent(execution.selected_agent)
    boundary = evaluate_capability_boundary(
        authority=authority,
        execution=execution,
        flags=flags,
    )

    divergences = []
    if attachment.current_attachment_ids and execution.lite_allowed:
        divergences.append("document_or_image_must_not_use_lite_profile")
    if execution.selected_agent == "chris" and execution.execution_profile == "governed":
        divergences.append("agent_authority_mismatch")

    return DecisionReceipt(
        trace_id=trace_id or f"trace_{uuid4().hex}",
        message_id=message_id,
        thread_id=thread_id,
        architecture=architecture.to_dict(),
        attachment_resolution=attachment.to_dict(),
        execution_profile=execution.to_dict(),
        agent_authority={
            **authority.to_dict(),
            "effective_capabilities": boundary.allowed_capabilities,
            "boundary_reason": boundary.reason,
            "execution_allowed": boundary.execution_allowed,
        },
        blocked_actions=boundary.blocked_actions,
        divergences=divergences,
        shadow_mode=flags.shadow_enabled,
        enforcement=(
            flags.attachment_enforcement_enabled
            or flags.execution_enforcement_enabled
        ),
        write_executed=False,
    )
