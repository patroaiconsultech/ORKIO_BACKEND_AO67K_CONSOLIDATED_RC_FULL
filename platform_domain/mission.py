"""
ORKIO OS Mission Kernel.

This module defines the initial Mission domain primitives.

Scope:
- domain-only
- no persistence
- no API
- no runtime mutation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class MissionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MissionStage(str, Enum):
    DRAFT = "draft"
    DISCOVERY = "discovery"
    DIAGNOSIS = "diagnosis"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    LEARNING = "learning"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class MissionContext:
    domain: Optional[str] = None
    workspace_id: Optional[str] = None
    owner_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MissionHealth:
    progress: float = 0.0
    confidence: float = 0.0
    open_risks: int = 0
    blockers: List[str] = field(default_factory=list)
    next_action: Optional[str] = None
    executive_summary: Optional[str] = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.progress <= 1.0:
            raise ValueError("progress must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.open_risks < 0:
            raise ValueError("open_risks cannot be negative")


@dataclass(frozen=True)
class MissionSummary:
    id: str
    title: str
    objective: str
    status: MissionStatus
    stage: MissionStage


@dataclass
class Mission:
    id: str
    title: str
    objective: str
    status: MissionStatus = MissionStatus.DRAFT
    stage: MissionStage = MissionStage.DRAFT
    context: MissionContext = field(default_factory=MissionContext)
    health: MissionHealth = field(default_factory=MissionHealth)
    metadata: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def summary(self) -> MissionSummary:
        return MissionSummary(
            id=self.id,
            title=self.title,
            objective=self.objective,
            status=self.status,
            stage=self.stage,
        )

    def advance_to(self, stage: MissionStage) -> None:
        self.stage = stage
        if stage in (MissionStage.COMPLETED, MissionStage.ARCHIVED):
            self.status = MissionStatus.COMPLETED if stage == MissionStage.COMPLETED else MissionStatus.ARCHIVED
        elif self.status == MissionStatus.DRAFT and stage != MissionStage.DRAFT:
            self.status = MissionStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)
