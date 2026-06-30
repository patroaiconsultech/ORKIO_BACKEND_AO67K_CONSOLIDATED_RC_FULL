from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"

@dataclass(frozen=True)
class Organization:
    organization_id: str
    name: str
    slug: str
    status: str = "active"
    plan: str = "beta"
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class Workspace:
    workspace_id: str
    organization_id: str
    name: str
    slug: str
    knowledge_scope: str = "workspace"
    planner_scope: str = "workspace"
    learning_scope: str = "workspace"
    members: list[str] = field(default_factory=list)
    status: str = "active"
    created_at: str = field(default_factory=_now)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class Project:
    project_id: str
    organization_id: str
    workspace_id: str
    name: str
    slug: str
    status: str = "active"
    modules: list[str] = field(default_factory=lambda: [
        "knowledge", "conversation", "proposal", "learning", "planner", "governance"
    ])
    created_at: str = field(default_factory=_now)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    organization_id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
