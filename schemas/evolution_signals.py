from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


SignalStatus = Literal[
    "measured",
    "estimated",
    "insufficient_evidence",
    "source_unavailable",
]

EvaluationStatus = Literal["passed", "failed"]


class EvolutionMetricOut(BaseModel):
    key: str
    label: str
    score: Optional[int] = None
    confidence: int = Field(ge=0, le=100)
    sample_count: int = Field(ge=0)
    signal_status: SignalStatus
    formula_version: str
    source: list[str] = Field(default_factory=list)
    time_window: str
    missing_sources: list[str] = Field(default_factory=list)
    summary: str = ""


class AgentEvolutionMetricOut(BaseModel):
    agent_id: str
    agent_name: str
    score: Optional[int] = None
    confidence: int = Field(ge=0, le=100)
    sample_count: int = Field(ge=0)
    signal_status: SignalStatus
    formula_version: str
    capability_count: int = Field(default=0, ge=0)
    passed_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)


class EvolutionSignalsCurrentOut(BaseModel):
    snapshot_kind: Literal["current_readonly"] = "current_readonly"
    historical_trend: bool = False
    formula_version: str
    org_slug: str
    generated_at: int
    overall_score: Optional[int] = None
    overall_confidence: int = Field(ge=0, le=100)
    measured_metrics: int = Field(ge=0)
    total_metrics: int = Field(ge=1)
    coverage_percent: int = Field(ge=0, le=100)
    metrics: list[EvolutionMetricOut] = Field(default_factory=list)
    agents: list[AgentEvolutionMetricOut] = Field(default_factory=list)
    write_executed: bool = False


class EvolutionSignalHistoryItem(BaseModel):
    snapshot_id: str
    metric_key: str
    scope_type: Literal["platform", "agent"]
    scope_id: Optional[str] = None
    score: Optional[int] = None
    confidence: int
    sample_count: int
    signal_status: str
    formula_version: str
    window_start: int
    window_end: int
    created_at: int


class EvolutionSignalHistoryOut(BaseModel):
    org_slug: str
    count: int
    items: list[EvolutionSignalHistoryItem] = Field(default_factory=list)
    write_executed: bool = False


class EvolutionSignalCaptureIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    approved: bool
    reason: str = Field(min_length=8, max_length=300)


class EvolutionSignalCaptureOut(BaseModel):
    captured: bool
    snapshot_group_id: str
    metrics_persisted: int
    agent_metrics_persisted: int
    generated_at: int
    write_executed: bool = True


class AgentCapabilityEvaluationIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    agent_id: str = Field(min_length=1, max_length=128)
    capability_id: str = Field(min_length=1, max_length=160)
    evaluation_key: str = Field(min_length=1, max_length=180)
    status: EvaluationStatus
    score: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    evidence_ref: str = Field(min_length=4, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("evidence_ref")
    @classmethod
    def evidence_ref_must_not_be_secret(cls, value: str) -> str:
        lowered = value.lower()
        blocked = ("bearer ", "password=", "token=", "secret=", "api_key=")
        if any(marker in lowered for marker in blocked):
            raise ValueError("evidence_ref must be a non-secret reference")
        return value


class AgentCapabilityEvaluationOut(BaseModel):
    evaluation_id: str
    org_slug: str
    agent_id: str
    capability_id: str
    evaluation_key: str
    status: EvaluationStatus
    score: int
    confidence: int
    created_at: int
    write_executed: bool = True
