from evolution.autonomous_planner.safety_gate import PlannerSafetyError, PlannerSafetyGate

gate = PlannerSafetyGate()

plan = {
    "plan_id": "plan_007_1",
    "steps": [
        {"step_id": "s1", "title": "Review proposal", "action": "review_only"},
        {"step_id": "s2", "title": "Prepare rollback", "action": "document_only"},
    ],
    "risk_level": "medium",
    "dependencies": ["OEP-007"],
    "rollback": "Discard generated plan and keep current baseline.",
}

safe_plan = gate.validate(plan)

assert safe_plan["plan_id"] == "plan_007_1"
assert safe_plan["approval_required"] is True
assert safe_plan["proposal_only"] is True
assert safe_plan["write_executed"] is False
assert safe_plan["human_approval_required"] is True
assert safe_plan["execution_allowed"] is False
assert isinstance(safe_plan["dependencies"], list)

try:
    gate.validate({"plan_id": "bad"})
    raise AssertionError("unsafe plan should fail")
except PlannerSafetyError:
    pass

print("OEP007_1_PLANNER_SAFETY_GATE_PASS")
