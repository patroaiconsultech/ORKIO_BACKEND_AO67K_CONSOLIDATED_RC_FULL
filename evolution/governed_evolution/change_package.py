from __future__ import annotations
from typing import Any
from .diff_preview import DiffPreviewGenerator
from .models import ChangePackage, ChangeStatus, new_package_id
from .rollback import RollbackGenerator
class ChangePackageBuilder:
    def __init__(self,diff_generator:DiffPreviewGenerator|None=None,rollback_generator:RollbackGenerator|None=None)->None:
        self._diff_generator=diff_generator or DiffPreviewGenerator(); self._rollback_generator=rollback_generator or RollbackGenerator()
    def build(self,title:str,summary:str,affected_modules:list[str],proposal_id:str|None=None,plan_id:str|None=None,risk_level:str="medium",validation_plan:list[str]|None=None,metadata:dict[str,Any]|None=None)->ChangePackage:
        modules=sorted(set(affected_modules or []))
        if not modules: raise ValueError("affected_modules is required")
        package=ChangePackage(package_id=new_package_id(),title=title,summary=summary,proposal_id=proposal_id,plan_id=plan_id,affected_modules=modules,diff_preview=self._diff_generator.generate(modules,summary),rollback_plan=self._rollback_generator.generate(modules),validation_plan=validation_plan or ["py_compile","smoke","regression"],risk_level=risk_level,status=ChangeStatus.DRAFT,metadata=metadata or {})
        package.validate_governance(); return package
