from evolution.autonomous_planner import AutonomousPlannerService

service = AutonomousPlannerService()
plan = service.create_plan(
    objective="Create a governed improvement plan for proposal ranking",
    context=[
        {"type": "proposal", "confidence": 0.86},
        {"type": "learning_signal", "confidence": 0.74},
    ],
)

assert plan["plan_id"].startswith("plan_")
assert plan["objective"]
assert len(plan["steps"]) >= 3
assert plan["proposal_only"] is True
assert plan["write_executed"] is False
assert plan["human_approval_required"] is True
assert all(step["proposal_only"] is True for step in plan["steps"])
assert all(step["write_executed"] is False for step in plan["steps"])
assert all(step["human_approval_required"] is True for step in plan["steps"])
assert service.validate_plan(plan) is True
assert len(service.list_plans()) == 1

print("OEP007_AUTONOMOUS_PLANNER_FOUNDATION_PASS")
