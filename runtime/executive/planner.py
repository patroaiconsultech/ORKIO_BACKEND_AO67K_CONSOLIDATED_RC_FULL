from __future__ import annotations

from typing import Any, Dict, List


_LABELS = {
    "thesis": "tese executiva",
    "diagnosis": "diagnóstico",
    "facts": "fatos",
    "inferences": "inferências",
    "missing_data": "dados faltantes",
    "risks": "riscos",
    "decision_metrics": "métricas de decisão",
    "stop_triggers": "gatilhos de parada",
    "recommendation": "recomendação",
    "next_steps": "próximos passos",
    "financial_calculation": "cálculos financeiros solicitados",
    "roadmap": "roadmap/plano de execução",
}


def build_execution_plan(preflight: Dict[str, Any]) -> Dict[str, Any]:
    required: List[str] = list((preflight or {}).get("required_outputs") or [])
    return {
        "version": (preflight or {}).get("version"),
        "applies": bool((preflight or {}).get("applies")),
        "intent": (preflight or {}).get("intent") or "general",
        "quality_mode": (preflight or {}).get("quality_mode") or "standard",
        "required_outputs": required,
        "required_output_labels": [_LABELS.get(item, item) for item in required],
        "instruction": (
            "Responda diretamente, use apenas os dados fornecidos, diferencie fatos de "
            "inferências e cubra todos os entregáveis obrigatórios."
            if required else ""
        ),
    }
