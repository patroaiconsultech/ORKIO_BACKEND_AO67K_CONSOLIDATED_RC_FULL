from __future__ import annotations


class AutonomousPlanValidator:
    def validate(self, plan: dict) -> bool:
        if not plan.get("plan_id"):
            raise ValueError("plan_id is required")
        if not plan.get("objective"):
            raise ValueError("objective is required")
        if not plan.get("steps"):
            raise ValueError("at least one step is required")
        if plan.get("proposal_only") is not True:
            raise ValueError("proposal_only must be True")
        if plan.get("write_executed") is not False:
            raise ValueError("write_executed must be False")
        if plan.get("human_approval_required") is not True:
            raise ValueError("human_approval_required must be True")
        for step in plan["steps"]:
            if step.get("proposal_only") is not True:
                raise ValueError("step proposal_only must be True")
            if step.get("write_executed") is not False:
                raise ValueError("step write_executed must be False")
            if step.get("human_approval_required") is not True:
                raise ValueError("step human_approval_required must be True")
        return True
