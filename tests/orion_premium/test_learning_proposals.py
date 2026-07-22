from services.orion_premium.learning_proposals import (
    create_learning_proposal,
    validate_learning_proposal,
)


def test_valid_learning_proposal_requires_evidence_and_approval():
    proposal = create_learning_proposal(
        key="orion.document_grounding",
        previous_value=None,
        proposed_value={"enabled": True},
        evidence_refs=["test:test_document_grounding"],
        confidence=0.95,
        approved_by="human-reviewer",
    )
    result = validate_learning_proposal(proposal)
    assert result["valid"] is True


def test_learning_without_approval_is_blocked():
    proposal = create_learning_proposal(
        key="orion.document_grounding",
        previous_value=None,
        proposed_value={"enabled": True},
        evidence_refs=["test:test_document_grounding"],
        confidence=0.95,
    )
    result = validate_learning_proposal(proposal)
    assert "human_approval_missing" in result["failures"]


def test_learning_without_evidence_is_blocked():
    proposal = create_learning_proposal(
        key="orion.document_grounding",
        previous_value=None,
        proposed_value={"enabled": True},
        evidence_refs=[],
        confidence=0.95,
        approved_by="human-reviewer",
    )
    result = validate_learning_proposal(proposal)
    assert "evidence_missing" in result["failures"]
