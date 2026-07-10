from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional

from .contracts import ExecutivePreflightResult

AO72_EXECUTIVE_ENGINE_VERSION = "AO72_EXECUTIVE_ENGINE_RC1_V1"

_NUMBER_RE = re.compile(
    r"(?:r\$|us\$|usd)?\s*\d[\d\.,]*\s*(?:%|milh(?:ao|oes)|mi|mil|k|m|meses?|dias?|anos?)?",
    re.I,
)

_EXECUTIVE_TERMS = {
    "ceo", "cfo", "cto", "board", "conselho", "diretoria", "executivo",
    "mrr", "arr", "nrr", "churn", "cac", "ltv", "payback", "runway",
    "caixa", "margem", "receita", "ebitda", "valuation", "gmv", "take rate",
    "captacao", "captação", "crescimento", "risco", "riscos",
}

_ACTION_TERMS = {
    "analise", "análise", "avalie", "diagnostico", "diagnóstico", "decida",
    "decisão", "recomende", "recomendação", "estruture", "calcule",
    "separe", "plano", "roadmap", "tese",
}


def _norm(value: Any) -> str:
    raw = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(ch for ch in raw if not unicodedata.combining(ch))


def _contains_any(text: str, terms) -> bool:
    return any(_norm(term) in text for term in terms)


def _required_outputs(text: str) -> List[str]:
    out: List[str] = []

    def add(key: str) -> None:
        if key not in out:
            out.append(key)

    checks = [
        ("thesis", ["tese"]),
        ("diagnosis", ["diagnostico", "diagnóstico"]),
        ("facts", ["fatos"]),
        ("inferences", ["inferencias", "inferências"]),
        ("missing_data", ["dados faltantes", "informacoes faltantes", "informações faltantes"]),
        ("risks", ["risco", "riscos"]),
        ("decision_metrics", ["metricas de decisao", "métricas de decisão", "metricas", "métricas"]),
        ("stop_triggers", ["gatilhos de parada", "gatilhos", "stop triggers"]),
        ("recommendation", ["recomendacao", "recomendação", "decisao recomendada", "decisão recomendada"]),
        ("next_steps", ["proximos passos", "próximos passos"]),
        ("roadmap", ["roadmap", "30-60-90", "30 60 90"]),
        ("financial_calculation", ["calcule", "calculo", "cálculo", "margem", "runway", "ltv/cac", "payback"]),
    ]
    for key, terms in checks:
        if _contains_any(text, terms):
            add(key)

    # Executive decision prompts need a minimum decision structure even when
    # the user does not enumerate every section.
    if _contains_any(text, ["decidir", "decisao", "decisão", "board", "conselho"]):
        for key in ("thesis", "risks", "decision_metrics", "recommendation"):
            add(key)

    return out


def build_executive_preflight(
    message: Any,
    *,
    response_control: Optional[str] = None,
    visible_agent: Optional[str] = None,
    target_agent_slug: Optional[str] = None,
    dest_mode: Optional[str] = None,
) -> Dict[str, Any]:
    text = _norm(message)
    rc = _norm(response_control)

    explicit_control = "structured_executive" in rc or "executive_direct" in rc
    executive_hits = sum(1 for term in _EXECUTIVE_TERMS if _norm(term) in text)
    action_hits = sum(1 for term in _ACTION_TERMS if _norm(term) in text)
    number_hits = len([m for m in _NUMBER_RE.findall(text) if str(m).strip()])

    explicit_specialist = _contains_any(
        " ".join([_norm(visible_agent), _norm(target_agent_slug), _norm(dest_mode)]),
        ["aria", "chris", "orion", "team", "equipe"],
    )

    operational_direct = (
        not explicit_specialist
        and _contains_any(
            text,
            [
                "confirme que esta operacional",
                "confirme que está operacional",
                "esta operacional",
                "está operacional",
                "status operacional",
                "responda em uma frase",
            ],
        )
    )

    structured = bool(
        explicit_control
        or (
            not explicit_specialist
            and executive_hits >= 1
            and action_hits >= 1
            and (number_hits >= 2 or executive_hits >= 3)
        )
    )

    required = _required_outputs(text) if structured else []
    if structured and not required:
        required = ["diagnosis", "risks", "recommendation"]

    confidence = 0.0
    if structured:
        confidence = min(
            0.99,
            0.55 + min(executive_hits, 4) * 0.07 + min(action_hits, 3) * 0.06 + min(number_hits, 4) * 0.04,
        )

    intent = "general"
    if structured:
        if _contains_any(text, ["board", "conselho", "decidir", "decisao", "decisão"]):
            intent = "executive_board_decision"
        elif _contains_any(text, ["mrr", "arr", "nrr", "churn", "cac", "ltv", "runway", "margem", "gmv"]):
            intent = "executive_financial_analysis"
        else:
            intent = "structured_executive_analysis"

    if operational_direct and not structured:
        intent = "operational_direct_answer"
        confidence = 0.95

    result = ExecutivePreflightResult(
        version=AO72_EXECUTIVE_ENGINE_VERSION,
        applies=structured,
        intent=intent,
        confidence=round(confidence, 3),
        required_outputs=required,
        block_public_journey_fastpath=bool(structured or operational_direct),
        quality_mode="strict" if structured else "standard",
        reason=(
            "structured_executive_task"
            if structured
            else ("operational_direct_answer" if operational_direct else "not_executive")
        ),
    )
    return result.to_dict()
