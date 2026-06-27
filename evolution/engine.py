from __future__ import annotations

from typing import Any, Dict, List, Optional

from .confidence import ConfidenceEngine
from .evidence import EvidenceEngine
from .governance import GovernanceEngine
from .knowledge import KnowledgeEngine
from .models import Evidence, Incident, Proposal
from .planner import EvolutionPlanner
from .proposal import ProposalEngine
from .registry import EvolutionRegistry
from .simulation import SimulationEngine
from .telemetry import emit_evolution_event

OEP_001_EVOLUTION_ENGINE_VERSION = "OEP_001_EVOLUTION_ENGINE_V1"

class EvolutionEngine:
    def __init__(self, registry: Optional[EvolutionRegistry] = None) -> None:
        self.registry = registry or EvolutionRegistry()
        self.evidence = EvidenceEngine()
        self.proposals = ProposalEngine()
        self.governance = GovernanceEngine()
        self.confidence = ConfidenceEngine()
        self.simulation = SimulationEngine()
        self.knowledge = KnowledgeEngine()
        self.planner = EvolutionPlanner()

    def open_incident(self, *, title: str, description: str, severity: str = "medium", tags: Optional[List[str]] = None, owner_agent: str = "orion") -> Incident:
        incident = Incident(title=title, description=description, severity=severity, tags=tags or [], owner_agent=owner_agent)
        self.registry.add_incident(incident)
        emit_evolution_event("incident.opened", incident.to_dict())
        return incident

    def add_log_evidence(self, incident_id: str, line: str, source: str = "log") -> Evidence:
        evidence = self.evidence.from_log_line(line, source=source)
        self.registry.add_evidence(incident_id, evidence)
        emit_evolution_event("evidence.added", {"incident_id": incident_id, **evidence.to_dict()})
        return evidence

    def add_feedback_evidence(self, incident_id: str, message: str, source: str = "user") -> Evidence:
        evidence = self.evidence.from_user_feedback(message, source=source)
        self.registry.add_evidence(incident_id, evidence)
        emit_evolution_event("evidence.added", {"incident_id": incident_id, **evidence.to_dict()})
        return evidence

    def create_proposal(self, *, incident_id: str, summary: str, files: List[str], diff_preview: str = "", risk: str = "medium", confidence: float = 0.5, rollback_plan: str = "", tests: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> Proposal:
        proposal = self.proposals.create(
            incident_id=incident_id,
            summary=summary,
            files=files,
            diff_preview=diff_preview,
            risk=risk,
            confidence=confidence,
            rollback_plan=rollback_plan,
            tests=tests,
            metadata=metadata,
        )
        self.registry.add_proposal(proposal)
        emit_evolution_event("proposal.created", proposal.to_dict())
        return proposal

    def review_proposal(self, proposal_id: str, *, human_approved: bool = False, approver: str | None = None):
        proposal = self.registry.get_proposal(proposal_id)
        if not proposal:
            raise KeyError(f"proposal not found: {proposal_id}")
        decision = self.governance.review(proposal, human_approved=human_approved, approver=approver)
        emit_evolution_event("governance.reviewed", decision.to_dict())
        return decision

    def rank_proposals(self, incident_id: str):
        ranked = self.planner.rank(self.registry.list_proposals(incident_id), self.registry.list_evidence(incident_id))
        emit_evolution_event("proposal.ranked", {"incident_id": incident_id, "ranked": ranked})
        return ranked

    def knowledge_snapshot(self) -> Dict[str, Any]:
        return self.knowledge.build_component_index(list(self.registry.evidence.values()), list(self.registry.proposals.values()), list(self.registry.learnings.values()))

    def registry_snapshot(self) -> Dict[str, Any]:
        return self.registry.snapshot()
