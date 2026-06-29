from __future__ import annotations
from typing import Any
class RollbackGenerator:
    def generate(self, affected_modules:list[str])->dict[str,Any]:
        modules=sorted(set(affected_modules or []))
        return {"strategy":"restore_previous_version","affected_modules":modules,"steps":["Stop rollout before execution.","Restore affected files/modules from previous commit.","Run regression suite.","Confirm governance audit remains green."],"proposal_only":True,"write_executed":False,"human_approval_required":True}
