from evolution.autonomous_planner import AutonomousPlannerService, PlanDependencyGraphBuilder

planner = AutonomousPlannerService()
plan = planner.create_plan(
    objective="Implement staged planner improvement",
    context="Create a small sequence of safe reviewable steps.",
)

builder = PlanDependencyGraphBuilder()
graph = builder.build(plan)

assert len(graph["nodes"]) >= 1
assert isinstance(graph["edges"], list)
assert graph["has_cycles"] is False
assert graph["proposal_only"] is True
assert graph["write_executed"] is False
assert graph["human_approval_required"] is True

print("OEP007_3_PLAN_DEPENDENCY_GRAPH_PASS")
