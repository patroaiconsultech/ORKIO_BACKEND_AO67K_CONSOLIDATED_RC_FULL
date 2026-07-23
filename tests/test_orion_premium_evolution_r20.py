from evolution import OrionPremiumEvolutionPipeline


def _plan():
    pipeline = OrionPremiumEvolutionPipeline()
    plan = pipeline.create_plan(
        objective="Adicionar contrato controlado de evolução",
        evidence=[{"source": "test", "fact": "baseline online"}],
        root_cause="Governança incompleta entre proposta e execução",
        files=["evolution/premium_pipeline.py"],
        diff_preview="--- a/x.py\n+++ b/x.py\n@@\n-old\n+new\n",
        rollback_strategy="git_revert",
        rollback_commands=["git revert <sha>"],
        tests=["python -m pytest tests/test_orion_premium_evolution_r20.py"],
        branch_name="orion/r20-smoke",
    )
    return pipeline, plan


def test_plan_defaults_to_proposal_only():
    _, plan = _plan()
    assert plan.proposal_only is True
    assert plan.requires_human_approval is True
    assert plan.write_executed is False
    assert plan.status == "proposal_only"


def test_branch_gate_requires_simulation_and_human_approval():
    pipeline, plan = _plan()
    denied = pipeline.evaluate_branch_gate(plan)
    assert denied.allowed is False
    assert "human_approval_missing" in denied.reasons
    assert "simulation_not_passed" in denied.reasons


def test_controlled_branch_dry_run_can_be_released_after_approval(tmp_path):
    pipeline, plan = _plan()
    # No repo_root here because this is a pure contract smoke test.
    report = pipeline.simulate(plan)
    assert report.passed is True

    pipeline.approve(plan, approver="human-reviewer")
    decision = pipeline.evaluate_branch_gate(plan, requested_mode="branch_dry_run")

    assert decision.allowed is True
    assert plan.status == "branch_gate_ready"
    assert plan.write_executed is False


def test_production_is_always_blocked():
    pipeline, plan = _plan()
    pipeline.simulate(plan)
    pipeline.approve(plan, approver="human-reviewer")

    decision = pipeline.evaluate_production_gate(plan)
    assert decision.allowed is False
    assert "production_execution_forbidden" in decision.reasons
