from __future__ import annotations
from dataclasses import replace
from uuid import uuid4
from .models import ApprovalRecord, ChangePackage, ChangeStatus
class ApprovalPipeline:
    def submit(self, package:ChangePackage)->ChangePackage:
        package.validate_governance(); return replace(package,status=ChangeStatus.PENDING_APPROVAL)
    def approve(self, package:ChangePackage, approver:str, reason:str="")->ChangePackage:
        package.validate_governance(); approval=ApprovalRecord(approval_id="appr_"+uuid4().hex[:16],approver=approver,decision="approved",reason=reason)
        return replace(package,approvals=[*package.approvals,approval],status=ChangeStatus.APPROVED)
    def reject(self, package:ChangePackage, approver:str, reason:str="")->ChangePackage:
        package.validate_governance(); approval=ApprovalRecord(approval_id="appr_"+uuid4().hex[:16],approver=approver,decision="rejected",reason=reason)
        return replace(package,approvals=[*package.approvals,approval],status=ChangeStatus.REJECTED)
