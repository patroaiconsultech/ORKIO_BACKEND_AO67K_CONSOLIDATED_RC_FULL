from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from .models import Evidence, LearningRecord, Proposal

OEP_001_KNOWLEDGE_ENGINE_VERSION = "OEP_001_KNOWLEDGE_ENGINE_V1"

class KnowledgeEngine:
    def build_component_index(self, evidence: List[Evidence], proposals: List[Proposal], learnings: List[LearningRecord]) -> Dict[str, object]:
        components = defaultdict(lambda: {"evidence": 0, "proposals": 0, "success": 0, "regression": 0})
        for item in evidence:
            for tag in item.tags:
                components[tag]["evidence"] += 1
        for proposal in proposals:
            for file in proposal.files:
                components[self._component_from_file(file)]["proposals"] += 1
        by_id = {p.proposal_id: p for p in proposals}
        for learning in learnings:
            proposal = by_id.get(learning.proposal_id)
            comps = [self._component_from_file(f) for f in (proposal.files if proposal else [])] or ["unknown"]
            for comp in comps:
                if learning.success:
                    components[comp]["success"] += 1
                if learning.regression:
                    components[comp]["regression"] += 1
        return {"version": OEP_001_KNOWLEDGE_ENGINE_VERSION, "components": dict(components)}

    def _component_from_file(self, file: str) -> str:
        f = str(file or "").lower()
        if "appconsole" in f:
            return "appconsole"
        if "realtime" in f:
            return "realtime"
        if "backend" in f or f.endswith(".py"):
            return "backend"
        if "frontend" in f or f.endswith((".jsx", ".tsx", ".js", ".ts")):
            return "frontend"
        if "auth" in f:
            return "auth"
        return "unknown"
