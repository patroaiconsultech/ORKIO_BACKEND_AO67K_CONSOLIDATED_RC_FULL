from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

EvidenceStatus = Literal["confirmed","partially_confirmed","inferred","hypothesis","not_tested"]
HealthStatus = Literal["green","yellow","red","unknown"]

class EvolutionEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str
    source_version: str = "unknown"
    status: EvidenceStatus = "confirmed"
    detail: str = ""
    measured_at: int | None = None

class AgentIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str
    display_name: str
    role: str
    description: str = ""
    route_role: str = "specialist"
    public_agent: bool = False
    internal_agent: bool = True

class AgentCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    purpose: str = ""
    risk_level: str = "unknown"
    governed: bool = True
    requires_authorization: bool = False
    allowed_targets: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = "confirmed"

class AgentKnowledgeSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_available: bool = False
    knowledge_card_count: int = 0
    hook_count: int = 0
    domains: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = "not_tested"

class AgentGap(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    severity: Literal["info","warning","critical"] = "info"
    description: str
    evidence_status: EvidenceStatus = "inferred"

class AgentHealth(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: HealthStatus = "unknown"
    maturity_percent: float = 0.0
    confidence_percent: float = 0.0
    coverage_percent: float = 0.0
    blocker_count: int = 0

class PolicyResolution(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resolved_at: int
    resolved_inputs: dict[str, Any]
    resolved_fingerprint: str

class AgentEvolutionSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    contract_version: str
    schema_version: str
    measurement_policy_version: str
    agent: AgentIdentity
    capabilities: list[AgentCapability]
    knowledge: AgentKnowledgeSummary
    gaps: list[AgentGap]
    dependencies: list[str]
    evidence: list[EvolutionEvidence]
    health: AgentHealth
    metrics: dict[str, Any]
    governance: dict[str, Any]
    policy_resolution: PolicyResolution
    measured_at: int
    latest_source_event_at: int
    freshness_seconds: int
    snapshot_fingerprint: str
    write_executed: bool = False

class AgentEvolutionListOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    contract_version: str
    org_slug: str
    count: int
    aggregate: dict[str, Any]
    items: list[AgentEvolutionSnapshot]
    write_executed: bool = False
