from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal, Optional


KPI_REGISTRY_VERSION = "ORKIO-EVOLUTION-KPI-REGISTRY-R2"
KPI_COLLECTOR_VERSION = "ORKIO-EVOLUTION-COLLECTORS-R2"
KPI_SOURCE_VERSION = "ORKIO-EVOLUTION-SOURCES-R2"

KPIDirection = Literal["higher_is_better", "lower_is_better"]
KPIDimension = Literal[
    "technical",
    "ai_runtime",
    "product",
    "experience",
    "governance",
    "evolution",
]

PROJECT_HEALTH_WEIGHTS: dict[str, float] = {
    "technical": 0.25,
    "ai_runtime": 0.20,
    "product": 0.15,
    "experience": 0.15,
    "governance": 0.15,
    "evolution": 0.10,
}

REQUIRED_KPI_FIELDS = (
    "code",
    "name",
    "description",
    "dimension",
    "unit",
    "direction",
    "source",
    "collector",
    "aggregation",
    "window",
    "minimum_sample_size",
    "target",
    "warning_threshold",
    "critical_threshold",
    "weight",
    "enabled",
    "proposal_enabled",
    "auto_apply_enabled",
    "collector_version",
    "source_version",
)


@dataclass(frozen=True)
class KPIDefinition:
    code: str
    name: str
    description: str
    dimension: KPIDimension
    unit: str
    direction: KPIDirection
    source: tuple[str, ...]
    collector: str
    aggregation: str
    window: str
    minimum_sample_size: int
    target: float
    warning_threshold: float
    critical_threshold: float
    weight: float
    enabled: bool = True
    proposal_enabled: bool = True
    auto_apply_enabled: bool = False
    owner: str = "ORKIO Engineering"
    data_freshness_limit_seconds: int = 86_400
    confidence_method: str = "sample_freshness_source_consistency_v1"
    business_impact: int = 70
    technical_impact: int = 70
    failure_domain: tuple[str, ...] = ()
    allowed_actions: tuple[str, ...] = (
        "generate_diagnostic",
        "recommend_instrumentation",
        "propose_patch",
    )
    forbidden_actions: tuple[str, ...] = (
        "increase_timeout_without_root_cause",
        "silence_errors",
        "auto_apply",
    )
    diagnostic_playbook: tuple[str, ...] = ()
    blocker: bool = False
    definition_version: str = KPI_REGISTRY_VERSION
    collector_version: str = KPI_COLLECTOR_VERSION
    source_version: str = KPI_SOURCE_VERSION

    def definition_status(self) -> str:
        payload = asdict(self)
        missing = []
        for field in REQUIRED_KPI_FIELDS:
            value = payload.get(field)
            if value is None or value == "" or value == () or value == []:
                missing.append(field)
        if self.minimum_sample_size < 0 or not 0 <= self.weight <= 1:
            missing.append("invalid_numeric_contract")
        if self.auto_apply_enabled:
            missing.append("auto_apply_must_be_false")
        return "complete" if not missing else "definition_incomplete"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source"] = list(self.source)
        payload["failure_domain"] = list(self.failure_domain)
        payload["allowed_actions"] = list(self.allowed_actions)
        payload["forbidden_actions"] = list(self.forbidden_actions)
        payload["diagnostic_playbook"] = list(self.diagnostic_playbook)
        payload["definition_status"] = self.definition_status()
        return payload


_DEFINITIONS: tuple[KPIDefinition, ...] = (
    KPIDefinition(
        code="security_governance",
        name="Segurança e governança",
        description="Avalia controles fail-closed e flags de mutação sem expor valores sensíveis.",
        dimension="governance",
        unit="score",
        direction="higher_is_better",
        source=("runtime_control_flags",),
        collector="_security_metric",
        aggregation="policy_check_ratio",
        window="current_runtime",
        minimum_sample_size=10,
        target=100,
        warning_threshold=92,
        critical_threshold=80,
        weight=0.35,
        business_impact=100,
        technical_impact=100,
        failure_domain=("security", "governance", "runtime"),
        diagnostic_playbook=(
            "confirmar flags de mutação",
            "confirmar human approval",
            "confirmar tenant isolation",
            "confirmar release identity",
        ),
        blocker=True,
    ),
    KPIDefinition(
        code="operational_reliability",
        name="Confiabilidade operacional",
        description="Percentual de execuções terminais concluídas com sucesso.",
        dimension="technical",
        unit="percent",
        direction="higher_is_better",
        source=("admin_evolution_executions",),
        collector="_reliability_metric",
        aggregation="success_ratio",
        window="30d",
        minimum_sample_size=20,
        target=99,
        warning_threshold=95,
        critical_threshold=90,
        weight=0.55,
        business_impact=90,
        technical_impact=95,
        failure_domain=("backend", "database", "infrastructure", "provider"),
        diagnostic_playbook=(
            "separar falhas por status terminal",
            "correlacionar request_id e release_id",
            "verificar migrations e pool",
            "não aumentar timeout sem causa raiz",
        ),
    ),
    KPIDefinition(
        code="governed_autoevolution",
        name="Autoevolução governada",
        description="Verifica aprovação humana, rollback e ausência de execução real não autorizada.",
        dimension="evolution",
        unit="score",
        direction="higher_is_better",
        source=("admin_evolution_proposals", "admin_evolution_executions"),
        collector="_autoevolution_metric",
        aggregation="governance_check_ratio",
        window="current_queue_and_30d_executions",
        minimum_sample_size=5,
        target=100,
        warning_threshold=95,
        critical_threshold=85,
        weight=1.0,
        business_impact=95,
        technical_impact=95,
        failure_domain=("governance", "repository", "deployment"),
        diagnostic_playbook=(
            "confirmar proposal_only",
            "confirmar write flags false",
            "confirmar rollback plan",
            "confirmar approval receipt",
        ),
        blocker=True,
    ),
    KPIDefinition(
        code="agent_knowledge",
        name="Conhecimento dos agentes",
        description="Qualidade ponderada das avaliações reais de capacidade dos agentes.",
        dimension="ai_runtime",
        unit="score",
        direction="higher_is_better",
        source=("agent_capability_evaluations", "agent_knowledge"),
        collector="_agent_knowledge_metric",
        aggregation="confidence_weighted_mean",
        window="90d",
        minimum_sample_size=10,
        target=90,
        warning_threshold=75,
        critical_threshold=60,
        weight=1.0,
        business_impact=75,
        technical_impact=70,
        failure_domain=("agent_runtime", "knowledge", "evaluation"),
        diagnostic_playbook=(
            "verificar cobertura por capability",
            "separar ausência de dados de falha",
            "confirmar evidência não sensível",
        ),
    ),
    KPIDefinition(
        code="core_modules",
        name="Módulos principais",
        description="Completude estrutural das configurações essenciais dos agentes.",
        dimension="technical",
        unit="score",
        direction="higher_is_better",
        source=("agents",),
        collector="_core_modules_metric",
        aggregation="configuration_check_ratio",
        window="current_configuration",
        minimum_sample_size=3,
        target=95,
        warning_threshold=85,
        critical_threshold=70,
        weight=0.45,
        business_impact=70,
        technical_impact=85,
        failure_domain=("configuration", "agent_runtime"),
        diagnostic_playbook=(
            "identificar campos ausentes por agente",
            "confirmar provider e model",
            "confirmar tool policy",
        ),
    ),
    KPIDefinition(
        code="evidence_observability",
        name="Evidência e observabilidade",
        description="Cobertura de request_id, ação, status, latência e execução rastreável.",
        dimension="governance",
        unit="score",
        direction="higher_is_better",
        source=("audit_logs", "admin_evolution_executions"),
        collector="_evidence_metric",
        aggregation="evidence_field_coverage",
        window="24h_audit_and_30d_executions",
        minimum_sample_size=30,
        target=98,
        warning_threshold=90,
        critical_threshold=75,
        weight=0.30,
        business_impact=80,
        technical_impact=90,
        failure_domain=("observability", "audit", "backend"),
        diagnostic_playbook=(
            "localizar primeiro evento sem request_id",
            "correlacionar action/path/status",
            "confirmar evento terminal",
        ),
    ),
    KPIDefinition(
        code="premium_experience",
        name="Experiência premium",
        description="Completude dos elementos de apresentação e configuração premium dos agentes.",
        dimension="experience",
        unit="score",
        direction="higher_is_better",
        source=("agents",),
        collector="_premium_experience_metric",
        aggregation="configuration_check_ratio",
        window="current_configuration",
        minimum_sample_size=3,
        target=90,
        warning_threshold=75,
        critical_threshold=60,
        weight=1.0,
        business_impact=85,
        technical_impact=55,
        failure_domain=("frontend", "product", "agent_configuration"),
        diagnostic_playbook=(
            "identificar descrição, voz, avatar ou modelo ausente",
            "validar impacto real na jornada",
        ),
    ),
)

_BY_CODE = {definition.code: definition for definition in _DEFINITIONS}


def list_kpi_definitions(*, enabled_only: bool = False) -> list[KPIDefinition]:
    values = list(_DEFINITIONS)
    if enabled_only:
        values = [definition for definition in values if definition.enabled]
    return values


def get_kpi_definition(code: str) -> Optional[KPIDefinition]:
    return _BY_CODE.get(str(code or "").strip())


def registry_payload() -> dict[str, Any]:
    definitions = [definition.to_dict() for definition in _DEFINITIONS]
    incomplete = [
        definition["code"]
        for definition in definitions
        if definition["definition_status"] != "complete"
    ]
    return {
        "registry_version": KPI_REGISTRY_VERSION,
        "definitions": definitions,
        "count": len(definitions),
        "definition_complete_count": len(definitions) - len(incomplete),
        "definition_incomplete": incomplete,
        "project_health_weights": dict(PROJECT_HEALTH_WEIGHTS),
        "auto_apply_enabled": False,
    }
