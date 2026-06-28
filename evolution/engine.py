from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .confidence import ConfidenceEngine
from .evidence import EvidenceEngine
from .governance import GovernanceEngine
from .knowledge import KnowledgeEngine
from .models import Evidence, ExecutionRecord, Incident, LearningRecord, Proposal
from .planner import EvolutionPlanner
from .proposal import ProposalEngine
from .registry import EvolutionRegistry
from .simulation import SimulationEngine
from .telemetry import emit_evolution_event

OEP_001_EVOLUTION_ENGINE_VERSION = "OEP_001_EVOLUTION_ENGINE_V1"
OEP_002_EVOLUTION_REGISTRY_ENGINE_VERSION = "OEP_002_EVOLUTION_REGISTRY_BACKEND_FOUNDATION_V1"


class EvolutionEngine:
    """
    Orion-facing assisted evolution kernel.

    OEP-002 keeps this engine dormant and side-effect safe:
    - opens incidents
    - attaches evidence
    - creates proposal_only proposals
    - records execution/learning outcomes
    - exports registry snapshots
    - never applies patches or writes runtime code
    """

    def __init__(self, registry: Optional[EvolutionRegistry] = None) -> None:
        self.registry = registry or EvolutionRegistry()
        self.evidence = EvidenceEngine()
        self.proposals = ProposalEngine()
        self.governance = GovernanceEngine()
        self.confidence = ConfidenceEngine()
        self.simulation = SimulationEngine()
        self.knowledge = KnowledgeEngine()
        self.planner = EvolutionPlanner()

    # ------------------------------------------------------------------
    # Incidents
    # ------------------------------------------------------------------
    def open_incident(
        self,
        *,
        title: str,
        description: str,
        severity: str = "medium",
        tags: Optional[List[str]] = None,
        owner_agent: str = "orion",
    ) -> Incident:
        incident = self.registry.create_incident(
            title=title,
            description=description,
            severity=severity,
            tags=tags or [],
            owner_agent=owner_agent,
        )
        emit_evolution_event("incident.opened", incident.to_dict())
        return incident

    def close_incident(self, incident_id: str) -> Incident:
        incident = self.registry.close_incident(incident_id)
        emit_evolution_event("incident.closed", incident.to_dict())
        return incident

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------
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

    def add_structured_evidence(
        self,
        *,
        incident_id: str,
        source: str,
        payload: Dict[str, Any],
        type: str = "other",
        confidence: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        evidence = self.registry.create_evidence(
            incident_id=incident_id,
            source=source,
            payload=payload,
            type=type,
            confidence=confidence,
            tags=tags or [],
        )
        emit_evolution_event("evidence.added", {"incident_id": incident_id, **evidence.to_dict()})
        return evidence

    # ------------------------------------------------------------------
    # Proposals
    # ------------------------------------------------------------------
    def create_proposal(
        self,
        *,
        incident_id: str,
        summary: str,
        files: List[str],
        diff_preview: str = "",
        risk: str = "medium",
        confidence: float = 0.5,
        rollback_plan: str = "",
        tests: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Proposal:
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
        if decision.allowed:
            self.registry.set_proposal_status(proposal_id, "approved", approver=approver)
        emit_evolution_event("governance.reviewed", decision.to_dict())
        return decision

    def rank_proposals(self, incident_id: str):
        ranked = self.planner.rank(self.registry.list_proposals(incident_id), self.registry.list_evidence(incident_id))
        emit_evolution_event("proposal.ranked", {"incident_id": incident_id, "ranked": ranked})
        return ranked

    # ------------------------------------------------------------------
    # Execution / Learning records
    # ------------------------------------------------------------------
    def record_execution(
        self,
        *,
        proposal_id: str,
        executed: bool = False,
        approved_by: Optional[str] = None,
        result: str = "not_executed",
        smoke_result: str = "not_run",
        rollback_executed: bool = False,
        write_executed: bool = False,
        logs: Optional[List[str]] = None,
    ) -> ExecutionRecord:
        record = self.registry.record_execution(
            proposal_id=proposal_id,
            executed=executed,
            approved_by=approved_by,
            result=result,
            smoke_result=smoke_result,
            rollback_executed=rollback_executed,
            write_executed=write_executed,
            logs=logs or [],
        )
        emit_evolution_event("execution.recorded", record.to_dict())
        return record

    def record_learning(
        self,
        *,
        proposal_id: str,
        success: bool,
        lessons: List[str],
        regression: bool = False,
        confidence_delta: float = 0.0,
    ) -> LearningRecord:
        record = self.registry.record_learning(
            proposal_id=proposal_id,
            success=success,
            lessons=lessons,
            regression=regression,
            confidence_delta=confidence_delta,
        )
        emit_evolution_event("learning.recorded", record.to_dict())
        return record

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------
    def knowledge_snapshot(self) -> Dict[str, Any]:
        return self.knowledge.build_component_index(
            list(self.registry.evidence.values()),
            list(self.registry.proposals.values()),
            list(self.registry.learnings.values()),
        )

    def registry_snapshot(self) -> Dict[str, Any]:
        return self.registry.snapshot()

    def export_registry_json(self, path: str | Path) -> Path:
        target = self.registry.export_json(path)
        emit_evolution_event("registry.exported", {"path": str(target)})
        return target
