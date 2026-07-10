from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List

def _norm(text: Any) -> str:
    raw = str(text or "").lower()
    raw = unicodedata.normalize("NFKD", raw)
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    return raw

def ao70_expected_checklist(prompt: Any) -> List[Dict[str, Any]]:
    text = _norm(prompt)
    items: List[Dict[str, Any]] = []

    def add(key: str, label: str, answer_terms: List[str], weight: int = 1):
        if key not in {i["key"] for i in items}:
            items.append({"key": key, "label": label, "answer_terms": answer_terms, "weight": weight})

    if "tese" in text:
        add("thesis", "entregar tese executiva", ["tese", "recomendacao", "recomendação", "decisao", "decisão"], 2)
    if any(t in text for t in ["fatos", "separe fatos"]):
        add("facts", "separar fatos", ["fatos", "dados fornecidos", "informacoes fornecidas", "informações fornecidas"], 1)
    if any(t in text for t in ["inferencias", "inferências"]):
        add("inferences", "separar inferências", ["inferencia", "inferência", "hipotese", "hipótese"], 1)
    if any(t in text for t in ["dados faltantes", "informacoes faltantes", "informações faltantes"]):
        add("missing_data", "declarar dados faltantes", ["dados faltantes", "informacoes faltantes", "informações faltantes", "nao informado", "não informado"], 2)
    if any(t in text for t in ["metricas de decisao", "métricas de decisão", "metricas", "métricas"]):
        add("decision_metrics", "entregar métricas de decisão", ["metrica", "métrica", "kpi", "indicador", "limiar"], 2)
    if any(t in text for t in ["gatilhos de parada", "gatilhos", "stop triggers"]):
        add("stop_triggers", "entregar gatilhos de parada", ["gatilho", "parada", "interromper", "pausar", "stop"], 2)
    if any(t in text for t in ["decisao recomendada", "decisão recomendada", "recomendacao", "recomendação", "recomende"]):
        add("recommendation", "entregar recomendação final", ["recomendo", "recomendacao", "recomendação", "decisao", "decisão"], 2)
    if any(t in text for t in ["proximos passos", "próximos passos"]):
        add("next_steps", "entregar próximos passos", ["proximo", "próximo", "passo", "acao", "ação"], 1)
    if any(t in text for t in ["lucro", "operacional", "ebitda", "resultado"]):
        add("operating_profit", "calcular/explicar lucro operacional ou resultado", ["lucro", "operacional", "ebitda", "resultado", "receita", "custo"], 2)
    if "margem" in text:
        add("margin", "calcular/explicar margem", ["margem", "%", "percentual"], 2)
    if "runway" in text or "caixa" in text or "burn" in text:
        add("runway", "calcular/explicar runway/caixa/burn", ["runway", "caixa", "burn", "meses"], 2)
    if "ltv" in text:
        add("ltv", "calcular/explicar LTV", ["ltv", "lifetime"], 2)
    if "cac" in text:
        add("cac", "calcular/explicar CAC", ["cac", "aquisicao", "aquisição"], 2)
    if "ltv/cac" in text or ("ltv" in text and "cac" in text):
        add("ltv_cac_ratio", "calcular/explicar LTV/CAC", ["ltv/cac", "ltv:cac", "ratio", "relacao", "relação"], 2)
    if "30-60-90" in text or "30 60 90" in text:
        add("plan_30_60_90", "entregar plano 30-60-90", ["30", "60", "90", "dias"], 2)
    if "roadmap" in text:
        add("roadmap", "entregar roadmap", ["roadmap", "fase", "prioridade", "marco"], 1)
    if any(t in text for t in ["risco", "riscos", "restricao", "restrição", "sem captacao", "sem captação"]):
        add("risks_constraints", "tratar riscos e restrições", ["risco", "restricao", "restrição", "mitig", "sem captacao", "sem captação"], 2)
    if any(t in text for t in ["recomende", "recomendacao", "recomendação", "estrategia", "estratégia"]):
        add("recommendations", "entregar recomendações executivas", ["recomendo", "recomendacao", "recomendação", "prioridade", "acao", "ação"], 1)

    # Baseline for executive prompts even when terms are broad.
    if not items and any(t in text for t in ["ceo", "executivo", "diretoria", "investidor", "valuation", "captação", "captacao"]):
        add("executive_summary", "entregar síntese executiva", ["resumo executivo", "diagnostico", "diagnóstico", "prioridade"], 1)
        add("next_steps", "entregar próximos passos", ["proximo", "próximo", "passo", "acao", "ação"], 1)

    return items
