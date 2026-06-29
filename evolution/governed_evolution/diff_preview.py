from __future__ import annotations
from typing import Any
class DiffPreviewGenerator:
    def generate(self, affected_modules:list[str], summary:str="")->dict[str,Any]:
        modules=sorted(set(affected_modules or []))
        return {"files_changed":modules,"summary":summary or "No executable diff generated. Preview only.","diff_generated":False,"proposal_only":True,"write_executed":False,"human_approval_required":True}
