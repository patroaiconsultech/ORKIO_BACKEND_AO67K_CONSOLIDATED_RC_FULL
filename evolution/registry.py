from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from .models import Evidence, ExecutionRecord, Incident, LearningRecord, Proposal

OEP_001_REGISTRY_VERSION = "OEP_001_IN_MEMORY_REGISTRY_V1"

class EvolutionRegistry:
    def __init__(self) -> None:
        self._lock = RLock()
        self.incidents: Dict[str, Incident] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.proposals: Dict[str, Proposal] = {}
        self.executions: Dict[str, ExecutionRecord] = {}
        self.learnings: Dict[str, LearningRecord] = {}

    def add_incident(self, incident: Incident) -> Incident:
        with self._lock:
            self.incidents[incident.incident_id] = incident
            return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        with self._lock:
            return self.incidents.get(incident_id)

    def list_incidents(self) -> List[Incident]:
        with self._lock:
            return list(self.incidents.values())

    def add_evidence(self, incident_id: str, evidence: Evidence) -> Evidence:
        with self._lock:
            self.evidence[evidence.evidence_id] = evidence
            incident = self.incidents.get(incident_id)
            if incident and evidence.evidence_id not in incident.evidence_ids:
                incident.evidence_ids.append(evidence.evidence_id)
                incident.touch()
            return evidence

    def list_evidence(self, incident_id: Optional[str] = None) -> List[Evidence]:
        with self._lock:
            if not incident_id:
                return list(self.evidence.values())
            incident = self.incidents.get(incident_id)
            return [self.evidence[eid] for eid in (incident.evidence_ids if incident else []) if eid in self.evidence]

    def add_proposal(self, proposal: Proposal) -> Proposal:
        with self._lock:
            self.proposals[proposal.proposal_id] = proposal
            incident = self.incidents.get(proposal.incident_id)
            if incident and proposal.proposal_id not in incident.proposal_ids:
                incident.proposal_ids.append(proposal.proposal_id)
                incident.touch()
            return proposal

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        with self._lock:
            return self.proposals.get(proposal_id)

    def list_proposals(self, incident_id: Optional[str] = None) -> List[Proposal]:
        with self._lock:
            if not incident_id:
                return list(self.proposals.values())
            return [p for p in self.proposals.values() if p.incident_id == incident_id]

    def add_execution(self, record: ExecutionRecord) -> ExecutionRecord:
        with self._lock:
            self.executions[record.execution_id] = record
            return record

    def add_learning(self, record: LearningRecord) -> LearningRecord:
        with self._lock:
            self.learnings[record.learning_id] = record
            return record

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "version": OEP_001_REGISTRY_VERSION,
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
