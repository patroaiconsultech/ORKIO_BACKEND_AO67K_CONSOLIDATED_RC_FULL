from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional

AO70_QUALITY_ENGINE_VERSION = "AO70_QUALITY_ENGINE_V1"

_EXECUTIVE_TERMS = {
    "ceo", "cfo", "cto", "executivo", "executiva", "diretoria", "board", "investidor",
    "investidores", "captação", "captacao", "m&a", "valuation", "unit economics",
    "runway", "burn", "mrr", "arr", "churn", "cac", "ltv", "ebitda", "roi", "tir",
    "vpl", "margem", "lucro", "receita", "custos", "opex", "roadmap", "go-to-market",
    "go to market", "plano 30-60-90", "30-60-90", "due diligence", "compliance",
    "risco", "riscos", "restrição", "restricao", "crescer", "crescimento",
}

_DELIVERABLE_TERMS = {
    "calcule", "calcular", "calculo", "cálculo", "analise", "análise", "diagnóstico",
    "diagnostico", "plano", "roadmap", "priorize", "priorização", "recomendações",
    "recomendacoes", "estratégia", "estrategia", "cenário", "cenario", "cenários",
    "cenarios", "projeção", "projecao", "simule", "simulação", "simulacao",
}

_NUMERIC_RE = re.compile(r"(\d+[\d\.,]*\s*(%|k|m|mi|mil|milhões|milhoes|r\$|usd|us\$|meses|dias|anos)?)", re.I)

def _norm(text: Any) -> str:
    raw = str(text or "").lower()
    raw = unicodedata.normalize("NFKD", raw)
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    return raw

def ao70_analyze_intent(message: Any, *, response_control: Optional[str] = None) -> Dict[str, Any]:
    text = _norm(message)
    rc = _norm(response_control)
    numbers = _NUMERIC_RE.findall(text)
    executive_hits = sorted([term for term in _EXECUTIVE_TERMS if term in text])
    deliverable_hits = sorted([term for term in _DELIVERABLE_TERMS if term in text])

    explicit_control = "structured_executive" in rc or "executive_direct" in rc
    high_signal = len(executive_hits) >= 2 and (len(numbers) >= 2 or len(deliverable_hits) >= 2)
    medium_signal = len(executive_hits) >= 1 and len(numbers) >= 3 and len(deliverable_hits) >= 1

    applies = bool(explicit_control or high_signal or medium_signal)
    complexity = "high" if applies and (len(numbers) >= 4 or len(deliverable_hits) >= 3) else ("medium" if applies else "low")

    expected_outputs: List[str] = []
    for key, terms in {
        "financial_calculation": ["calcule", "calcular", "lucro", "margem", "ltv", "cac", "runway", "roi", "tir", "vpl", "ebitda"],
        "risk_assessment": ["risco", "riscos", "compliance", "due diligence", "restricao", "restrição"],
        "roadmap": ["roadmap", "30-60-90", "plano", "priorize", "priorização", "priorizacao"],
        "executive_recommendation": ["recomendacoes", "recomendações", "estrategia", "estratégia", "ceo", "diretoria", "board"],
    }.items():
        if any(_norm(t) in text for t in terms):
            expected_outputs.append(key)

    if applies and not expected_outputs:
        expected_outputs = ["executive_recommendation"]

    return {
        "version": AO70_QUALITY_ENGINE_VERSION,
        "applies": applies,
        "intent": "executive_analysis" if applies else "general_chat",
        "complexity": complexity,
        "explicit_control": explicit_control,
        "numeric_signal_count": len(numbers),
        "executive_hits": executive_hits[:12],
        "deliverable_hits": deliverable_hits[:12],
        "expected_outputs": expected_outputs,
    }

def ao70_should_apply_quality_engine(message: Any, *, response_control: Optional[str] = None) -> bool:
    return bool(ao70_analyze_intent(message, response_control=response_control).get("applies"))
