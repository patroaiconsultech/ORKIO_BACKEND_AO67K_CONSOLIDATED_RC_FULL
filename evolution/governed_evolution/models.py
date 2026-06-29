from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4
class ChangeStatus(str, Enum):
    DRAFT="draft"; PENDING_APPROVAL="pending_approval"; APPROVED="approved"; REJECTED="rejected"
def new_package_id()->str: return "chg_"+uuid4().hex[:16]
def now_utc()->str: return datetime.now(timezone.utc).isoformat()
@dataclass(frozen=True)
class ApprovalRecord:
    approval_id:str; approver:str; decision:str; reason:str=""; created_at:str=field(default_factory=now_utc)
    proposal_only:bool=True; write_executed:bool=False; human_approval_required:bool=True
    def to_dict(self)->dict[str,Any]: return asdict(self)
@dataclass(frozen=True)
class ChangePackage:
    package_id:str; title:str; summary:str; proposal_id:str|None=None; plan_id:str|None=None
    affected_modules:list[str]=field(default_factory=list); diff_preview:dict[str,Any]=field(default_factory=dict)
    rollback_plan:dict[str,Any]=field(default_factory=dict); validation_plan:list[str]=field(default_factory=list)
    governance_checks:list[dict[str,Any]]=field(default_factory=list); approvals:list[ApprovalRecord]=field(default_factory=list)
    risk_level:str="medium"; status:ChangeStatus=ChangeStatus.DRAFT; created_at:str=field(default_factory=now_utc)
    proposal_only:bool=True; write_executed:bool=False; human_approval_required:bool=True; metadata:dict[str,Any]=field(default_factory=dict)
    def validate_governance(self)->bool:
        if self.proposal_only is not True: raise ValueError("proposal_only must be True")
        if self.write_executed is not False: raise ValueError("write_executed must be False")
        if self.human_approval_required is not True: raise ValueError("human_approval_required must be True")
        if not self.rollback_plan: raise ValueError("rollback_plan is required")
        if not self.validation_plan: raise ValueError("validation_plan is required")
        return True
    def to_dict(self)->dict[str,Any]:
        self.validate_governance(); data=asdict(self)
        data["status"]=self.status.value if isinstance(self.status,ChangeStatus) else str(self.status)
        data["approvals"]=[a.to_dict() if hasattr(a,"to_dict") else dict(a) for a in self.approvals]
        return data
