from __future__ import annotations
from typing import Any
from .approval import ApprovalPipeline
from .audit import GovernanceAudit
from .change_package import ChangePackageBuilder
from .models import ChangePackage
class GovernedEvolutionService:
    def __init__(self,builder:ChangePackageBuilder|None=None,approval:ApprovalPipeline|None=None,audit:GovernanceAudit|None=None)->None:
        self._builder=builder or ChangePackageBuilder(); self._approval=approval or ApprovalPipeline(); self._audit=audit or GovernanceAudit(); self._packages:dict[str,ChangePackage]={}
    def create_package(self, **kwargs:Any)->dict[str,Any]:
        package=self._builder.build(**kwargs); self._audit.audit(package); self._packages[package.package_id]=package; return package.to_dict()
    def submit_for_approval(self, package_id:str)->dict[str,Any]:
        package=self._approval.submit(self._packages[package_id]); self._audit.audit(package); self._packages[package.package_id]=package; return package.to_dict()
    def approve(self, package_id:str, approver:str, reason:str="")->dict[str,Any]:
        package=self._approval.approve(self._packages[package_id],approver,reason); self._audit.audit(package); self._packages[package.package_id]=package; return package.to_dict()
    def list_packages(self)->list[dict[str,Any]]: return [p.to_dict() for p in self._packages.values()]
governed_evolution_service=GovernedEvolutionService()
