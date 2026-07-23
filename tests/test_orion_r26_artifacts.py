from pathlib import Path
import pytest
from orion.artifacts import (
    ArtifactLineage, ArtifactStore, EvidenceArtifact, DiagnosisArtifact,
    ProposalArtifact, GovernanceArtifact, default_registry, envelope_for,
)

def context():
    return {"cycle_id":"cycle_1","correlation_id":"corr_1"}

def test_artifact_hash_store_and_tamper_detection(tmp_path):
    env = envelope_for("evidence", EvidenceArtifact("log","x","boot ok",1.0), producer="test", **context())
    default_registry().validate(env)
    store = ArtifactStore(tmp_path)
    store.save(env)
    assert store.get(env.artifact_id).payload_hash == env.payload_hash
    with pytest.raises(FileExistsError):
        store.save(env)

def test_proposal_requires_governance_safety_fields():
    proposal = ProposalArtifact(
        objective="safe patch", diagnosis_id="d1", evidence_ids=("e1",),
        affected_files=("app/main.py",), diff_preview="--- a", risk={"level":"low"},
        rollback={"strategy":"git revert"}, tests=("pytest",),
    )
    env = envelope_for("proposal", proposal, producer="test", **context())
    default_registry().validate(env)

def test_production_governance_is_forbidden():
    payload = GovernanceArtifact(
        proposal_id="p1", decision="approved_for_sandbox", reasons=("ok",),
        policy_version="1", target_environment="production",
    )
    env = envelope_for("governance", payload, producer="test", **context())
    with pytest.raises(ValueError, match="production"):
        default_registry().validate(env)

def test_lineage_requires_expected_parent_type():
    evidence = envelope_for("evidence", EvidenceArtifact("log","x","fact",1), producer="test", **context())
    diagnosis = envelope_for(
        "diagnosis", DiagnosisArtifact("cause",(evidence.artifact_id,),0.9),
        producer="test", parents=(evidence.artifact_id,), **context()
    )
    ArtifactLineage().validate(diagnosis, [evidence])
