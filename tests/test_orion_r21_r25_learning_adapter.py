from evolution.premium_pipeline import OrionPremiumEvolutionPipeline
from orion.adapters.evolution_r20_adapter import EvolutionR20Adapter
from orion.learning.evolution_memory import EvolutionMemory


def test_r20_adapter_preserves_governance_contract():
    pipeline = OrionPremiumEvolutionPipeline()
    plan = pipeline.create_plan(
        objective="adapter test",
        evidence=[],
        root_cause="test",
        files=["evolution/premium_pipeline.py"],
        diff_preview="--- a/x\n+++ b/x\n@@\n-old\n+new\n",
        rollback_strategy="git_revert",
        rollback_commands=["git revert <sha>"],
        tests=["python -m pytest"],
        branch_name="orion/adapter-test",
    )
    converted = EvolutionR20Adapter().from_r20(plan)
    assert converted.proposal_only is True
    assert converted.requires_human_approval is True
    assert converted.proposal_id == plan.proposal_id


def test_memory_is_append_only_and_blocks_policy_override(tmp_path):
    memory = EvolutionMemory(tmp_path / "memory.jsonl")
    memory.record({"proposal_id": "p1", "approved": True, "score": 92})
    assert memory.read_all()[0]["proposal_id"] == "p1"

    import pytest
    with pytest.raises(ValueError, match="forbidden_learning_fields"):
        memory.record({"proposal_id": "p2", "permissions": {"deploy": True}})
