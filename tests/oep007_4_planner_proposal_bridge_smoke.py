from evolution.autonomous_planner import (
    AutonomousPlannerService,
    PlanDependencyGraphBuilder,
    PlannerProposalBridge,
    PlanRiskScorer,
)

planner = AutonomousPlannerService()
plan = planner.create_plan(
    objective="Create a governed planner proposal",
    context="The planner must generate a proposal package without execution.",
)

risk = PlanRiskScorer().score(plan)
graph = PlanDependencyGraphBuilder().build(plan)
proposal = PlannerProposalBridge().to_proposal(plan, risk, graph)

assert proposal["proposal_id"].startswith("ppkg_")
assert proposal["plan_id"] == plan.plan_id
assert len(proposal["evidence"]) >= 3
assert proposal["recommendation"] == "submit_for_human_review"
assert proposal["proposal_only"] is True
assert proposal["write_executed"] is False
assert proposal["human_approval_required"] is True

print("OEP007_4_PLANNER_PROPOSAL_BRIDGE_PASS")
