from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ObjectiveStatus = Literal["draft", "active", "paused", "completed"]
ProposalPolicy = Literal["proposal_only"]


class ObjectiveCreateIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    approved: bool
    name: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=8, max_length=4000)
    category: str = Field(min_length=3, max_length=64)
    priority: int = Field(default=50, ge=0, le=100)
    status: ObjectiveStatus = "draft"
    starts_at: Optional[int] = Field(default=None, ge=0)
    ends_at: Optional[int] = Field(default=None, ge=0)
    owner_ref: str = Field(min_length=2, max_length=180)
    success_definition: str = Field(min_length=8, max_length=2000)
    proposal_policy: ProposalPolicy = "proposal_only"
    human_approval_required: bool = True

    @model_validator(mode="after")
    def validate_governance(self):
        if not self.approved:
            raise ValueError("human approval is required")
        if not self.human_approval_required:
            raise ValueError("human_approval_required must remain true")
        if self.ends_at is not None and self.starts_at is not None:
            if self.ends_at <= self.starts_at:
                raise ValueError("ends_at must be greater than starts_at")
        return self


class ObjectiveUpdateIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    approved: bool
    name: Optional[str] = Field(default=None, min_length=3, max_length=180)
    description: Optional[str] = Field(default=None, min_length=8, max_length=4000)
    category: Optional[str] = Field(default=None, min_length=3, max_length=64)
    priority: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[ObjectiveStatus] = None
    starts_at: Optional[int] = Field(default=None, ge=0)
    ends_at: Optional[int] = Field(default=None, ge=0)
    owner_ref: Optional[str] = Field(default=None, min_length=2, max_length=180)
    success_definition: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=2000,
    )
    proposal_policy: Optional[ProposalPolicy] = None
    human_approval_required: Optional[bool] = None

    @model_validator(mode="after")
    def validate_governance(self):
        if not self.approved:
            raise ValueError("human approval is required")
        if self.human_approval_required is False:
            raise ValueError("human_approval_required must remain true")
        return self


class KPITargetUpsertIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    approved: bool
    objective_id: Optional[str] = Field(default=None, max_length=96)
    kpi_code: str = Field(min_length=3, max_length=128)
    target_value: float = Field(ge=0, le=100)
    warning_threshold: float = Field(ge=0, le=100)
    critical_threshold: float = Field(ge=0, le=100)
    weight: float = Field(gt=0, le=1)
    minimum_sample_size: int = Field(ge=0, le=10_000_000)
    enabled: bool = True
    proposal_enabled: bool = True
    auto_apply_enabled: bool = False
    change_reason: str = Field(min_length=8, max_length=300)
    approval_id: str = Field(min_length=3, max_length=160)

    @model_validator(mode="after")
    def validate_target(self):
        if not self.approved:
            raise ValueError("human approval is required")
        if self.auto_apply_enabled:
            raise ValueError("auto_apply_enabled must remain false")
        if self.critical_threshold > self.warning_threshold:
            raise ValueError("critical_threshold must be <= warning_threshold")
        if self.warning_threshold > self.target_value:
            raise ValueError("warning_threshold must be <= target_value")
        return self


class HealthSnapshotCaptureIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    approved: bool
    reason: str = Field(min_length=8, max_length=300)
    objective_id: Optional[str] = Field(default=None, max_length=96)

    @field_validator("approved")
    @classmethod
    def approval_required(cls, value: bool) -> bool:
        if not value:
            raise ValueError("human approval is required")
        return value


class HealthSnapshotInvalidateIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    approved: bool
    reason: str = Field(min_length=8, max_length=500)
    approval_id: str = Field(min_length=3, max_length=160)

    @field_validator("approved")
    @classmethod
    def approval_required(cls, value: bool) -> bool:
        if not value:
            raise ValueError("human approval is required")
        return value


class ProposalPreviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    objective_id: Optional[str] = Field(default=None, max_length=96)
    kpi_codes: list[str] = Field(default_factory=list, max_length=50)


class GenericEvolutionOut(BaseModel):
    model_config = ConfigDict(extra="allow")

    org_slug: str
    write_executed: bool = False


class ObjectiveOut(GenericEvolutionOut):
    id: str
    name: str
    description: str
    category: str
    priority: int
    status: ObjectiveStatus
    starts_at: Optional[int] = None
    ends_at: Optional[int] = None
    owner_ref: str
    success_definition: str
    proposal_policy: ProposalPolicy
    human_approval_required: bool
    version: int
    created_at: int
    updated_at: int


class ObjectiveListOut(GenericEvolutionOut):
    count: int
    items: list[ObjectiveOut] = Field(default_factory=list)


class KPIRegistryOut(GenericEvolutionOut):
    registry_version: str
    count: int
    definition_complete_count: int
    definition_incomplete: list[str] = Field(default_factory=list)
    definitions: list[dict[str, Any]] = Field(default_factory=list)
    project_health_weights: dict[str, float] = Field(default_factory=dict)
    targets: list[dict[str, Any]] = Field(default_factory=list)


class HealthPreviewOut(GenericEvolutionOut):
    formula_version: str
    generated_at: int
    score: Optional[float] = None
    confidence: float
    coverage: float
    health_coverage: float
    coverage_status: str
    status: str
    production_go: bool
    dimensions: dict[str, Any] = Field(default_factory=dict)
    kpis: list[dict[str, Any]] = Field(default_factory=list)
    missing_kpis: list[str] = Field(default_factory=list)
    unknown_kpis: list[str] = Field(default_factory=list)
    stale_kpis: list[str] = Field(default_factory=list)
    missing_dimensions: list[str] = Field(default_factory=list)
    blocker_kpis: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    release_identity: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    window_start: int
    window_end: int
    sample_size: int


class DiagnosticPreviewOut(GenericEvolutionOut):
    diagnostic_version: str
    count: int
    items: list[dict[str, Any]] = Field(default_factory=list)


class PriorityPreviewOut(GenericEvolutionOut):
    priority_version: str
    count: int
    items: list[dict[str, Any]] = Field(default_factory=list)
    production_go: bool


class ProposalPreviewOut(GenericEvolutionOut):
    proposal_mode: Literal["proposal_only"] = "proposal_only"
    count: int
    items: list[dict[str, Any]] = Field(default_factory=list)
    human_approval_required: bool = True
    auto_apply: bool = False


class HealthSnapshotListOut(GenericEvolutionOut):
    count: int
    items: list[dict[str, Any]] = Field(default_factory=list)
