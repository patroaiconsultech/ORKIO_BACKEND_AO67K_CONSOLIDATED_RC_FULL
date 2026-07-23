import pytest
from orion.artifacts import OutcomeArtifact, envelope_for
from orion.learning import EvidenceRanker, OperationalMemory, PatternExtractor, create_snapshot

def outcome(i, success=True, regressions=()):
    payload = OutcomeArtifact(
        cycle_id=f"c{i}", proposal_id=f"p{i}", execution_id=f"x{i}",
        validation_id=f"v{i}", result="ok", success=success, regressions=regressions,
    )
    return envelope_for("outcome", payload, cycle_id=f"c{i}", correlation_id=f"r{i}", producer="test")

def test_only_outcomes_are_recorded(tmp_path):
    memory = OperationalMemory(tmp_path/"memory.jsonl")
    memory.record(outcome(1))
    assert len(memory.read_all()) == 1

def test_learning_cannot_override_policy(tmp_path):
    memory = OperationalMemory(tmp_path/"memory.jsonl")
    env = outcome(1)
    object.__setattr__(env, "payload", {**env.payload, "policy_override": True})
    with pytest.raises(ValueError, match="forbidden"):
        memory.record(env)

def test_pattern_needs_three_successful_non_regressive_samples():
    records = [{"payload": o.payload, "payload_hash": o.payload_hash} for o in [outcome(1),outcome(2),outcome(3)]]
    pattern = PatternExtractor().extract(records, root_cause_family="namespace")
    assert pattern is not None and pattern.sample_size == 3

def test_current_evidence_dominates_history():
    ranked = EvidenceRanker().rank("namespace", current_score=0.9, historical_score=0.0, snapshot_id="s1")
    assert ranked.final_score == pytest.approx(0.72)
