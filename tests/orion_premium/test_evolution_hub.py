import pytest

from services.orion_premium.evolution_hub import (
    EvolutionTarget,
    build_agent_dispatch_plan,
    build_evolution_proposal,
    can_execute,
)


def _proposal():
    return build_evolution_proposal(
        title="Improve document grounding",
        objective="Prevent unsupported claims",
        evidence=[{"kind": "runtime_log", "ref": "abc"}],
        targets=[EvolutionTarget("agent", "orion", "document_analysis")],
        proposed_changes=[{"file": "main.py", "operation": "review_diff"}],
        risk="medium",
        rollback="revert commit",
        confidence=0.9,
    )


def test_proposal_is_sealed_and_proposal_only():
    proposal = _proposal()
    assert proposal.status == "proposal_only"
    assert proposal.integrity_hash
    assert can_execute(proposal, human_approved=True) is False


def test_dispatch_never_allows_execution():
    dispatch = build_agent_dispatch_plan(_proposal())
    assert dispatch["execution_allowed"] is False
    assert dispatch["mode"] == "proposal_only"


def test_evidence_is_required():
    with pytest.raises(ValueError, match="evidence_required"):
        build_evolution_proposal(
            title="x", objective="x", evidence=[],
            targets=[EvolutionTarget("agent", "a", "b")],
            proposed_changes=[{"x": 1}], risk="low", rollback="revert", confidence=0.5,
        )
