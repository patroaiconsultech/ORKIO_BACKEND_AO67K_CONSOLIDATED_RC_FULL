from .models import Classification
import re
import unicodedata


MANUS_UX_R3_CLASSIFIER_VERSION = "MANUS_UX_R3_INTENT_PRECEDENCE_V1"


def _normalize(value: str) -> str:
    raw = str(value or "").strip().lower()
    try:
        raw = unicodedata.normalize("NFD", raw)
        raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    except Exception:
        pass
    return re.sub(r"\s+", " ", raw).strip()


def _hits(text: str, markers):
    return [marker for marker in markers if marker in text][:12]


def _has_any(text: str, markers) -> bool:
    return any(marker in text for marker in markers)


def classify_message(message: str) -> Classification:
    """Classify a user turn with executive intent before financial math.

    MANUS UX R3 rule:
    - Numbers, revenue, headcount, dates, pipeline value or "R$" alone do not
      make a message a calculation.
    - Calculation is allowed only when the user asks for a computation/formula
      with explicit math intent.
    - Strategic, crisis and dashboard prompts keep ownership even when they
      contain financial context.
    """
    text = _normalize(message)

    explicit_calculation_terms = [
        "calcule", "calcular", "calculo", "calculos", "formula", "formulas",
        "quanto da", "qual e o valor", "qual o valor", "mostre a conta",
        "mostre os calculos", "matematicamente", "porcentagem", "percentual",
        "roi", "payback", "ebitda", "dre", "resultado financeiro",
        "margem operacional considerando", "lucro operacional considerando",
    ]
    finance_context_terms = [
        "fatura", "faturamento", "receita", "custos", "custo", "margem",
        "lucro", "gap", "ebitda", "dre", "roi", "payback",
    ]
    executive_strategy_terms = [
        "risco", "riscos", "proximos 12 meses", "cenario", "cenarios",
        "visao estrategica", "estrategia", "conselho", "expansao", "expandir",
        "decisao", "framework de decisao", "internacionalizacao", "mexico",
        "mercado mexicano", "competitivo", "concorrencia", "players",
        "tendencias", "diferenciar", "preparar", "prioridade", "prioridades",
        "trade-off", "tradeoffs", "trade offs", "ameaca", "ameacas",
        "oportunidade", "oportunidades", "plano de acao", "retencao",
        "internacional", "matriz de decisao", "framework", "como devo me preparar",
    ]
    executive_crisis_terms = [
        "crise", "saiu hoje", "demitiu", "demissao", "sem aviso previo",
        "48 horas", "72 horas", "urgente", "contingencia", "vp de vendas",
        "pediu demissao", "pipeline em risco", "clientes em risco",
        "estabilizar a operacao", "minimizar o impacto",
    ]
    executive_dashboard_terms = [
        "kpis", "kpi", "indicadores", "dashboard", "acompanhar semanalmente",
        "cadencia", "metricas semanais", "benchmarks",
    ]
    governance_terms = [
        "observe_only", "proposal_only", "rollback", "aprovacao humana",
        "nao execute", "não execute",
    ]
    capability_terms = [
        "o que e", "capacidades", "oferece hoje", "roadmap", "producao",
        "beta", "proposta",
    ]
    code_terms = ["alterar codigo", "abrir pr", "deploy", "pull request", "commit"]

    calculation_intent = _has_any(text, explicit_calculation_terms)
    financial_context = _has_any(text, finance_context_terms)

    # Highest-precedence executive paths. These must win over money/headcount.
    if _has_any(text, executive_dashboard_terms):
        return Classification(
            "executive_dashboard_mode",
            0.98,
            _hits(text, executive_dashboard_terms),
        )
    if _has_any(text, executive_crisis_terms):
        return Classification(
            "executive_crisis_mode",
            0.98,
            _hits(text, executive_crisis_terms),
        )
    if _has_any(text, executive_strategy_terms) and not calculation_intent:
        return Classification(
            "executive_strategy_mode",
            0.98,
            _hits(text, executive_strategy_terms),
        )

    # Math only after the executive gates and only with explicit math language.
    if calculation_intent and financial_context:
        return Classification(
            "quantitative_business_math",
            0.96,
            _hits(text, explicit_calculation_terms + finance_context_terms),
        )

    if _has_any(text, governance_terms):
        return Classification("governance_proposal_only", 0.95, _hits(text, governance_terms))
    if _has_any(text, code_terms):
        return Classification("autoevolution_capability_boundary", 0.94, _hits(text, code_terms))
    if _has_any(text, capability_terms):
        return Classification("platform_capability_question", 0.90, _hits(text, capability_terms))

    return Classification("general_executive", 0.70, [])
