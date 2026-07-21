from __future__ import annotations

from typing import Any, Mapping

from .kpi_registry import get_kpi_definition


DIAGNOSTIC_VERSION = "ORKIO-EVOLUTION-DIAGNOSTIC-R1"


def build_diagnostic_preview(health: Mapping[str, Any]) -> dict[str, Any]:
    diagnostics: list[dict[str, Any]] = []
    for item in health.get("kpis") or []:
        status = str(item.get("status") or "unknown")
        if status == "healthy" or status == "disabled":
            continue
        code = str(item.get("code") or "")
        definition = get_kpi_definition(code)
        if definition is None:
            continue
        confidence = float(item.get("confidence") or 0.0)
        if confidence < 0.50:
            action = "collect_more_evidence"
        elif confidence < 0.75:
            action = "observability_proposal_only"
        elif confidence < 0.85:
            action = "diagnosis_allowed"
        else:
            action = "technical_proposal_allowed"

        diagnostics.append(
            {
                "diagnostic_version": DIAGNOSTIC_VERSION,
                "kpi": code,
                "status": status,
                "evidence": [
                    {
                        "classification": "evidência confirmada",
                        "fact": str(item.get("summary") or "Métrica calculada."),
                        "source": source,
                    }
                    for source in (item.get("source") or [])
                ],
                "hypotheses": [
                    {
                        "classification": "hipótese prioritária",
                        "cause": hypothesis,
                        "confidence": round(max(0.10, confidence * 0.70), 4),
                    }
                    for hypothesis in definition.diagnostic_playbook
                ],
                "root_cause_status": "not_confirmed",
                "confidence": confidence,
                "recommended_action": action,
                "allowed_actions": list(definition.allowed_actions),
                "forbidden_actions": list(definition.forbidden_actions),
                "write_executed": False,
            }
        )
    return {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "org_slug": str(health.get("org_slug") or ""),
        "count": len(diagnostics),
        "items": diagnostics,
        "write_executed": False,
    }
