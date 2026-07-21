"""Evolution Intelligence Foundation — proposal-only, tenant-isolated."""

from .governance import (
    EVOLUTION_INTELLIGENCE_VERSION,
    EvolutionGovernanceError,
    load_evolution_governance_config,
    validate_evolution_governance_config,
)
from .kpi_registry import (
    KPI_REGISTRY_VERSION,
    KPIDefinition,
    get_kpi_definition,
    list_kpi_definitions,
)
from .scoring import build_project_health_preview

__all__ = [
    "EVOLUTION_INTELLIGENCE_VERSION",
    "EvolutionGovernanceError",
    "KPI_REGISTRY_VERSION",
    "KPIDefinition",
    "build_project_health_preview",
    "get_kpi_definition",
    "list_kpi_definitions",
    "load_evolution_governance_config",
    "validate_evolution_governance_config",
]
