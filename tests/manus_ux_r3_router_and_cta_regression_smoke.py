from runtime.orkio_executive_guard import eos06_build_router_precedence_payload


R3_SCENARIO_1 = (
    "Sou CEO de uma empresa de tecnologia com 50 funcionários e faturamento de R$12M/ano. "
    "Preciso de uma visão estratégica clara: quais são os 3 principais riscos para meu negócio "
    "nos próximos 12 meses e como devo me preparar para cada um deles?"
)

R3_SCENARIO_2 = (
    "Preciso entender melhor o cenário competitivo do meu setor. Somos uma empresa de SaaS B2B "
    "focada em gestão financeira para PMEs. Quem são os principais players no Brasil, quais "
    "tendências devo observar e como posso me diferenciar?"
)

R3_SCENARIO_3 = (
    "Estou considerando expandir para o mercado mexicano no próximo semestre. Quais fatores devo "
    "avaliar antes de tomar essa decisão? Me ajude a estruturar um framework de decisão para internacionalização."
)

R3_SCENARIO_4 = (
    "Meu VP de Vendas pediu demissão ontem sem aviso prévio e levou 2 gerentes com ele. "
    "Tenho um pipeline de R$3M em risco. O que faço nas próximas 72 horas para estabilizar "
    "a operação comercial?"
)

R3_SCENARIO_5 = (
    "Quais KPIs financeiros e operacionais devo acompanhar semanalmente como CEO de uma SaaS B2B? "
    "Me ajude a montar um dashboard executivo com os indicadores mais relevantes para meu estágio "
    "(Series A, 50 funcionários)."
)


def _assert_no_commercial_cta(payload):
    answer = payload.get("answer", "")
    routing = payload.get("runtime_hints", {}).get("routing", {})
    assert payload.get("commercial_cta_suppressed") is True
    assert routing.get("commercial_cta_suppressed") is True
    assert routing.get("commercial_cta_allowed") is False
    assert "whatsapp" not in answer.lower()
    assert "projeto guiado" not in answer.lower()
    assert "pronto para transformar" not in answer.lower()


def test_r3_risk_strategy_prompt_wins_over_financial_numbers():
    payload = eos06_build_router_precedence_payload(R3_SCENARIO_1)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"
    assert "Risco de crescimento com eficiência" in payload.get("answer", "")
    assert "faltam dados" not in payload.get("answer", "").lower()
    assert "margem operacional atual" not in payload.get("answer", "").lower()
    _assert_no_commercial_cta(payload)


def test_r3_competitive_prompt_routes_to_strategy_without_cta():
    payload = eos06_build_router_precedence_payload(R3_SCENARIO_2)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"
    assert "posicionamento competitivo" in payload.get("answer", "").lower()
    _assert_no_commercial_cta(payload)


def test_r3_internationalization_prompt_routes_to_strategy_without_cta():
    payload = eos06_build_router_precedence_payload(R3_SCENARIO_3)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"
    assert "framework de decisão estratégica" in payload.get("answer", "")
    _assert_no_commercial_cta(payload)


def test_r3_crisis_prompt_routes_to_crisis_without_cta():
    payload = eos06_build_router_precedence_payload(R3_SCENARIO_4)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_crisis_mode"
    assert "Próximas 72 horas" in payload.get("answer", "")
    _assert_no_commercial_cta(payload)


def test_r3_kpi_dashboard_prompt_routes_to_dashboard_without_cta():
    payload = eos06_build_router_precedence_payload(R3_SCENARIO_5)

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_dashboard_mode"
    assert "KPIs recomendados" in payload.get("answer", "")
    _assert_no_commercial_cta(payload)


def test_r3_explicit_financial_calculation_still_calculates():
    payload = eos06_build_router_precedence_payload(
        "Calcule minha margem operacional considerando receita de R$12M e lucro operacional de R$2,4M."
    )

    assert payload.get("handled") is True
    assert payload.get("category") == "quantitative_business_math"
    assert "20,00%" in payload.get("answer", "")


def test_r3_numbers_without_math_words_do_not_trigger_calculator():
    payload = eos06_build_router_precedence_payload(
        "Tenho 50 funcionários e R$12M de faturamento. Devo priorizar expansão internacional ou retenção?"
    )

    assert payload.get("handled") is True
    assert payload.get("category") == "executive_strategy_mode"
    assert "trade-offs" in payload.get("answer", "")
    assert "faltam dados" not in payload.get("answer", "").lower()
