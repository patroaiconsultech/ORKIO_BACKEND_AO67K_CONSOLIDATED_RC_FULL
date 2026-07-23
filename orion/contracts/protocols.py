from __future__ import annotations

from typing import Any, Iterable, Protocol

from .models import (
    Diagnosis,
    Evidence,
    EvolutionProposal,
    ExecutionReport,
    GovernanceDecision,
    PatchArtifact,
    ValidationReport,
)


class PerceptionService(Protocol):
    def collect(self, context: Any) -> list[Evidence]: ...


class ReasoningService(Protocol):
    def diagnose(self, evidence: list[Evidence], context: Any) -> Diagnosis: ...


class PlanningService(Protocol):
    def build_proposal(self, diagnosis: Diagnosis, context: Any) -> EvolutionProposal: ...


class EngineeringService(Protocol):
    def generate_patch(self, proposal: EvolutionProposal, context: Any) -> PatchArtifact: ...


class GovernanceService(Protocol):
    def evaluate(self, artifact: object, context: Any) -> GovernanceDecision: ...


class ExecutionService(Protocol):
    def execute_in_workspace(
        self, patch: PatchArtifact, authorization: GovernanceDecision
    ) -> ExecutionReport: ...


class ValidationService(Protocol):
    def validate(self, execution: ExecutionReport, context: Any) -> ValidationReport: ...


class LearningService(Protocol):
    def record_outcome(self, cycle_report: Any) -> None: ...
