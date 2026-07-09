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
