from app.services.ocil.attachment_intelligence import resolve_attachments
from app.services.ocil.execution_intelligence import resolve_execution_profile


def test_document_disables_lite() -> None:
    attachment = resolve_attachments(
        message_id="m1",
        thread_id="t1",
        current_attachment_ids=["document.pdf"],
        historical_attachment_ids=[],
        explicit_historical_context_requested=False,
    )

    result = resolve_execution_profile(
        requested_agent="orion",
        attachment_contract=attachment,
        user_intent="Analise o documento.",
    )

    assert result.execution_profile == "document_grounded"
    assert result.document_grounding_required is True
    assert result.lite_allowed is False
    assert result.fallback_allowed is False
