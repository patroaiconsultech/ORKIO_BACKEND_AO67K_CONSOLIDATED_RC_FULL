from app.services.ocil.foundation import build_shadow_decision


def test_foundation_generates_readonly_receipt(monkeypatch) -> None:
    monkeypatch.setenv("OCIL_SHADOW_ENABLED", "true")
    monkeypatch.setenv("OCIL_ATTACHMENT_ENFORCEMENT_ENABLED", "false")
    monkeypatch.setenv("OCIL_EXECUTION_ENFORCEMENT_ENABLED", "false")
    monkeypatch.setenv("OCIL_AUTONOMOUS_ACTIONS_ENABLED", "false")

    receipt = build_shadow_decision(
        message_id="m1",
        thread_id="t1",
        requested_agent="orion",
        current_attachment_ids=["current.pdf"],
        historical_attachment_ids=["old.pdf"],
        explicit_historical_context_requested=False,
        user_intent="Analise o documento atual.",
        trace_id="trace-test",
    )

    assert receipt.shadow_mode is True
    assert receipt.enforcement is False
    assert receipt.write_executed is False
    assert receipt.attachment_resolution["historical_attachment_ids"] == []
    assert receipt.execution_profile["execution_profile"] == "document_grounded"
