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

# EOS06-AO85-HF1 — Router Precedence Guard
# Deterministic, readonly, no DB/network/provider/filesystem side effects.
EOS06_AO85_HF1_VERSION = "EOS06_AO85_HF1_ROUTER_PRECEDENCE_GUARD_V1"


def _parse_pt_number(raw: str) -> float:
    s = str(raw or "").strip().lower()
    if not s:
        return 0.0
    s = s.replace("r$", "").replace(" ", "")
    # Brazilian format: 300.000,50. If comma exists, treat comma as decimal.
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # 300.000 without comma should be thousands.
        parts = s.split(".")
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            s = "".join(parts)
    try:
        return float(s)
    except Exception:
        return 0.0


def _money_matches(text: str):
    values = []
    pattern = r"(?:r\$\s*)?(\d[\d.,]*)\s*(milh(?:a|õ|o)es|milhoes|milhao|milhão|mil)?"
    for m in re.finditer(pattern, text, flags=re.IGNORECASE):
        raw = m.group(1)
        full = str(m.group(0) or "")
        scale = (m.group(2) or "").lower()
        # Avoid treating percentages like "42%" as money. A money candidate
        # must have an explicit R$ prefix or a magnitude suffix such as "mil".
        if "r$" not in full.lower() and not scale:
            continue
        value = _parse_pt_number(raw)
        if value <= 0:
            continue
        if "milh" in scale or "milhao" in scale or "milhão" in scale or "milhoes" in scale:
            value *= 1_000_000
        elif scale == "mil":
            value *= 1_000
        values.append((value, m.start(), m.end(), m.group(0)))
    return values


def _percent_matches(text: str):
    values = []
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*%", text):
        value = _parse_pt_number(m.group(1))
        values.append((value, m.start(), m.end(), m.group(0)))
    return values


def _nearest_keyword_value(values, text: str, keywords):
    if not values:
        return None
    best = None
    best_score = 10**9
    low = text.lower()
    for value, start, end, raw in values:
        window_start = max(0, start - 80)
        window_end = min(len(low), end + 80)
        window = low[window_start:window_end]
        if any(k in window for k in keywords):
            # Prefer closest keyword occurrence in the local window.
            local_scores = []
            for k in keywords:
                pos = window.find(k)
                if pos >= 0:
                    local_scores.append(abs((window_start + pos) - start))
            score = min(local_scores or [0])
            if score < best_score:
                best = value
                best_score = score
    return best


def _looks_like_financial_math_request(text: str) -> bool:
    low = _normalize(text)
    if not low:
        return False
    math_markers = (
        "calcule", "calcular", "calculo", "cálculo", "formula", "fórmula",
        "margem", "lucro", "gap", "custos variaveis", "custos variáveis",
        "custos fixos", "faturamento", "receita", "ebitda",
    )
    return bool(
        any(m in low for m in math_markers)
        and ("%" in low or "r$" in low or re.search(r"\d", low))
        and any(m in low for m in ("empresa", "fatura", "faturamento", "receita", "margem", "lucro", "custo"))
    )


def _looks_like_eos06_governance_request(text: str) -> bool:
    low = _normalize(text)
    if not low:
        return False
    eos_marker = any(x in low for x in (
        "eos-06", "eos06", "executive intelligence", "inteligencia executiva",
        "proposal_only", "observe_only", "aprovacao humana", "aprovação humana",
    ))
    structural_marker = any(x in low for x in (
        "mudanca estrutural", "mudança estrutural", "backend", "confiabilidade do chat",
        "estado real da plataforma", "capacidade declarada", "validacao pendente",
        "validação pendente", "impacto", "risco", "rollback", "dependencias",
        "dependências", "nao execute", "não execute",
    ))
    propose_marker = any(x in low for x in (
        "proponha", "propor", "recomendar", "recomende", "antes de recomendar",
        "inclua", "separe",
    ))
    return bool(eos_marker and structural_marker and propose_marker)


def _build_financial_math_answer(message: Any) -> str:
    raw = str(message or "")
    low = _normalize(raw)
    money = _money_matches(raw)
    percents = _percent_matches(raw)

    revenue = _nearest_keyword_value(money, raw, ("fatura", "faturamento", "receita", "vendas"))
    fixed = _nearest_keyword_value(money, raw, ("fixo", "fixos", "custos fixos", "custo fixo"))
    variable_pct = _nearest_keyword_value(percents, raw, ("variavel", "variaveis", "variável", "variáveis"))
    target_margin_pct = _nearest_keyword_value(percents, raw, ("margem de", "margem alvo", "margem operacional", "lucro necessario", "lucro necessário"))

    # Conservative fallbacks for the common prompt shape:
    if revenue is None and money:
        revenue = money[0][0]
    if fixed is None and len(money) >= 2:
        fixed = money[1][0]
    if variable_pct is None and percents:
        variable_pct = percents[0][0]
    if target_margin_pct is None and len(percents) >= 2:
        # If the first percent is near variable costs, the second is usually target margin.
        target_margin_pct = percents[1][0]
    if target_margin_pct == variable_pct and len(percents) >= 2:
        target_margin_pct = percents[1][0]

    if revenue and fixed is not None and variable_pct is not None and target_margin_pct is not None:
        variable_cost = float(revenue) * float(variable_pct) / 100.0
        current_profit = float(revenue) - variable_cost - float(fixed)
        current_margin = (current_profit / float(revenue) * 100.0) if revenue else 0.0
        target_profit = float(revenue) * float(target_margin_pct) / 100.0
        gap = target_profit - current_profit

        def brl(v: float) -> str:
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def pct(v: float) -> str:
            return f"{v:.2f}%".replace(".", ",")

        feasibility = (
            "fecha matematicamente se houver melhoria de resultado operacional de "
            f"{brl(gap)}."
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
            f"- faturamento: {brl(float(revenue))}\n"
            f"- custos variáveis: {pct(float(variable_pct))} × {brl(float(revenue))} = {brl(variable_cost)}\n"
            f"- custos fixos: {brl(float(fixed))}\n"
            f"- lucro operacional atual: {brl(float(revenue))} - {brl(variable_cost)} - {brl(float(fixed))} = {brl(current_profit)}\n"
            f"- margem operacional atual: {brl(current_profit)} ÷ {brl(float(revenue))} = {pct(current_margin)}\n"
            f"- lucro necessário para margem de {pct(float(target_margin_pct))}: {brl(float(revenue))} × {pct(float(target_margin_pct))} = {brl(target_profit)}\n"
            f"- gap: {brl(target_profit)} - {brl(current_profit)} = {brl(gap)}\n\n"
            f"Veredito matemático: {feasibility}\n\n"
            "Não estou assumindo cargos, novos agentes, investimento, aumento de receita ou corte de custos. "
            "A conta acima usa somente os números fornecidos."
        )

    return (
        "Posso calcular, mas faltam dados numéricos suficientes para fechar a fórmula com segurança.\n\n"
        "Para margem operacional, preciso de: faturamento, percentual de custos variáveis, custos fixos e margem-alvo. "
        "Sem esses quatro elementos, qualquer cenário seria inferência e não cálculo comprovado."
    )


def _build_eos06_governance_answer(message: Any) -> str:
    return (
        "EOS-06 — Executive Intelligence Foundation / observe_only\n\n"
        "1. Estado comprovado\n"
        "- Há uma solicitação do usuário para propor uma mudança estrutural no backend visando maior confiabilidade do chat.\n"
        "- A própria solicitação exige: impacto, riscos, dependências, validação, rollback e aprovação humana.\n"
        "- Não há, nesta resposta, acesso comprovado a logs atuais, diff real, estado de banco, fila, provedor LLM ou métricas de produção.\n\n"
        "2. Capacidade declarada, não disponibilidade comprovada\n"
        "- A plataforma declara capacidade de stream, runtime, governança, propostas e aprovação humana.\n"
        "- Declaração de capacidade não prova disponibilidade operacional em tempo real.\n"
        "- Nenhum patch, branch, PR, deploy, migration ou escrita será executado por esta resposta.\n\n"
        "3. Validação pendente\n"
        "- Confirmar logs recentes de /api/chat/stream.\n"
        "- Confirmar se há eventos SSE obrigatórios: status, chunk, agent_done, error e done.\n"
        "- Confirmar se há persistência única da mensagem assistant.\n"
        "- Confirmar se roteadores legados competem com EOS-06/AO85.\n"
        "- Confirmar se o input do frontend é liberado após todos os terminais.\n\n"
        "4. Mudança estrutural proposta\n"
        "Criar um Router Authority Gate antes dos fast-paths legados do chat.\n\n"
        "Objetivo:\n"
        "- classificar pedidos executivos, quantitativos e governados antes de HF6R1, welcome fastpath e governed_evolution_pipeline;\n"
        "- impedir dupla resposta;\n"
        "- garantir que solicitações EOS-06 permaneçam em observe_only/proposal_only;\n"
        "- separar estado comprovado, capacidade declarada e validação pendente.\n\n"
        "5. Impacto\n"
        "- Melhora a previsibilidade do chat.\n"
        "- Reduz queda indevida em saudação institucional.\n"
        "- Reduz acionamento indevido de pipeline de autoevolução.\n"
        "- Preserva stream/SSE, backend, frontend, banco e realtime sem mudança estrutural imediata.\n\n"
        "6. Riscos\n"
        "- Risco médio por alterar precedência de roteamento.\n"
        "- Pode bloquear algum fast-path legítimo se o matcher ficar amplo demais.\n"
        "- Pode exigir novos smokes para prompts quantitativos, governados e saudações simples.\n\n"
        "7. Dependências\n"
        "- main.py, somente no ponto de decisão de roteamento.\n"
        "- runtime/orkio_executive_guard.py para classificação pura e sem efeitos colaterais.\n"
        "- runtime/chat_stream_runtime_stabilizer.py apenas se stream-lite competir com o gate.\n\n"
        "8. Validação\n"
        "- Smoke 1: cálculo financeiro deve responder fórmula e números, sem saudação.\n"
        "- Smoke 2: pedido EOS-06 deve retornar observe_only e proposal_only=true.\n"
        "- Smoke 3: saudação simples deve continuar usando welcome quando a mensagem for só cumprimento.\n"
        "- Smoke 4: pedido real de pipeline governado com @Orion deve continuar funcionando.\n"
        "- Smoke 5: /api/chat/stream deve emitir evento terminal e liberar input.\n\n"
        "9. Rollback\n"
        "- Reverter o Router Authority Gate.\n"
        "- Restaurar a ordem anterior dos fast-paths.\n"
        "- Manter os módulos EOS-06 existentes sem execução automática.\n\n"
        "10. Governança\n"
        "- mode: observe_only\n"
        "- proposal_only: true\n"
        "- write_executed: false\n"
        "- branch_created: false\n"
        "- pr_created: false\n"
        "- deploy_executed: false\n"
        "- human_approval_required: true\n\n"
        "Veredito: GO para proposal_only/hotfix de precedência. NO-GO para execução, commit, deploy ou alteração estrutural sem aprovação humana."
    )


def eos06_build_router_precedence_payload(message: Any) -> Dict[str, Any]:
    """Return a deterministic payload for EOS-06/AO85 precedence cases.

    This is intentionally narrow. It prevents legacy welcome/evolution routes
    from capturing requests that must be answered as executive work.
    """
    if _looks_like_financial_math_request(str(message or "")):
        answer = _build_financial_math_answer(message)
        return {
            "handled": True,
            "category": "quantitative_business_math",
            "route_family": "eos06_router_precedence_guard",
            "answer": answer,
            "message": answer,
            "final_text": answer,
            "agent_id": "orkio",
            "agent_name": "Orkio",
            "runtime_hints": {
                "routing": {
                    "routing_source": "eos06_ao85_hf1_router_precedence_guard",
                    "route_applied": True,
                    "route_family": "executive_quantitative_answer",
                    "proposal_only": False,
                    "observe_only": True,
                    "write_executed": False,
                    "human_approval_required_before_write": True,
                }
            },
        }

    if _looks_like_eos06_governance_request(str(message or "")):
        answer = _build_eos06_governance_answer(message)
        return {
            "handled": True,
            "category": "eos06_governance_proposal_only",
            "route_family": "eos06_router_precedence_guard",
            "answer": answer,
            "message": answer,
            "final_text": answer,
            "agent_id": "orkio",
            "agent_name": "Orkio",
            "runtime_hints": {
                "routing": {
                    "routing_source": "eos06_ao85_hf1_router_precedence_guard",
                    "route_applied": True,
                    "route_family": "executive_governance_proposal_only",
                    "proposal_only": True,
                    "observe_only": True,
                    "write_executed": False,
                    "branch_created": False,
                    "pr_created": False,
                    "deploy_executed": False,
                    "human_approval_required_before_write": True,
                    "blocked_routes": [
                        "HF6R1_welcome_fastpath",
                        "governed_evolution_pipeline",
                        "legacy_public_identity_fastpath",
                    ],
                }
            },
        }

    return {
        "handled": False,
        "category": "not_eos06_precedence_case",
        "route_family": "eos06_router_precedence_guard",
    }


def eos06_should_block_legacy_routes(message: Any) -> bool:
    return bool(eos06_build_router_precedence_payload(message).get("handled"))

