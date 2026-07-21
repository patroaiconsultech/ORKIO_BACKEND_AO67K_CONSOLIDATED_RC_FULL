from __future__ import annotations

from typing import Any, Mapping, Optional

from .kpi_registry import (
    PROJECT_HEALTH_WEIGHTS,
    KPIDefinition,
    get_kpi_definition,
)


HEALTH_FORMULA_VERSION = "ORKIO-EVOLUTION-HEALTH-R1.1"
KPI_STATUSES = {
    "unknown",
    "insufficient_data",
    "healthy",
    "warning",
    "critical",
    "recovering",
    "stale",
    "disabled",
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


def _target_values(
    definition: KPIDefinition,
    override: Optional[Mapping[str, Any]],
) -> tuple[float, float, float, float, int, bool]:
    data = dict(override or {})
    return (
        float(data.get("target_value", definition.target)),
        float(data.get("warning_threshold", definition.warning_threshold)),
        float(data.get("critical_threshold", definition.critical_threshold)),
        float(data.get("weight", definition.weight)),
        int(data.get("minimum_sample_size", definition.minimum_sample_size)),
        bool(data.get("enabled", definition.enabled)),
    )


def evaluate_kpi(
    metric: Mapping[str, Any],
    definition: KPIDefinition,
    *,
    target_override: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    target, warning, critical, weight, minimum_sample_size, enabled = _target_values(
        definition,
        target_override,
    )
    raw_score = metric.get("score")
    confidence = _clamp(float(metric.get("confidence") or 0)) / 100.0
    sample_size = max(0, int(metric.get("sample_count") or 0))
    source_status = str(metric.get("signal_status") or "unknown").strip().lower()
    missing_sources = list(metric.get("missing_sources") or [])

    if not enabled:
        status = "disabled"
    elif raw_score is None or source_status == "source_unavailable":
        status = "unknown"
    elif sample_size < minimum_sample_size or confidence < 0.50:
        status = "insufficient_data"
    else:
        score = _clamp(float(raw_score))
        if definition.direction == "higher_is_better":
            if score >= warning:
                status = "healthy"
            elif score >= critical:
                status = "warning"
            else:
                status = "critical"
        else:
            if score <= warning:
                status = "healthy"
            elif score <= critical:
                status = "warning"
            else:
                status = "critical"

    normalized_score = None if raw_score is None else round(_clamp(float(raw_score)), 2)
    return {
        "code": definition.code,
        "name": definition.name,
        "dimension": definition.dimension,
        "value": normalized_score,
        "value_semantics": "normalized_score",
        "score": normalized_score,
        "confidence": round(confidence, 4),
        "sample_size": sample_size,
        "minimum_sample_size": minimum_sample_size,
        "status": status,
        "target": target,
        "warning_threshold": warning,
        "critical_threshold": critical,
        "weight": weight,
        "source": list(metric.get("source") or definition.source),
        "source_status": source_status,
        "time_window": str(metric.get("time_window") or definition.window),
        "missing_sources": missing_sources,
        "summary": str(metric.get("summary") or ""),
        "formula_version": str(metric.get("formula_version") or ""),
        "definition_version": definition.definition_version,
        "collector_version": definition.collector_version,
        "source_version": definition.source_version,
        "proposal_enabled": bool(definition.proposal_enabled),
        "auto_apply_enabled": False,
        "blocker": bool(definition.blocker),
    }


def _weighted(values: list[tuple[float, float]]) -> Optional[float]:
    total_weight = sum(max(0.0, weight) for _, weight in values)
    if total_weight <= 0:
        return None
    return sum(value * max(0.0, weight) for value, weight in values) / total_weight


def build_project_health_preview(
    current_snapshot: Mapping[str, Any],
    *,
    target_overrides: Optional[Mapping[str, Mapping[str, Any]]] = None,
) -> dict[str, Any]:
    overrides = target_overrides or {}
    metrics_by_code = {
        str(metric.get("key") or ""): metric
        for metric in current_snapshot.get("metrics") or []
    }

    evaluated: list[dict[str, Any]] = []
    missing_kpis: list[str] = []
    unknown_kpis: list[str] = []
    stale_kpis: list[str] = []
    blocker_kpis: list[str] = []
    by_dimension: dict[str, list[dict[str, Any]]] = {
        key: [] for key in PROJECT_HEALTH_WEIGHTS
    }

    for code, metric in metrics_by_code.items():
        definition = get_kpi_definition(code)
        if definition is None:
            missing_kpis.append(code)
            continue
        item = evaluate_kpi(
            metric,
            definition,
            target_override=overrides.get(code),
        )
        evaluated.append(item)
        by_dimension[definition.dimension].append(item)
        if item["status"] in {"unknown", "insufficient_data", "stale"}:
            missing_kpis.append(code)
        if item["status"] == "unknown":
            unknown_kpis.append(code)
        if item["status"] == "stale":
            stale_kpis.append(code)
        if item["blocker"] and item["status"] == "critical":
            blocker_kpis.append(code)

    dimensions: dict[str, dict[str, Any]] = {}
    missing_dimensions: list[str] = []
    dimension_values: list[tuple[float, float]] = []
    confidence_values: list[tuple[float, float]] = []

    for dimension, project_weight in PROJECT_HEALTH_WEIGHTS.items():
        items = by_dimension.get(dimension) or []
        usable = [
            item
            for item in items
            if item["score"] is not None
            and item["status"] not in {"unknown", "disabled"}
        ]
        score_values = [
            (float(item["score"]), float(item["weight"]) * max(item["confidence"], 0.01))
            for item in usable
        ]
        confidence_components = [
            (float(item["confidence"]), float(item["weight"]))
            for item in usable
        ]
        score = _weighted(score_values)
        confidence = _weighted(confidence_components)
        if score is None:
            missing_dimensions.append(dimension)
        else:
            dimension_values.append((score, project_weight))
            confidence_values.append((float(confidence or 0.0), project_weight))
        dimensions[dimension] = {
            "score": None if score is None else round(score, 2),
            "confidence": 0.0 if confidence is None else round(confidence, 4),
            "weight": project_weight,
            "kpi_count": len(items),
            "usable_kpi_count": len(usable),
            "missing_kpis": [
                item["code"]
                for item in items
                if item["status"] in {"unknown", "insufficient_data", "stale"}
            ],
        }

    overall_score = _weighted(dimension_values)
    overall_confidence = _weighted(confidence_values)
    covered_weight = sum(
        PROJECT_HEALTH_WEIGHTS[dimension]
        for dimension in PROJECT_HEALTH_WEIGHTS
        if dimension not in missing_dimensions
    )
    coverage = round(covered_weight / sum(PROJECT_HEALTH_WEIGHTS.values()), 4)

    if blocker_kpis:
        status = "blocker"
        production_go = False
    elif overall_score is None:
        status = "unknown"
        production_go = False
    elif overall_score >= 90:
        status = "healthy"
        production_go = True
    elif overall_score >= 75:
        status = "warning"
        production_go = True
    else:
        status = "critical"
        production_go = False

    return {
        "formula_version": HEALTH_FORMULA_VERSION,
        "org_slug": str(current_snapshot.get("org_slug") or ""),
        "generated_at": int(current_snapshot.get("generated_at") or 0),
        "score": None if overall_score is None else round(overall_score, 2),
        "confidence": 0.0 if overall_confidence is None else round(overall_confidence, 4),
        "coverage": coverage,
        "health_coverage": coverage,
        "coverage_status": (
            "complete"
            if coverage >= 0.9999 and not missing_kpis
            else "partial"
            if coverage > 0
            else "insufficient"
        ),
        "status": status,
        "production_go": production_go,
        "dimensions": dimensions,
        "kpis": evaluated,
        "missing_kpis": sorted(set(missing_kpis)),
        "unknown_kpis": sorted(set(unknown_kpis)),
        "stale_kpis": sorted(set(stale_kpis)),
        "missing_dimensions": missing_dimensions,
        "blocker_kpis": sorted(set(blocker_kpis)),
        "blockers": sorted(set(blocker_kpis)),
        "write_executed": False,
        "auto_apply_enabled": False,
    }
