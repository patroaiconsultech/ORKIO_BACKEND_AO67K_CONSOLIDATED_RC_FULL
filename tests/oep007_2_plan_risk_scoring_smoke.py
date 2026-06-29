from evolution.autonomous_planner import AutonomousPlannerService, PlanRiskScorer

planner = AutonomousPlannerService()
plan = planner.create_plan(
    objective="Prepare production database migration safely",
    context="Need to update schema with rollback and security review.",
)

scorer = PlanRiskScorer()
result = scorer.score(plan)

assert 0.0 <= result["risk_score"] <= 1.0
assert result["risk_level"] in ("low", "medium", "high")
assert result["requires_review"] is True
assert result["rollback_required"] is True
assert result["proposal_only"] is True
assert result["write_executed"] is False
assert result["human_approval_required"] is True

print("OEP007_2_PLAN_RISK_SCORING_PASS")
