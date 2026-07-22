from app.services.ocil.attachment_intelligence import resolve_attachments


def test_current_message_attachment_has_precedence() -> None:
    result = resolve_attachments(
        message_id="m1",
        thread_id="t1",
        current_attachment_ids=["file-current.pdf"],
        historical_attachment_ids=["file-old.pdf"],
        explicit_historical_context_requested=False,
    )

    assert result.current_attachment_ids == ["file-current.pdf"]
    assert result.historical_attachment_ids == []
    assert result.selection_reason == "current_message_binding"
    assert result.context_isolated is True


def test_historical_attachment_requires_explicit_request() -> None:
    result = resolve_attachments(
        message_id="m2",
        thread_id="t1",
        current_attachment_ids=[],
        historical_attachment_ids=["file-old.pdf"],
        explicit_historical_context_requested=True,
    )

    assert result.historical_attachment_ids == ["file-old.pdf"]
    assert result.selection_reason == "explicit_historical_context"
