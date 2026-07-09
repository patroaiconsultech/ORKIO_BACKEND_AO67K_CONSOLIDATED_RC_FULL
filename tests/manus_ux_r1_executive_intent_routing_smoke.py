from runtime.orkio_executive_guard import eos06_build_router_precedence_payload
from runtime.orkio_kernel import build_orkio_kernel_response


def test_manus_risk_strategy_does_not_trigger_financial_math():
    msg = "Sou CEO de uma SaaS B2B com R$12M/ano. Quais são os 3 principais riscos para os próximos 12 meses?"
    payload = eos06_build_router_precedence_payload(msg)
    answer = payload.get("answer", "")

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"
    assert payload.get("runtime_hints", {}).get("routing", {}).get("commercial_cta_suppressed") is True
    assert "Risco de crescimento com eficiencia" in answer
    assert "margem operacional atual" not in answer.lower()


def test_manus_explicit_financial_calculation_still_routes_to_math():
    msg = "Calcule minha margem operacional considerando receita de R$12M e lucro operacional de R$2,4M."
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "quantitative_business_math"


def test_manus_numbers_without_calculation_route_to_strategy():
    msg = "Tenho 50 funcionários e R$12M de faturamento. Devo priorizar expansão internacional ou retenção?"
    payload = eos06_build_router_precedence_payload(msg)
    answer = payload.get("answer", "")

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"
    assert "trade-offs" in answer
    assert "margem operacional atual" not in answer.lower()


def test_manus_crisis_routes_to_executive_crisis():
    msg = "Meu VP de Vendas saiu hoje. O que devo fazer nas próximas 48 horas?"
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_crisis_mode"
    assert "Proximas 48 horas" in payload.get("answer", "")


def test_manus_kpis_route_to_executive_dashboard():
    msg = "Quais KPIs devo acompanhar semanalmente como CEO de SaaS B2B?"
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_dashboard_mode"
    assert "KPIs recomendados" in payload.get("answer", "")


def test_kernel_classifier_matches_manus_strategy_before_math():
    result = build_orkio_kernel_response(
        "Sou CEO de uma SaaS B2B com R$12M/ano. Quais são os 3 principais riscos para os próximos 12 meses?"
    )

    assert result.classification.category == "executive_strategy_mode"
    assert "Risco de crescimento" in result.response_text


def test_round2_full_risk_prompt_routes_to_strategy():
    msg = (
        "Sou CEO de uma empresa de tecnologia com 50 funcionários e faturamento de R$12M/ano. "
        "Preciso de uma visão estratégica clara: quais são os 3 principais riscos para meu negócio "
        "nos próximos 12 meses e como devo me preparar para cada um deles?"
    )
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"
    assert "Risco de crescimento com eficiencia" in payload.get("answer", "")
    assert "faltam dados" not in payload.get("answer", "").lower()
    assert "margem operacional" not in payload.get("answer", "").lower()


def test_round2_competitive_scenario_routes_to_strategy():
    msg = (
        "Preciso entender melhor o cenário competitivo do meu setor. Somos uma empresa de SaaS B2B "
        "focada em gestão financeira para PMEs. Quem são os principais players no Brasil, quais "
        "tendências devo observar e como posso me diferenciar?"
    )
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"


def test_round2_internationalization_framework_routes_to_strategy():
    msg = (
        "Estou considerando expandir para o mercado mexicano no próximo semestre. Quais fatores devo "
        "avaliar antes de tomar essa decisão? Me ajude a estruturar um framework de decisão para internacionalização."
    )
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"


def test_round2_72h_vp_crisis_routes_to_crisis():
    msg = (
        "Meu VP de Vendas pediu demissão ontem sem aviso prévio. Ele leva consigo relacionamentos-chave "
        "com nossos 3 maiores clientes. Como devo agir nas próximas 72 horas para minimizar o impacto "
        "e qual plano de contingência devo montar?"
    )
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_crisis_mode"


def test_round2_kpi_dashboard_routes_to_dashboard():
    msg = (
        "Quais KPIs financeiros e operacionais devo acompanhar semanalmente como CEO de um SaaS B2B? "
        "Me ajude a montar um dashboard executivo com os indicadores mais relevantes, benchmarks de mercado "
        "e frequência ideal de acompanhamento."
    )
    payload = eos06_build_router_precedence_payload(msg)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_dashboard_mode"
