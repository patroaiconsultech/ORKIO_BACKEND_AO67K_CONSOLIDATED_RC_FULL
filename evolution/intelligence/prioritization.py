from __future__ import annotations

from typing import Any, Mapping

from .kpi_registry import get_kpi_definition


PRIORITIZATION_VERSION = "ORKIO-EVOLUTION-PRIORITY-R1"

_STATUS_SEVERITY = {
    "blocker": 100,
    "critical": 95,
    "warning": 70,
    "recovering": 45,
    "stale": 35,
    "insufficient_data": 30,
    "unknown": 20,
    "healthy": 0,
    "disabled": 0,
}


def _priority_class(score: float, *, blocker: bool) -> str:
    if blocker:
        return "P0"
    if score >= 90:
        return "P0"
    if score >= 75:
        return "P1"
    if score >= 50:
        return "P2"
    if score >= 25:
        return "P3"
    return "observation"


def build_priority_preview(
    health: Mapping[str, Any],
    *,
    objective_priority: int = 80,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for metric in health.get("kpis") or []:
        status = str(metric.get("status") or "unknown")
        if status in {"healthy", "disabled"}:
            continue
        definition = get_kpi_definition(str(metric.get("code") or ""))
        if definition is None:
            continue
        confidence = max(0.0, min(1.0, float(metric.get("confidence") or 0.0)))
        severity = _STATUS_SEVERITY.get(status, 20)
        business_impact = int(definition.business_impact)
        user_impact = round((definition.business_impact + definition.technical_impact) / 2)
        strategic_alignment = max(0, min(100, int(objective_priority)))
        trend_deterioration = 0
        fix_feasibility = 60
        score = (
            severity * 0.25
            + business_impact * 0.20
            + user_impact * 0.15
            + strategic_alignment * 0.15
            + confidence * 100 * 0.10
            + trend_deterioration * 0.10
            + fix_feasibility * 0.05
        )
        blocker = bool(metric.get("blocker")) and status == "critical"
        if confidence < 0.50:
            score = min(score, 24.0)
        items.append(
            {
                "priority_version": PRIORITIZATION_VERSION,
                "id": f"priority:{metric['code']}",
                "kpi_code": metric["code"],
                "severity": severity,
                "business_impact": business_impact,
                "user_impact": user_impact,
                "strategic_alignment": strategic_alignment,
                "confidence": round(confidence * 100, 2),
                "trend_deterioration": trend_deterioration,
                "trend_status": "unavailable",
                "fix_feasibility": fix_feasibility,
                "priority_score": round(score, 2),
                "priority_class": _priority_class(score, blocker=blocker),
                "blocker": blocker,
                "production_go": not blocker,
                "write_executed": False,
            }
        )
    items.sort(key=lambda item: (-int(item["blocker"]), -float(item["priority_score"])))
    return {
        "priority_version": PRIORITIZATION_VERSION,
        "org_slug": str(health.get("org_slug") or ""),
        "count": len(items),
        "items": items,
        "production_go": bool(health.get("production_go", False))
        and not any(item["blocker"] for item in items),
        "write_executed": False,
    }
