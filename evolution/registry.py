from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from .models import (
    Evidence,
    Execution,
    ExecutionRecord,
    Incident,
    Learning,
    LearningRecord,
    Proposal,
    utc_now_iso,
)

OEP_001_REGISTRY_VERSION = "OEP_001_IN_MEMORY_REGISTRY_V1"
OEP_002_REGISTRY_VERSION = "OEP_002_EVOLUTION_REGISTRY_BACKEND_FOUNDATION_V1"


class EvolutionRegistry:
    """
    OEP-002 Evolution Registry.

    Safe backend-only registry for assisted evolution.

    Design rules:
    - proposal_only remains the default contract.
    - write_executed is never set by the registry automatically.
    - no runtime, realtime, chat or deployment side effects.
    - persistence is explicit JSON export/import only.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self.incidents: Dict[str, Incident] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.proposals: Dict[str, Proposal] = {}
        self.executions: Dict[str, ExecutionRecord] = {}
        self.learnings: Dict[str, LearningRecord] = {}

    # ---------------------------------------------------------------------
    # Incident Registry
    # ---------------------------------------------------------------------
    def add_incident(self, incident: Incident) -> Incident:
        with self._lock:
            incident.touch()
            self.incidents[incident.incident_id] = incident
            return incident

    def create_incident(
        self,
        *,
        title: str,
        description: str,
        severity: str = "medium",
        tags: Optional[List[str]] = None,
        owner_agent: str = "orion",
        status: str = "open",
    ) -> Incident:
        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            status=status,
            tags=tags or [],
            owner_agent=owner_agent,
        )
        return self.add_incident(incident)

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        with self._lock:
            return self.incidents.get(incident_id)

    def list_incidents(
        self,
        *,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        owner_agent: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Incident]:
        with self._lock:
            items = list(self.incidents.values())
            if status:
                items = [i for i in items if i.status == status]
            if severity:
                items = [i for i in items if i.severity == severity]
            if owner_agent:
                items = [i for i in items if i.owner_agent == owner_agent]
            if tag:
                items = [i for i in items if tag in (i.tags or [])]
            return items

    def update_incident_status(self, incident_id: str, status: str) -> Incident:
        with self._lock:
            incident = self._require_incident(incident_id)
            incident.status = status
            if status in {"closed", "archived"} and not incident.closed_at:
                incident.closed_at = utc_now_iso()
            incident.touch()
            return incident

    def close_incident(self, incident_id: str) -> Incident:
        return self.update_incident_status(incident_id, "closed")

    # ---------------------------------------------------------------------
    # Evidence Registry
    # ---------------------------------------------------------------------
    def add_evidence(self, incident_id: str, evidence: Evidence) -> Evidence:
        with self._lock:
            incident = self._require_incident(incident_id)
            self.evidence[evidence.evidence_id] = evidence
            if evidence.evidence_id not in incident.evidence_ids:
                incident.evidence_ids.append(evidence.evidence_id)
                incident.touch()
            return evidence

    def create_evidence(
        self,
        *,
        incident_id: str,
        source: str,
        payload: Dict[str, Any],
        type: str = "other",
        confidence: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        evidence = Evidence(
            source=source,
            payload=payload,
            type=type,
            confidence=confidence,
            tags=tags or [],
        )
        return self.add_evidence(incident_id, evidence)

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        with self._lock:
            return self.evidence.get(evidence_id)

    def list_evidence(self, incident_id: Optional[str] = None) -> List[Evidence]:
        with self._lock:
            if not incident_id:
                return list(self.evidence.values())
            incident = self.incidents.get(incident_id)
            return [self.evidence[eid] for eid in (incident.evidence_ids if incident else []) if eid in self.evidence]

    # ---------------------------------------------------------------------
    # Proposal Registry
    # ---------------------------------------------------------------------
    def add_proposal(self, proposal: Proposal) -> Proposal:
        with self._lock:
            self._require_incident(proposal.incident_id)
            proposal.proposal_only = True
            proposal.write_executed = False
            proposal.human_approval_required = True
            proposal.touch()
            self.proposals[proposal.proposal_id] = proposal
            incident = self.incidents[proposal.incident_id]
            if proposal.proposal_id not in incident.proposal_ids:
                incident.proposal_ids.append(proposal.proposal_id)
                if incident.status == "open":
                    incident.status = "proposed"
                incident.touch()
            return proposal

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
        status: str = "ready_for_review",
    ) -> Proposal:
        proposal = Proposal(
            incident_id=incident_id,
            summary=summary,
            files=files,
            diff_preview=diff_preview,
            risk=risk,
            confidence=confidence,
            rollback_plan=rollback_plan,
            tests=tests or [],
            metadata=metadata or {},
            status=status,
            proposal_only=True,
            write_executed=False,
            human_approval_required=True,
        )
        return self.add_proposal(proposal)

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        with self._lock:
            return self.proposals.get(proposal_id)

    def list_proposals(self, incident_id: Optional[str] = None, *, status: Optional[str] = None) -> List[Proposal]:
        with self._lock:
            items = list(self.proposals.values())
            if incident_id:
                items = [p for p in items if p.incident_id == incident_id]
            if status:
                items = [p for p in items if p.status == status]
            return items

    def set_proposal_status(self, proposal_id: str, status: str, *, approver: Optional[str] = None) -> Proposal:
        with self._lock:
            proposal = self._require_proposal(proposal_id)
            proposal.status = status
            if status == "approved":
                proposal.approved_by = approver
                proposal.approved_at = utc_now_iso()
            proposal.touch()
            incident = self.incidents.get(proposal.incident_id)
            if incident and status == "approved":
                incident.status = "approved"
                incident.touch()
            return proposal

    # ---------------------------------------------------------------------
    # Execution Registry
    # ---------------------------------------------------------------------
    def add_execution(self, record: ExecutionRecord) -> ExecutionRecord:
        with self._lock:
            self._require_proposal(record.proposal_id)
            # Governance invariant: registry only records; it does not execute.
            if record.write_executed and not record.executed:
                raise ValueError("write_executed=True requires executed=True")
            self.executions[record.execution_id] = record
            return record

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
        record = Execution(
            proposal_id=proposal_id,
            executed=executed,
            approved_by=approved_by,
            executed_at=utc_now_iso() if executed else None,
            result=result,
            smoke_result=smoke_result,
            rollback_executed=rollback_executed,
            write_executed=write_executed,
            logs=logs or [],
        )
        return self.add_execution(record)

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        with self._lock:
            return self.executions.get(execution_id)

    def list_executions(self, proposal_id: Optional[str] = None) -> List[ExecutionRecord]:
        with self._lock:
            items = list(self.executions.values())
            if proposal_id:
                items = [e for e in items if e.proposal_id == proposal_id]
            return items

    # ---------------------------------------------------------------------
    # Learning Registry
    # ---------------------------------------------------------------------
    def add_learning(self, record: LearningRecord) -> LearningRecord:
        with self._lock:
            self._require_proposal(record.proposal_id)
            self.learnings[record.learning_id] = record
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
        record = Learning(
            proposal_id=proposal_id,
            success=success,
            lessons=lessons,
            regression=regression,
            confidence_delta=confidence_delta,
        )
        return self.add_learning(record)

    def get_learning(self, learning_id: str) -> Optional[LearningRecord]:
        with self._lock:
            return self.learnings.get(learning_id)

    def list_learnings(self, proposal_id: Optional[str] = None) -> List[LearningRecord]:
        with self._lock:
            items = list(self.learnings.values())
            if proposal_id:
                items = [l for l in items if l.proposal_id == proposal_id]
            return items

    # ---------------------------------------------------------------------
    # Snapshots / Persistence
    # ---------------------------------------------------------------------
    def counts(self) -> Dict[str, int]:
        with self._lock:
            return {
                "incidents": len(self.incidents),
                "evidence": len(self.evidence),
                "proposals": len(self.proposals),
                "executions": len(self.executions),
                "learnings": len(self.learnings),
            }

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "version": OEP_002_REGISTRY_VERSION,
                "legacy_version": OEP_001_REGISTRY_VERSION,
                "counts": self.counts(),
                "incidents": [i.to_dict() for i in self.incidents.values()],
                "evidence": [e.to_dict() for e in self.evidence.values()],
                "proposals": [p.to_dict() for p in self.proposals.values()],
                "executions": [e.to_dict() for e in self.executions.values()],
                "learnings": [l.to_dict() for l in self.learnings.values()],
            }

    def export_json(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.snapshot(), ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    # ---------------------------------------------------------------------
    # Internals
    # ---------------------------------------------------------------------
    def _require_incident(self, incident_id: str) -> Incident:
        incident = self.incidents.get(incident_id)
        if not incident:
            raise KeyError(f"incident not found: {incident_id}")
        return incident

    def _require_proposal(self, proposal_id: str) -> Proposal:
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise KeyError(f"proposal not found: {proposal_id}")
        return proposal
