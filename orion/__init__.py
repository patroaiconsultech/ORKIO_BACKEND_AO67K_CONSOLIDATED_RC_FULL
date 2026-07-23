"""Orion controlled-evolution subsystem, R21-R25."""

from .contracts.models import (
    Diagnosis,
    Evidence,
    EvolutionProposal,
    GovernanceDecision,
    OrionEvent,
    PatchArtifact,
    ValidationReport,
)
from .kernel.cognitive_kernel import CognitiveKernel, KernelServices

__all__ = [
    "Evidence",
    "Diagnosis",
    "EvolutionProposal",
    "GovernanceDecision",
    "OrionEvent",
    "PatchArtifact",
    "ValidationReport",
    "CognitiveKernel",
    "KernelServices",
]

__version__ = "25.0.0"
