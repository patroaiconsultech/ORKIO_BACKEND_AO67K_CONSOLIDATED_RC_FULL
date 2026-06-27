from __future__ import annotations

from typing import Dict, List

from .confidence import ConfidenceEngine
from .models import Evidence, Proposal
from .simulation import SimulationEngine

OEP_001_PLANNER_VERSION = "OEP_001_EVOLUTION_PLANNER_V1"

class EvolutionPlanner:
    def __init__(self) -> None:
        self.confidence = ConfidenceEngine()
        self.simulation = SimulationEngine()

    def rank(self, proposals: List[Proposal], evidence: List[Evidence]) -> List[Dict[str, object]]:
        ranked = []
        for proposal in proposals:
            confidence = self.confidence.proposal_confidence(proposal, evidence)
            risk = self.confidence.risk_score(proposal)
            score = round(max(0.0, min(1.0, confidence - (risk * 0.35))), 4)
            ranked.append({
                "proposal_id": proposal.proposal_id,
                "summary": proposal.summary,
                "confidence": confidence,
                "risk_score": risk,
                "score": score,
                "simulation": self.simulation.simulate(proposal),
            })
        return sorted(ranked, key=lambda item: item["score"], reverse=True)
