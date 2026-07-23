"""ORKIO Evolution modules."""

from .premium_contracts import (
    EvolutionPlan,
    RiskAssessment,
    RollbackPlan,
    SimulationReport,
)
from .premium_guard import ExecutionGateDecision, PremiumExecutionGuard
from .premium_pipeline import OrionPremiumEvolutionPipeline
from .premium_risk import PremiumRiskEngine
from .premium_simulation import PremiumSimulationEngine

__all__ = [
    "EvolutionPlan",
    "RiskAssessment",
    "RollbackPlan",
    "SimulationReport",
    "ExecutionGateDecision",
    "PremiumExecutionGuard",
    "OrionPremiumEvolutionPipeline",
    "PremiumRiskEngine",
    "PremiumSimulationEngine",
]

try:
    from orion.adapters.evolution_r20_adapter import EvolutionR20Adapter
except ImportError:  # Orion overlay may not be installed yet.
    EvolutionR20Adapter = None
