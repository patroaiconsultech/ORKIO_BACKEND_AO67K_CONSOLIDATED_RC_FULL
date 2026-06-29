from __future__ import annotations
from typing import Any
class GovernanceAuditError(ValueError): pass
class GovernanceAudit:
    REQUIRED_FLAGS={"proposal_only":True,"write_executed":False,"human_approval_required":True}
    def audit(self, package:Any)->dict[str,Any]:
        data=package.to_dict() if hasattr(package,"to_dict") else dict(package); checks=[]
        for key,expected in self.REQUIRED_FLAGS.items():
            actual=data.get(key); checks.append({"check":key,"passed":actual is expected,"expected":expected,"actual":actual})
        checks += [{"check":"rollback_plan","passed":bool(data.get("rollback_plan"))},{"check":"validation_plan","passed":bool(data.get("validation_plan"))},{"check":"affected_modules","passed":bool(data.get("affected_modules"))}]
        passed=all(item["passed"] for item in checks)
        result={"passed":passed,"checks":checks,"proposal_only":True,"write_executed":False,"human_approval_required":True}
        if not passed: raise GovernanceAuditError(result)
        return result
