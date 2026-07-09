from .models import Classification


def classify_message(message: str) -> Classification:
    text = (message or "").lower()
    explicit_calculation_terms = [
        "calcule", "calcular", "calculo", "cálculo", "formula", "fórmula",
        "quanto da", "quanto dá", "porcentagem", "percentual", "roi",
        "payback", "ebitda", "dre", "resultado financeiro",
    ]
    finance_context_terms = [
        "fatura", "faturamento", "receita", "custos", "margem", "lucro",
        "gap",
    ]
    executive_strategy_terms = [
        "riscos", "risco", "proximos 12 meses", "próximos 12 meses",
        "cenario", "cenário", "estrategia", "estratégia", "conselho",
        "expansao", "expansão", "decisao", "decisão", "prioridades",
        "trade-offs", "trade offs", "ameaças", "ameacas", "oportunidades",
        "plano de ação", "plano de acao", "internacional", "retencao",
        "retenção",
    ]
    executive_crisis_terms = ["crise", "saiu hoje", "48 horas", "urgente", "vp de vendas"]
    executive_dashboard_terms = ["kpis", "kpi", "indicadores", "acompanhar semanalmente", "cadencia", "cadência"]
    governance_terms = ["observe_only", "proposal_only", "rollback", "aprovação humana", "aprovacao humana", "não execute", "nao execute"]
    capability_terms = ["o que é", "o que e", "capacidades", "oferece hoje", "roadmap", "produção", "producao", "beta", "proposta"]
    code_terms = ["alterar código", "alterar codigo", "abrir pr", "deploy", "pull request", "commit"]

    if any(t in text for t in executive_dashboard_terms):
        return Classification("executive_dashboard_mode", 0.96, [t for t in executive_dashboard_terms if t in text])
    if any(t in text for t in executive_crisis_terms):
        return Classification("executive_crisis_mode", 0.96, [t for t in executive_crisis_terms if t in text])
    if any(t in text for t in executive_strategy_terms) and not any(t in text for t in explicit_calculation_terms):
        return Classification("executive_strategy_mode", 0.96, [t for t in executive_strategy_terms if t in text])
    if any(t in text for t in explicit_calculation_terms) and any(t in text for t in finance_context_terms):
        return Classification("quantitative_business_math", 0.96, [t for t in explicit_calculation_terms + finance_context_terms if t in text])
    if any(t in text for t in governance_terms):
        return Classification("governance_proposal_only", 0.95, [t for t in governance_terms if t in text])
    if any(t in text for t in code_terms):
        return Classification("autoevolution_capability_boundary", 0.94, [t for t in code_terms if t in text])
    if any(t in text for t in capability_terms):
        return Classification("platform_capability_question", 0.90, [t for t in capability_terms if t in text])
    return Classification("general_executive", 0.70, [])
