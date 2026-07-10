from __future__ import annotations

"""Pure routing guard for substantive executive work.

MANUS UX R3 hardens two production-critical behaviours validated by the R3
user test:
1. qualitative executive prompts with numbers must not be captured by the
   financial-calculation route;
2. commercial CTAs must be opt-in, never a default footer in advisory/crisis
   answers.

No database, network, provider, filesystem, commit, PR or deploy side effects.
"""

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional, Tuple


ORKIO_EXECUTIVE_GUARD_VERSION = "AO01_COMPLEX_PROMPT_BYPASS_V2"
EOS06_AO85_HF2_VERSION = "EOS06_AO85_HF2_EXECUTIVE_TURN_OWNERSHIP_V1"
MANUS_UX_R1_VERSION = "MANUS_UX_R1_EXECUTIVE_INTENT_ROUTING_V1"
MANUS_UX_R3_VERSION = "MANUS_UX_R3_ROUTER_AND_CTA_GUARD_V1"


def _normalize(value: Any) -> str:
    raw = str(value or "").strip().lower()
    try:
        raw = unicodedata.normalize("NFD", raw)
        raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    except Exception:
        pass
    return re.sub(r"\s+", " ", raw).strip()


def _matches(text: str, markers: Iterable[str], limit: int = 12) -> Tuple[str, ...]:
    return tuple(marker for marker in markers if marker in text)[:limit]


def _has_any(text: str, markers: Iterable[str]) -> bool:
    return any(marker in text for marker in markers)



_COMPLEX_PROMPT_BYPASS_MARKERS = (
    "entregue:",
    "crie:",
    "analise de sensibilidade",
    "cenario a:",
    "cenario b:",
    "cenario c:",
    "matriz de prioridades",
    "roadmap de 30",
    "criterios objetivos de go/no-go",
    "indicadores tecnicos",
    "indicadores de produto",
    "riscos e mitigacoes",
    "plano de acao para 90 dias",
    "explique premissas",
    "sinalize qualquer inconsistencia",
    "ltv/cac",
    "payback do cac",
    "impacto do churn",
    "runway",
)


def _has_explicit_complex_prompt_marker(message: Any) -> bool:
    """Detect unequivocal prompts that must bypass deterministic templates.

    The input is normalized before comparison, so the marker list is stored
    without accents. This guard is intentionally simple and precedes all
    executive/dashboard/math fast paths.
    """
    low = _normalize(message)
    if not low:
        return False

    marker_hits = sum(1 for marker in _COMPLEX_PROMPT_BYPASS_MARKERS if marker in low)
    scenario_hits = len(re.findall(r"\bcenario\s+[a-z0-9]+\s*:", low))
    numbered_deliverables = len(
        re.findall(r"(?m)^\s*\d{1,2}[.)]\s+", str(message or ""))
    )

    return bool(
        marker_hits >= 1
        or scenario_hits >= 2
        or numbered_deliverables >= 4
    )


def _requires_full_llm_runtime(message: Any) -> bool:
    """Return True when deterministic templates would under-answer the request.

    The executive guard is intentionally useful for short, narrow and predictable
    requests. It must not take ownership of prompts that require multi-step
    reasoning, several independent deliverables, scenario comparison, sensitivity
    analysis or a complete technical/executive plan.

    This function has no side effects. Returning True means only that the guard
    must fail open so the normal context-aware LLM runtime can answer.
    """
    raw = str(message or "").strip()
    low = _normalize(raw)
    if not low:
        return False

    # Numbered deliverables such as "1.", "2.", ..., or "1)", "2)".
    numbered_items = len(
        re.findall(r"(?m)^\s*(?:\d{1,2}[.)]|[-*]\s+\d{1,2}[.)])\s+", raw)
    )

    # Semicolon-separated or explicitly requested output sections.
    output_markers = _matches(
        low,
        (
            "entregue:", "crie:", "calcule", "compare", "recomende",
            "analise de sensibilidade", "análise de sensibilidade",
            "diagnostico tecnico", "diagnóstico técnico",
            "diagnostico de produto", "diagnóstico de produto",
            "matriz de prioridades", "roadmap de 30", "criterios objetivos",
            "critérios objetivos", "indicadores tecnicos", "indicadores técnicos",
            "indicadores de produto", "riscos e mitigacoes", "riscos e mitigações",
            "plano de acao para 90 dias", "plano de ação para 90 dias",
            "explique premissas", "sinalize qualquer inconsistencia",
            "sinalize qualquer inconsistência",
        ),
        limit=32,
    )

    scenario_count = len(re.findall(r"(?i)\bcen[aá]rio\s+[a-z0-9]", raw))
    financial_terms = _matches(
        low,
        (
            "ltv", "cac", "payback", "runway", "churn", "margem de contribuicao",
            "margem de contribuição", "resultado operacional", "custo de capital",
            "retorno sobre o capital", "ajuste pelo risco", "probabilidade de sucesso",
        ),
        limit=24,
    )

    asks_sensitivity = _has_any(
        low,
        (
            "analise de sensibilidade", "análise de sensibilidade",
            "mais ou menos 10", "+/- 10", "±10",
        ),
    )

    long_structured_prompt = len(raw) >= 500 and (
        numbered_items >= 3 or len(output_markers) >= 3
    )
    multi_deliverable = numbered_items >= 4 or len(output_markers) >= 5
    scenario_analysis = scenario_count >= 2 and (
        asks_sensitivity or len(financial_terms) >= 3
    )
    complex_financial_request = (
        len(financial_terms) >= 4
        and _has_any(low, ("calcule", "calcular", "entregue", "compare"))
    )

    return bool(
        long_structured_prompt
        or multi_deliverable
        or scenario_analysis
        or complex_financial_request
    )


_DIRECTIVE_MARKERS = (
    "analise", "avalie", "compare", "recomende", "diagnostico", "calcule",
    "mostre os calculos", "estruture", "elabore", "proponha", "priorize",
    "roadmap", "plano de acao", "primeiro passo", "proximo passo",
    "como melhorar", "como aumentar", "como reduzir", "como escalar",
    "prepare minha empresa", "simule", "projete", "quantifique", "decida",
    "analyze", "evaluate", "compare", "recommend", "diagnose", "calculate",
    "action plan", "first step", "next step", "how to improve",
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

_EXECUTIVE_STRATEGY_MARKERS = (
    "risco", "riscos", "proximos 12 meses", "cenario", "cenarios",
    "visao estrategica", "estrategia", "conselho", "expansao", "expandir",
    "decisao", "framework de decisao", "internacionalizacao", "mexico",
    "mercado mexicano", "competitivo", "competitiva", "concorrencia",
    "concorrente", "concorrentes", "players",
    "tendencias", "diferenciar", "preparar", "prioridade", "prioridades",
    "trade-off", "tradeoffs", "trade offs", "ameaca", "ameacas",
    "oportunidade", "oportunidades", "plano de acao", "retencao",
    "internacional", "matriz de decisao", "framework", "como devo me preparar",
    "reposicionar", "posicionamento", "series b", "series a",
)

_EXECUTIVE_CRISIS_MARKERS = (
    "crise", "saiu hoje", "demitiu", "demissao", "renunciou",
    "sem aviso previo", "48 horas", "72 horas", "urgente", "contingencia",
    "vp de vendas", "pediu demissao", "pipeline em risco",
    "clientes em risco", "estabilizar a operacao", "minimizar o impacto",
)

_EXECUTIVE_DASHBOARD_MARKERS = (
    "kpi", "kpis", "indicadores", "dashboard", "acompanhar semanalmente",
    "cadencia", "metricas semanais", "benchmarks",
)

_EXPLICIT_MATH_MARKERS = (
    "calcule", "calcular", "calculo", "calculos", "formula", "formulas",
    "mostre a formula", "mostre os calculos", "quanto da", "qual e o valor",
    "qual o valor", "porcentagem", "percentual", "roi", "payback", "ebitda",
    "dre", "resultado financeiro", "matematicamente",
    "margem operacional considerando", "lucro operacional considerando",
)

_FINANCE_CONTEXT_MARKERS = (
    "empresa", "fatura", "faturamento", "receita", "margem", "lucro",
    "custo", "custos", "ebitda", "dre", "roi", "payback", "gap",
)

_HUMAN_HELP_INTENT_MARKERS = (
    "quero falar com", "falar com a equipe", "falar com alguem",
    "atendimento humano", "suporte humano", "qual e o whatsapp",
    "me chama no whatsapp", "chamar no whatsapp", "mandar whatsapp",
    "contratar", "contratacao", "preco", "custos de implantacao",
    "custo de implantacao", "custos de implementacao", "custo de implementacao",
    "talk to the team", "talk to a human", "human support", "pricing",
    "implementation cost",
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
    numeric_evidence = bool(re.search(r"(?:\d[\d.,]*\s*%|r\$\s*\d|\d[\d.,]*\s*(?:m|mi|mil|milhao|milhoes))", text))

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
    return not bool(isinstance(decision, dict) and decision.get("force_context_runtime"))


def _parse_pt_number(raw: str) -> float:
    s = str(raw or "").strip().lower().replace("r$", "").replace(" ", "")
    if not s:
        return 0.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        parts = s.split(".")
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            s = "".join(parts)
    try:
        return float(s)
    except Exception:
        return 0.0


def _money_matches(text: str) -> List[Tuple[float, int, int, str]]:
    values: List[Tuple[float, int, int, str]] = []
    pattern = r"(?:r\$\s*)?(\d+(?:[\.,]\d+)?)\s*(m|mi|mm|milh(?:a|o|õ)es|milhoes|milhao|milhão|mil)?(?:/ano)?"
    for m in re.finditer(pattern, str(text or ""), flags=re.IGNORECASE):
        raw = m.group(1)
        full = str(m.group(0) or "")
        scale = _normalize(m.group(2) or "")
        low_full = _normalize(full)

        # Money candidates need R$ or an explicit magnitude suffix.
        if "r$" not in low_full and not scale:
            continue

        value = _parse_pt_number(raw)
        if value <= 0:
            continue
        if scale in {"m", "mi", "mm"} or "milh" in scale or "milhao" in scale or "milhoes" in scale:
            value *= 1_000_000
        elif scale == "mil":
            value *= 1_000
        values.append((value, m.start(), m.end(), m.group(0)))
    return values


def _percent_matches(text: str) -> List[Tuple[float, int, int, str]]:
    values: List[Tuple[float, int, int, str]] = []
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*%", str(text or "")):
        values.append((_parse_pt_number(m.group(1)), m.start(), m.end(), m.group(0)))
    return values


def _nearest_keyword_value(values, text: str, keywords: Iterable[str]) -> Optional[float]:
    if not values:
        return None
    best = None
    best_score = 10**9
    low = _normalize(text)
    normalized_keywords = tuple(_normalize(k) for k in keywords)
    for value, start, end, raw in values:
        window_start = max(0, start - 90)
        window_end = min(len(low), end + 90)
        window = low[window_start:window_end]
        local_scores = []
        for k in normalized_keywords:
            search_from = 0
            while True:
                pos = window.find(k, search_from)
                if pos < 0:
                    break
                absolute_pos = window_start + pos
                # In phrases like "lucro operacional de R$2,4M", the label is
                # expected before the value. Penalize labels that appear only
                # after a previous money value, otherwise revenue can be
                # incorrectly reused as operating profit.
                after_value_penalty = 500 if absolute_pos > start else 0
                local_scores.append(abs(absolute_pos - start) + after_value_penalty)
                search_from = pos + len(k)
        if local_scores:
            score = min(local_scores)
            if score < best_score:
                best = value
                best_score = score
    return best


def _looks_like_financial_math_request(text: Any) -> bool:
    """Numbers alone must not trigger financial math."""
    low = _normalize(text)
    if not low:
        return False

    if _looks_like_executive_dashboard_request(low):
        return False
    if _looks_like_executive_crisis_request(low):
        return False
    if _looks_like_executive_strategy_request(low):
        return False

    return bool(
        _has_any(low, _EXPLICIT_MATH_MARKERS)
        and ("%" in low or "r$" in low or re.search(r"\d", low))
        and _has_any(low, _FINANCE_CONTEXT_MARKERS)
    )


def _looks_like_executive_strategy_request(text: Any) -> bool:
    low = _normalize(text)
    if not low:
        return False
    if _has_any(low, _EXPLICIT_MATH_MARKERS) and _has_any(low, ("calcule", "calcular", "formula", "quanto da", "qual e o valor")):
        return False
    executive_markers = (
        "ceo", "founder", "fundador", "diretor", "lideranca", "saas",
        "b2b", "empresa", "negocio", "faturamento", "funcionarios",
        "mercado", "setor", "pme", "pmes",
    )
    return bool(
        _has_any(low, _EXECUTIVE_STRATEGY_MARKERS)
        and (_has_any(low, executive_markers) or "?" in str(text or ""))
    )


def _looks_like_executive_crisis_request(text: Any) -> bool:
    low = _normalize(text)
    if not low:
        return False
    crisis_domain = (
        "vp", "diretor", "ceo", "lider", "vendas", "operacao",
        "equipe", "clientes", "pipeline", "gerentes", "relacionamentos",
    )
    return bool(_has_any(low, _EXECUTIVE_CRISIS_MARKERS) and _has_any(low, crisis_domain))


def _looks_like_executive_dashboard_request(text: Any) -> bool:
    low = _normalize(text)
    if not low:
        return False
    return bool(
        _has_any(low, _EXECUTIVE_DASHBOARD_MARKERS)
        and _has_any(low, ("ceo", "saas", "b2b", "empresa", "negocio", "series a", "operacionais", "financeiros"))
    )


def _looks_like_eos06_governance_request(text: Any) -> bool:
    low = _normalize(text)
    if not low:
        return False
    eos_marker = _has_any(low, (
        "eos-06", "eos06", "executive intelligence", "inteligencia executiva",
        "proposal_only", "observe_only", "aprovacao humana",
    ))
    structural_marker = _has_any(low, (
        "mudanca estrutural", "backend", "confiabilidade do chat",
        "estado real da plataforma", "o que voce sabe", "capacidade declarada",
        "precisa ser verificado", "validacao pendente", "impacto", "risco",
        "rollback", "dependencias", "nao execute",
    ))
    propose_marker = _has_any(low, ("proponha", "propor", "recomendar", "recomende", "inclua", "separe"))
    return bool(eos_marker and structural_marker and propose_marker)


def _human_help_intent(text: Any) -> bool:
    return _has_any(_normalize(text), _HUMAN_HELP_INTENT_MARKERS)


def _brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v: float) -> str:
    return f"{v:.2f}%".replace(".", ",")


def _build_financial_math_answer(message: Any) -> str:
    raw = str(message or "")
    money = _money_matches(raw)
    percents = _percent_matches(raw)

    revenue = _nearest_keyword_value(money, raw, ("fatura", "faturamento", "receita", "vendas"))
    operating_profit = _nearest_keyword_value(money, raw, ("lucro operacional", "lucro", "resultado operacional"))
    fixed = _nearest_keyword_value(money, raw, ("fixo", "fixos", "custos fixos", "custo fixo"))
    variable_pct = _nearest_keyword_value(percents, raw, ("variavel", "variaveis", "custos variaveis", "custo variavel"))
    target_margin_pct = _nearest_keyword_value(percents, raw, ("margem de", "margem alvo", "margem operacional", "lucro necessario"))

    if revenue is None and money:
        revenue = money[0][0]
    if operating_profit is None and len(money) >= 2 and _has_any(_normalize(raw), ("lucro operacional", "lucro")):
        operating_profit = money[1][0]

    # Common explicit prompt: "Calcule minha margem operacional considerando receita X e lucro operacional Y".
    if revenue and operating_profit is not None and _has_any(_normalize(raw), ("margem", "lucro operacional")):
        margin = (float(operating_profit) / float(revenue) * 100.0) if revenue else 0.0
        return (
            "Cálculo objetivo.\n\n"
            "Fórmula:\n"
            "- margem operacional = lucro operacional ÷ receita\n\n"
            "Aplicação:\n"
            f"- receita: {_brl(float(revenue))}\n"
            f"- lucro operacional: {_brl(float(operating_profit))}\n"
            f"- margem operacional: {_brl(float(operating_profit))} ÷ {_brl(float(revenue))} = {_pct(margin)}\n\n"
            "Veredito matemático: a margem operacional informada é "
            f"{_pct(margin)}. A conta usa somente os números fornecidos."
        )

    if fixed is None and len(money) >= 2:
        fixed = money[1][0]
    if variable_pct is None and percents:
        variable_pct = percents[0][0]
    if target_margin_pct is None and len(percents) >= 2:
        target_margin_pct = percents[1][0]
    if target_margin_pct == variable_pct and len(percents) >= 2:
        target_margin_pct = percents[1][0]

    if revenue and fixed is not None and variable_pct is not None and target_margin_pct is not None:
        variable_cost = float(revenue) * float(variable_pct) / 100.0
        current_profit = float(revenue) - variable_cost - float(fixed)
        current_margin = (current_profit / float(revenue) * 100.0) if revenue else 0.0
        target_profit = float(revenue) * float(target_margin_pct) / 100.0
        gap = target_profit - current_profit
        feasibility = (
            "fecha matematicamente se houver melhoria de resultado operacional de "
            f"{_brl(gap)}."
            if gap > 0
            else "já fecha matematicamente para a margem alvo informada."
        )
        return (
            "Cálculo objetivo.\n\n"
            "Fórmulas:\n"
            "- custo variável = faturamento × percentual de custos variáveis\n"
            "- lucro operacional atual = faturamento - custo variável - custos fixos\n"
            "- margem operacional atual = lucro operacional atual ÷ faturamento\n"
            "- lucro-alvo = faturamento × margem-alvo\n"
            "- gap = lucro-alvo - lucro operacional atual\n\n"
            "Aplicação:\n"
            f"- faturamento: {_brl(float(revenue))}\n"
            f"- custos variáveis: {_pct(float(variable_pct))} × {_brl(float(revenue))} = {_brl(variable_cost)}\n"
            f"- custos fixos: {_brl(float(fixed))}\n"
            f"- lucro operacional atual: {_brl(float(revenue))} - {_brl(variable_cost)} - {_brl(float(fixed))} = {_brl(current_profit)}\n"
            f"- margem operacional atual: {_brl(current_profit)} ÷ {_brl(float(revenue))} = {_pct(current_margin)}\n"
            f"- lucro necessário para margem de {_pct(float(target_margin_pct))}: {_brl(float(revenue))} × {_pct(float(target_margin_pct))} = {_brl(target_profit)}\n"
            f"- gap: {_brl(target_profit)} - {_brl(current_profit)} = {_brl(gap)}\n\n"
            f"Veredito matemático: {feasibility}\n\n"
            "Não estou assumindo cargos, novos agentes, investimento, aumento de receita ou corte de custos. "
            "A conta acima usa somente os números fornecidos."
        )

    return (
        "Posso calcular, mas faltam dados numéricos suficientes para fechar a fórmula com segurança.\n\n"
        "Informe a fórmula desejada e os valores necessários. Números de contexto, como faturamento, "
        "headcount ou pipeline, não serão tratados como cálculo sem pedido explícito."
    )


def _build_eos06_governance_answer(message: Any) -> str:
    return (
        "EOS-06 — Executive Intelligence Foundation / observe_only\n\n"
        "1. Estado comprovado\n"
        "- Há uma solicitação do usuário para propor uma mudança estrutural no backend visando maior confiabilidade do chat.\n"
        "- Não há, nesta resposta, acesso comprovado a logs atuais, diff real, estado de banco, fila, provedor LLM ou métricas de produção.\n\n"
        "2. Capacidade declarada, não disponibilidade comprovada\n"
        "- A plataforma declara capacidade de stream, runtime, governança, propostas e aprovação humana.\n"
        "- Nenhum patch, branch, PR, deploy, migration ou escrita será executado por esta resposta.\n\n"
        "3. Validação pendente\n"
        "- Confirmar logs recentes de /api/chat/stream.\n"
        "- Confirmar se há eventos SSE obrigatórios: status, chunk, agent_done, error e done.\n"
        "- Confirmar persistência única da mensagem assistant.\n"
        "- Confirmar se roteadores legados competem com EOS-06/AO85.\n"
        "- Confirmar se o input do frontend é liberado após todos os terminais.\n\n"
        "4. Mudança estrutural proposta\n"
        "- Criar um Router Authority Gate antes dos fast-paths legados do chat.\n"
        "- Classificar pedidos executivos, quantitativos e governados antes de templates públicos, welcome fastpath e pipeline de evolução.\n\n"
        "5. Governança\n"
        "- mode: observe_only\n"
        "- proposal_only: true\n"
        "- write_executed: false\n"
        "- branch_created: false\n"
        "- pr_created: false\n"
        "- deploy_executed: false\n"
        "- human_approval_required: true\n\n"
        "Veredito: GO para proposal_only/hotfix de precedência. NO-GO para execução, commit, deploy ou alteração estrutural sem aprovação humana."
    )


def _build_executive_strategy_answer(message: Any) -> str:
    low = _normalize(message)

    if _has_any(low, ("competitivo", "competitiva", "concorrencia", "concorrente", "concorrentes", "players", "tendencias", "diferenciar", "reposicionar", "posicionamento", "series b", "series a")):
        return (
            "Diagnóstico breve: esta é uma decisão de posicionamento competitivo, não um cálculo financeiro.\n\n"
            "1. Mapeie o campo competitivo\n"
            "- Sinal de alerta: comparar apenas preço e ignorar canal, ICP, implementação e retenção.\n"
            "- Ação recomendada: separar concorrentes diretos, substitutos manuais e soluções enterprise que descem para PME.\n\n"
            "2. Observe tendências de pressão\n"
            "- Sinal de alerta: IA, embedded finance, open finance e automação reduzindo diferenciais superficiais.\n"
            "- Ação recomendada: medir onde sua solução reduz tempo, risco e custo operacional para o cliente.\n\n"
            "3. Defina uma diferenciação defensável\n"
            "- Sinal de alerta: discurso amplo demais, sem prova de valor por segmento.\n"
            "- Ação recomendada: escolher um ICP prioritário e provar ganho em onboarding, fechamento contábil, cobrança, caixa ou decisão financeira.\n\n"
            "Próximo passo sugerido: montar uma matriz com players, ICP atendido, promessa central, pricing, canal e prova de ROI."
        )

    if _has_any(low, ("retencao", "priorizar")):
        return (
            "Diagnóstico breve: há números no contexto, mas a pergunta pede escolha estratégica, não cálculo.\n\n"
            "Prioridades e trade-offs:\n"
            "1. Retenção protege receita, margem de manobra e aprendizado do cliente.\n"
            "2. Expansão internacional aumenta opcionalidade, mas eleva complexidade comercial, jurídica e operacional.\n"
            "3. A decisão deve depender de sinais de repetibilidade: ICP claro, churn sob controle, payback previsível e time capaz de executar sem dispersão.\n\n"
            "Sinais de alerta: churn crescendo, suporte saturado, pipeline local inconsistente ou liderança sem foco.\n\n"
            "Ação recomendada: priorizar retenção se a base ainda não é previsível; testar expansão com aposta limitada se a máquina local já for repetível.\n\n"
            "Próximo passo sugerido: montar uma matriz de decisão com impacto, risco, prazo e capacidade interna."
        )

    if _has_any(low, ("internacional", "internacionalizacao", "mexico", "mercado mexicano", "expandir")):
        return (
            "Diagnóstico breve: há números no contexto, mas a pergunta pede framework de decisão estratégica, não cálculo financeiro.\n\n"
            "1. Atratividade do mercado\n"
            "- Avalie TAM/SAM realista, dor local, maturidade digital, concorrentes e disposição de pagamento.\n\n"
            "2. Prontidão operacional\n"
            "- Verifique suporte, idioma, compliance, billing, integrações fiscais/financeiras e capacidade de implantação remota.\n\n"
            "3. Estratégia de entrada\n"
            "- Compare piloto com parceiros, venda direta, canal local ou expansão por clientes já multinacionais.\n\n"
            "4. Risco financeiro e foco\n"
            "- Defina orçamento máximo, hipótese de payback, métricas de tração e ponto de parada.\n\n"
            "Sinais de alerta: churn local ainda alto, ICP indefinido, liderança sem folga ou dependência de customizações pesadas.\n\n"
            "Próximo passo sugerido: aprovar um piloto limitado com critérios de go/no-go antes de comprometer expansão ampla."
        )

    return (
        "Diagnóstico breve: esta é uma pergunta executiva aberta. Vou tratar como decisão estratégica, "
        "não como cálculo financeiro, porque não houve pedido explícito de fórmula ou porcentagem.\n\n"
        "1. Risco de crescimento com eficiência\n"
        "- Sinal de alerta: CAC subindo, churn estável ou expansão abaixo do esperado.\n"
        "- Ação recomendada: revisar ICP, payback, canais e eficiência comercial.\n\n"
        "2. Risco de concentração de receita\n"
        "- Sinal de alerta: dependência excessiva de poucos clientes, canais ou segmentos.\n"
        "- Ação recomendada: mapear concentração e criar plano de diversificação.\n\n"
        "3. Risco de execução organizacional\n"
        "- Sinal de alerta: liderança sobrecarregada, gaps de gestão ou lentidão em produto.\n"
        "- Ação recomendada: definir cadência executiva, ownership e métricas semanais.\n\n"
        "Próximo passo sugerido: transformar estes riscos em um plano de ação de 30/60/90 dias."
    )


def _build_executive_crisis_answer(message: Any) -> str:
    return (
        "Diagnóstico breve: isto é uma crise executiva de continuidade comercial. A prioridade é proteger clientes, pipeline e moral do time antes de discutir qualquer projeto novo.\n\n"
        "Próximas 72 horas:\n"
        "1. Estabilizar comando: nomeie um responsável interino por vendas ainda hoje.\n"
        "2. Proteger pipeline: classifique oportunidades por valor, data de fechamento, decisor e risco de perda.\n"
        "3. Blindar clientes-chave: defina quem falará com cada conta crítica e prepare mensagem de continuidade.\n"
        "4. Preservar informação: centralize CRM, forecast, playbooks, propostas, acordos pendentes e histórico de negociação.\n"
        "5. Reorganizar cadência: faça checkpoint diário por 2 semanas com funil, riscos, decisões e donos.\n\n"
        "Sinais de alerta: vendedores sem direção, forecast opaco, clientes-chave inseguros ou propostas paradas sem owner.\n\n"
        "Próximo passo sugerido: fazer hoje uma reunião de 30 minutos com liderança e donos do pipeline para redistribuir contas e próximos contatos."
    )


def _build_executive_dashboard_answer(message: Any) -> str:
    return (
        "Diagnóstico breve: para CEO de SaaS B2B em estágio Series A, o dashboard semanal deve conectar crescimento, eficiência, retenção e execução.\n\n"
        "KPIs recomendados:\n"
        "1. Receita: MRR/ARR, new MRR, expansion MRR, contraction MRR e churn MRR.\n"
        "2. Comercial: pipeline qualificado, cobertura de pipeline, win rate, ciclo de venda, CAC e payback.\n"
        "3. Cliente: logo churn, NRR, ativação, uso do produto, health score e tickets críticos.\n"
        "4. Produto: entregas-chave, bugs críticos, tempo até valor e adoção de features essenciais.\n"
        "5. Execução: prioridades da semana, owners, bloqueios, decisões pendentes e capacidade do time.\n\n"
        "Sinais de alerta: crescimento sem retenção, pipeline inflado, CAC subindo, NRR abaixo do esperado ou time sem owners claros.\n\n"
        "Próximo passo sugerido: criar uma reunião semanal de 45 minutos em que cada desvio tenha decisão, responsável e prazo."
    )


def _routing_hints(route_family: str, turn_owner: str, *, commercial_cta_allowed: bool = False, proposal_only: bool = False) -> Dict[str, Any]:
    return {
        "routing_source": MANUS_UX_R3_VERSION,
        "route_applied": True,
        "route_family": route_family,
        "turn_owner": turn_owner,
        "block_public_deterministic_fastpaths": True,
        "proposal_only": bool(proposal_only),
        "observe_only": True,
        "write_executed": False,
        "commercial_cta_allowed": bool(commercial_cta_allowed),
        "commercial_cta_suppressed": not bool(commercial_cta_allowed),
        "execution_trace_priority": "secondary_collapsed",
        "human_approval_required_before_write": True,
    }


def _payload(category: str, route_family: str, answer: str, *, turn_owner: str = "MANUS_UX_R3", commercial_cta_allowed: bool = False, proposal_only: bool = False) -> Dict[str, Any]:
    return {
        "handled": True,
        "category": category,
        "route_family": route_family,
        "answer": answer,
        "message": answer,
        "final_text": answer,
        "agent_id": "orkio",
        "agent_name": "Orkio",
        "commercial_cta_allowed": bool(commercial_cta_allowed),
        "commercial_cta_suppressed": not bool(commercial_cta_allowed),
        "execution_trace_priority": "secondary_collapsed",
        "runtime_hints": {
            "routing": _routing_hints(
                route_family,
                turn_owner,
                commercial_cta_allowed=commercial_cta_allowed,
                proposal_only=proposal_only,
            )
        },
    }


def eos06_build_router_precedence_payload(message: Any) -> Dict[str, Any]:
    """Return a deterministic payload for precedence cases.

    Important integration rule:
    call this gate before legacy financial calculators, public welcome
    fast-paths, smart CTA decorators and governed evolution triggers.
    """
    raw_message = str(message or "")

    # AO-01 HOTFIX V2: explicit complex markers take precedence over every
    # deterministic executive/dashboard/math template. The broader heuristic
    # remains as a secondary safety net.
    if (
        _has_explicit_complex_prompt_marker(raw_message)
        or _requires_full_llm_runtime(raw_message)
    ):
        return {
            "handled": False,
            "category": "full_llm_runtime_required",
            "route_family": "context_aware_llm_answer",
            "commercial_cta_allowed": False,
            "commercial_cta_suppressed": True,
            "runtime_hints": {
                "routing": {
                    **_routing_hints(
                        "full_llm_runtime_required",
                        "AO01_COMPLEX_PROMPT_BYPASS_V1",
                    ),
                    "bypass_reason": "complex_multi_deliverable_prompt",
                    "blocked_routes": [
                        "executive_strategy_answer",
                        "executive_quantitative_answer",
                        "executive_dashboard_answer",
                    ],
                }
            },
        }

    if _human_help_intent(raw_message):
        # This does not create a sales answer by itself. It only allows the UI
        # to render contact affordances if the normal assistant answer includes
        # a WhatsApp link after explicit user intent.
        return {
            "handled": False,
            "category": "explicit_human_help_intent",
            "route_family": "manus_ux_r3_cta_allowance",
            "commercial_cta_allowed": True,
            "commercial_cta_suppressed": False,
            "runtime_hints": {"routing": _routing_hints("explicit_human_help_intent", "MANUS_UX_R3", commercial_cta_allowed=True)},
        }

    # Executive routes first. This is the core R3 fix.
    if _looks_like_executive_dashboard_request(raw_message):
        return _payload(
            "executive_dashboard_mode",
            "executive_dashboard_answer",
            _build_executive_dashboard_answer(message),
        )

    if _looks_like_executive_crisis_request(raw_message):
        return _payload(
            "executive_crisis_mode",
            "executive_crisis_answer",
            _build_executive_crisis_answer(message),
        )

    if _looks_like_executive_strategy_request(raw_message):
        return _payload(
            "executive_strategy_mode",
            "executive_strategy_answer",
            _build_executive_strategy_answer(message),
        )

    if _looks_like_financial_math_request(raw_message):
        return _payload(
            "quantitative_business_math",
            "executive_quantitative_answer",
            _build_financial_math_answer(message),
            turn_owner="EOS06_AO85",
        )

    if _looks_like_eos06_governance_request(raw_message):
        payload = _payload(
            "eos06_governance_proposal_only",
            "executive_governance_proposal_only",
            _build_eos06_governance_answer(message),
            turn_owner="EOS06_AO85",
            proposal_only=True,
        )
        payload["runtime_hints"]["routing"]["blocked_routes"] = [
            "HF6R1_welcome_fastpath",
            "governed_evolution_pipeline",
            "legacy_public_identity_fastpath",
        ]
        return payload

    return {
        "handled": False,
        "category": "not_eos06_precedence_case",
        "route_family": "eos06_executive_turn_ownership_guard",
        "commercial_cta_allowed": False,
        "commercial_cta_suppressed": True,
    }


def eos06_should_block_legacy_routes(message: Any) -> bool:
    return bool(eos06_build_router_precedence_payload(message).get("handled"))


def manus_ux_r3_router_precedence_payload(message: Any) -> Dict[str, Any]:
    """Alias with explicit R3 name for new integrations."""
    return eos06_build_router_precedence_payload(message)


def manus_ux_r3_should_block_legacy_routes(message: Any) -> bool:
    return eos06_should_block_legacy_routes(message)
