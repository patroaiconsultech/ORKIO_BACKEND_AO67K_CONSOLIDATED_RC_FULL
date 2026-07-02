from __future__ import annotations

"""Pure routing guard for substantive executive work.

This module has no database, provider, network, or persistence side effects. It
only decides whether a request must bypass deterministic public fast-paths and
continue to Orkio's contextual runtime.
"""

import re
import unicodedata
from typing import Any, Dict, Iterable, Tuple


ORKIO_EXECUTIVE_GUARD_VERSION = "AO85_ORKIO_EXECUTIVE_RUNTIME_AUTHORITY_V1"


def _normalize(value: Any) -> str:
    raw = str(value or "").strip()
    try:
        raw = unicodedata.normalize("NFD", raw)
        raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    except Exception:
        pass
    return re.sub(r"\s+", " ", raw.lower()).strip()


def _matches(text: str, markers: Iterable[str]) -> Tuple[str, ...]:
    return tuple(marker for marker in markers if marker in text)[:8]


_DIRECTIVE_MARKERS = (
    "analise", "avalie", "compare", "recomende", "diagnostico", "calcule",
    "mostre os calculos", "estruture", "elabore", "proponha", "priorize",
    "roadmap", "plano de acao", "primeiro passo", "proximo passo",
    "como melhorar", "como aumentar", "como reduzir", "como escalar",
    "prepare minha empresa", "simule", "projete", "quantifique", "decida",
    "analyze", "evaluate", "compare", "recommend", "diagnose", "calculate",
    "roadmap", "action plan", "first step", "next step", "how to improve",
)

_BUSINESS_MARKERS = (
    "empresa", "negocio", "modelo de negocio", "estrategia", "objetivo",
    "receita", "faturamento", "margem", "lucro", "custo", "caixa", "ebitda",
    "preco", "pricing", "vendas", "comercial", "cliente", "mercado", "b2b",
    "crescimento", "expansao", "operacao", "processo", "equipe", "lideranca",
    "marketing", "funil", "cac", "ltv", "roi", "valuation", "captacao",
    "investimento", "risco", "indicador", "kpi", "projeto", "produto", "mvp",
    "esg", "governanca", "company", "business", "revenue", "margin", "profit",
    "cost", "cash flow", "sales", "customer", "market", "growth", "operations",
)

_STRUCTURE_MARKERS = (
    "30 dias", "60 dias", "90 dias", "30/60/90", "cenario", "cenarios",
    "premissa", "premissas", "restricao", "restricoes", "meta", "metas",
    "responsavel", "responsaveis", "owner", "owners", "kpi", "indicador",
    "etapa", "etapas", "fase", "fases", "prioridade", "prioridades",
)

_CONSTRAINED_ANSWER_MARKERS = (
    "responda apenas", "responda somente", "responda exatamente",
    "diga exatamente", "retorne somente", "em uma frase objetiva",
    "answer only", "reply only", "answer exactly",
)


def classify_orkio_executive_request(message: Any) -> Dict[str, Any]:
    text = _normalize(message)
    if not text:
        return {
            "version": ORKIO_EXECUTIVE_GUARD_VERSION,
            "force_context_runtime": False,
            "reason": "empty_message",
            "confidence": 0.0,
            "matched_markers": [],
        }

    directives = _matches(text, _DIRECTIVE_MARKERS)
    domains = _matches(text, _BUSINESS_MARKERS)
    structures = _matches(text, _STRUCTURE_MARKERS)
    constrained = _matches(text, _CONSTRAINED_ANSWER_MARKERS)
    numeric_evidence = bool(re.search(r"(?:\d[\d.,]*\s*%|r\$\s*\d|\d[\d.,]*\s*(?:mil|milhao|milhoes))", text))

    # A business domain plus an explicit instruction is the strongest signal.
    # Numeric evidence or requested execution structure also protects concise
    # prompts such as "margem 8%, meta 15%: calcule o gap".
    substantive = bool(
        constrained
        or (directives and domains)
        or (domains and numeric_evidence)
        or (domains and structures)
    )

    if constrained:
        reason = "constrained_answer_request"
        confidence = 0.99
    elif directives and domains:
        reason = "executive_action_on_business_domain"
        confidence = 0.97
    elif domains and numeric_evidence:
        reason = "quantified_business_problem"
        confidence = 0.95
    elif domains and structures:
        reason = "structured_business_problem"
        confidence = 0.92
    else:
        reason = "not_substantive_executive_work"
        confidence = 0.25

    return {
        "version": ORKIO_EXECUTIVE_GUARD_VERSION,
        "force_context_runtime": substantive,
        "reason": reason,
        "confidence": confidence,
        "matched_markers": list(dict.fromkeys(directives + domains + structures + constrained))[:12],
        "numeric_evidence": numeric_evidence,
    }


def executive_fastpath_allowed(decision: Any) -> bool:
    return not bool(
        isinstance(decision, dict) and decision.get("force_context_runtime")
    )
