from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Callable, Optional

from .adapters import canonical_agent_items, capability_records, dependency_records, knowledge_summary
from .contracts import (
    AgentCapability, AgentEvolutionSnapshot, AgentGap, AgentHealth, AgentIdentity,
    AgentKnowledgeSummary, EvolutionEvidence, PolicyResolution,
)

CONTRACT_VERSION = "ORKIO_AGENT_EVOLUTION_MAP_R2.0_PREMIUM"
SCHEMA_VERSION = "agent_evolution_snapshot.v2"
MEASUREMENT_POLICY_VERSION = "agent_evolution_readonly_policy.v2"

def _fingerprint(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class AgentEvolutionMapService:
    """Read-only composition service. It owns no state and performs no writes."""

    def __init__(self, *, now_fn: Callable[[], int] | None = None) -> None:
        self._now_fn = now_fn or (lambda: int(time.time()))

    def list_agent_ids(self) -> list[str]:
        return sorted({
            str(item.get("slug") or "").strip().lower()
            for item in canonical_agent_items()
            if str(item.get("slug") or "").strip()
        })

    def _identity(self, item: dict[str, Any]) -> AgentIdentity:
        return AgentIdentity(
            agent_id=str(item.get("slug") or "").strip().lower(),
            display_name=str(item.get("display_name") or item.get("slug") or ""),
            role=str(item.get("role_label") or ""),
            description=str(item.get("description") or ""),
            route_role=str(item.get("route_role") or "specialist"),
            public_agent=bool(item.get("public_agent", False)),
            internal_agent=bool(item.get("internal_agent", item.get("internal", True))),
        )

    def get_snapshot(self, agent_id: str, *, org_slug: str, measured_at: Optional[int] = None) -> Optional[AgentEvolutionSnapshot]:
        normalized = str(agent_id or "").strip().lower()
        item = next((x for x in canonical_agent_items() if str(x.get("slug") or "").strip().lower() == normalized), None)
        if item is None:
            return None

        now = int(measured_at if measured_at is not None else self._now_fn())
        capabilities = [AgentCapability(**record) for record in capability_records(normalized)]
        knowledge = AgentKnowledgeSummary(**knowledge_summary(normalized))
        dependencies = dependency_records(normalized)

        gaps: list[AgentGap] = []
        if not capabilities:
            gaps.append(AgentGap(code="capability_registry_empty", severity="warning",
                description="No declared capabilities were found in the canonical capability registry.",
                evidence_status="confirmed"))
        if not knowledge.profile_available:
            gaps.append(AgentGap(code="knowledge_profile_unavailable", severity="info",
                description="No internal knowledge profile is available for this agent.",
                evidence_status="confirmed"))
        if knowledge.evidence_status != "confirmed":
            gaps.append(AgentGap(code="knowledge_evidence_partial", severity="info",
                description="Knowledge evidence is incomplete or unavailable in the current baseline.",
                evidence_status="partially_confirmed"))

        verified = sum(1 for c in capabilities if c.evidence_status == "confirmed")
        capability_coverage = round((verified / len(capabilities)) * 100.0, 2) if capabilities else 0.0
        evidence_confirmed = sum(1 for status in [*([c.evidence_status for c in capabilities]), knowledge.evidence_status] if status == "confirmed")
        evidence_total = len(capabilities) + 1
        confidence = round((evidence_confirmed / evidence_total) * 100.0, 2) if evidence_total else 0.0
        blocker_count = sum(1 for g in gaps if g.severity == "critical")
        maturity = round((capability_coverage * 0.65) + (confidence * 0.35), 2)
        health_status = "red" if blocker_count else ("green" if maturity >= 80 else "yellow")

        policy_inputs = {
            "proposal_only": True, "read_only": True, "auto_apply": False,
            "human_approval_required": True, "tenant_scope": org_slug,
            "measurement_policy_version": MEASUREMENT_POLICY_VERSION,
        }
        evidence = [
            EvolutionEvidence(source="app.runtime.agent_registry", source_version="canonical_static_v1",
                status="confirmed", detail="Identity composed from canonical runtime registry.", measured_at=now),
            EvolutionEvidence(source="app.runtime.capability_registry", source_version="current",
                status="confirmed", detail="Capabilities and dependencies read from existing registry.", measured_at=now),
            EvolutionEvidence(source="app.agents.registry", source_version="AO67C_AGENT_KNOWLEDGE_REGISTRY_V1",
                status=knowledge.evidence_status, detail="Knowledge coverage reflects registered profiles, cards and hooks.", measured_at=now),
        ]
        payload_for_fingerprint = {
            "agent": self._identity(item).model_dump(),
            "capabilities": [c.model_dump() for c in capabilities],
            "knowledge": knowledge.model_dump(),
            "gaps": [g.model_dump() for g in gaps],
            "dependencies": dependencies,
            "metrics": {"capability_coverage_percent": capability_coverage, "confidence_percent": confidence},
            "tenant_scope": org_slug,
        }
        return AgentEvolutionSnapshot(
            contract_version=CONTRACT_VERSION,
            schema_version=SCHEMA_VERSION,
            measurement_policy_version=MEASUREMENT_POLICY_VERSION,
            agent=self._identity(item),
            capabilities=capabilities,
            knowledge=knowledge,
            gaps=gaps,
            dependencies=dependencies,
            evidence=evidence,
            health=AgentHealth(status=health_status, maturity_percent=maturity,
                confidence_percent=confidence, coverage_percent=capability_coverage,
                blocker_count=blocker_count),
            metrics={
                "declared_capabilities": len(capabilities),
                "verified_capabilities": verified,
                "capability_coverage_percent": capability_coverage,
                "knowledge_card_count": knowledge.knowledge_card_count,
                "hook_count": knowledge.hook_count,
                "gap_count": len(gaps),
                "dependency_count": len(dependencies),
                "confidence_percent": confidence,
                "maturity_percent": maturity,
            },
            governance=policy_inputs,
            policy_resolution=PolicyResolution(
                resolved_at=now,
                resolved_inputs=policy_inputs,
                resolved_fingerprint=_fingerprint(policy_inputs),
            ),
            measured_at=now,
            latest_source_event_at=now,
            freshness_seconds=0,
            snapshot_fingerprint=_fingerprint(payload_for_fingerprint),
            write_executed=False,
        )

    def list_snapshots(self, *, org_slug: str, measured_at: Optional[int] = None) -> list[AgentEvolutionSnapshot]:
        now = int(measured_at if measured_at is not None else self._now_fn())
        return [s for agent_id in self.list_agent_ids() if (s := self.get_snapshot(agent_id, org_slug=org_slug, measured_at=now)) is not None]

    def aggregate(self, snapshots: list[AgentEvolutionSnapshot]) -> dict[str, Any]:
        count = len(snapshots)
        avg = lambda values: round(sum(values) / len(values), 2) if values else 0.0
        return {
            "agent_count": count,
            "green_count": sum(1 for s in snapshots if s.health.status == "green"),
            "yellow_count": sum(1 for s in snapshots if s.health.status == "yellow"),
            "red_count": sum(1 for s in snapshots if s.health.status == "red"),
            "average_maturity_percent": avg([s.health.maturity_percent for s in snapshots]),
            "average_confidence_percent": avg([s.health.confidence_percent for s in snapshots]),
            "total_gaps": sum(len(s.gaps) for s in snapshots),
            "total_capabilities": sum(len(s.capabilities) for s in snapshots),
            "write_executed": False,
        }
