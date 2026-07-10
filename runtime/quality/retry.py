from __future__ import annotations

from typing import Any, Dict

_LABELS = {
    "operating_profit": "lucro operacional/resultado",
    "margin": "margem",
    "runway": "runway/caixa/burn",
    "ltv": "LTV",
    "cac": "CAC",
    "ltv_cac_ratio": "LTV/CAC",
    "plan_30_60_90": "plano 30-60-90",
    "roadmap": "roadmap",
    "risks_constraints": "riscos/restrições",
    "recommendations": "recomendações executivas",
    "executive_summary": "síntese executiva",
    "next_steps": "próximos passos",
    "thesis": "tese executiva",
    "facts": "fatos",
    "inferences": "inferências",
    "missing_data": "dados faltantes",
    "decision_metrics": "métricas de decisão",
    "stop_triggers": "gatilhos de parada",
    "recommendation": "recomendação final",
}

def ao70_build_quality_retry_prompt(*, original_prompt: Any, first_answer: Any, validation: Dict[str, Any]) -> str:
    missing = list((validation or {}).get("missing_items") or [])
    missing_labels = [_LABELS.get(str(x), str(x)) for x in missing]
    missing_text = "\n".join(f"- {label}" for label in missing_labels) or "- completude executiva"

    return f"""Você deve refazer a resposta ao pedido original abaixo.

PEDIDO ORIGINAL:
{str(original_prompt or '').strip()}

A resposta anterior ficou incompleta. Itens obrigatórios ausentes ou fracos:
{missing_text}

REGRAS:
1. Responda diretamente ao pedido original.
2. Não faça onboarding nem peça dados que já foram fornecidos.
3. Quando houver números suficientes, calcule e mostre a lógica de forma objetiva.
4. Cubra todos os itens obrigatórios.
5. Estruture como resposta executiva, com diagnóstico, cálculos, riscos e próximos passos quando aplicável.
6. Não mencione auditoria interna, score, retry ou política do sistema.

RESPOSTA ANTERIOR APENAS PARA CONTEXTO:
{str(first_answer or '').strip()}
"""
