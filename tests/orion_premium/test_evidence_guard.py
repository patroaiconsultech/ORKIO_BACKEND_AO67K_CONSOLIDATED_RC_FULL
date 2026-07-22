from services.orion_premium.evidence_guard import evaluate_document_grounding


def test_allows_grounded_document_context():
    decision = evaluate_document_grounding(
        {
            "file_ids": ["f1"],
            "files_used": ["f1"],
            "citations": [{"id": "c1"}],
            "file_evidence_count": 1,
            "file_context_chars": 320,
            "file_context_injected": True,
        },
        enabled=True,
        shadow_mode=False,
    )
    assert decision.allowed is True
    assert decision.mode == "document_evidence_based"
    assert decision.grounding_score > 0


def test_blocks_registered_file_without_evidence_when_enforced():
    decision = evaluate_document_grounding(
        {
            "file_ids": ["f1"],
            "citations": [],
            "file_evidence_count": 0,
            "file_context_chars": 0,
            "file_context_injected": False,
        },
        enabled=True,
        shadow_mode=False,
    )
    assert decision.allowed is False
    assert decision.mode == "document_hypothesis_only"


def test_shadow_mode_observes_without_blocking():
    decision = evaluate_document_grounding(
        {"file_ids": ["f1"]},
        enabled=True,
        shadow_mode=True,
    )
    assert decision.allowed is True
    assert decision.enforced is False


def test_no_file_is_distinct_from_failed_extraction():
    decision = evaluate_document_grounding(
        {},
        enabled=True,
        shadow_mode=False,
    )
    assert decision.allowed is False
    assert decision.mode == "no_document_attached"
