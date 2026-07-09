import json

from runtime.orkio_backend_cta_guard import (
    enforce_backend_cta_policy,
    has_commercial_cta_signature,
    strip_unrequested_commercial_cta,
)
from runtime.orkio_stream_precedence import (
    build_chat_stream_precedence_payload,
    extract_user_message_from_payload,
    iter_manus_ux_r3_1_sse_events,
)


R3_SCENARIO_1 = (
    "Sou CEO de uma empresa de tecnologia com 50 funcionários e faturamento de R$12M/ano. "
    "Preciso de uma visão estratégica clara: quais são os 3 principais riscos para meu negócio "
    "nos próximos 12 meses e como devo me preparar para cada um deles?"
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


def _assert_terminal_payload(payload, category):
    assert payload["handled"] is True
    assert payload["stream_terminal"] is True
    assert payload["route_applied_at_stream_entry"] is True
    assert payload["category"] == category
    assert payload["commercial_cta_allowed"] is False
    assert payload["commercial_cta_suppressed"] is True

    routing = payload["runtime_hints"]["routing"]
    assert routing["route_applied_at_stream_entry"] is True
    assert routing["block_legacy_financial_calculator"] is True
    assert routing["block_default_commercial_cta"] is True
    assert routing["execution_trace_priority"] == "secondary_collapsed"

    answer = payload["answer"].lower()
    assert "whatsapp" not in answer
    assert "projeto guiado" not in answer
    assert "pronto para transformar" not in answer


def test_extracts_last_user_message_from_common_stream_payload():
    payload = {
        "thread_id": "t1",
        "messages": [
            {"role": "assistant", "content": "Olá."},
            {"role": "user", "content": R3_SCENARIO_1},
        ],
    }
    assert extract_user_message_from_payload(payload) == R3_SCENARIO_1


def test_stream_entry_gate_handles_risk_strategy_before_legacy_calculator():
    payload = build_chat_stream_precedence_payload({"message": R3_SCENARIO_1})
    _assert_terminal_payload(payload, "executive_strategy_mode")
    assert "Risco de crescimento com eficiência" in payload["answer"]
    assert "faltam dados" not in payload["answer"].lower()
    assert "margem operacional atual" not in payload["answer"].lower()


def test_stream_entry_gate_handles_crisis_without_commercial_cta():
    payload = build_chat_stream_precedence_payload({"message": R3_SCENARIO_4})
    _assert_terminal_payload(payload, "executive_crisis_mode")
    assert "Próximas 72 horas" in payload["answer"]


def test_stream_entry_gate_handles_dashboard_without_commercial_cta():
    payload = build_chat_stream_precedence_payload({"message": R3_SCENARIO_5})
    _assert_terminal_payload(payload, "executive_dashboard_mode")
    assert "KPIs recomendados" in payload["answer"]


def test_stream_entry_gate_preserves_explicit_financial_calculation():
    payload = build_chat_stream_precedence_payload(
        {
            "message": (
                "Calcule minha margem operacional considerando receita de R$12M "
                "e lucro operacional de R$2,4M."
            )
        }
    )
    _assert_terminal_payload(payload, "quantitative_business_math")
    assert "20,00%" in payload["answer"]


def test_backend_cta_guard_removes_residual_footer_when_not_allowed():
    dirty = (
        "Plano executivo em 3 passos.\n\n"
        "1. Estabilizar liderança.\n"
        "2. Proteger clientes.\n\n"
        "Pronto para transformar isso em projeto guiado?\n"
        "Falar com a equipe no WhatsApp: https://wa.me/5500000000000"
    )
    assert has_commercial_cta_signature(dirty)
    clean = strip_unrequested_commercial_cta(dirty, allow=False)
    assert "Plano executivo em 3 passos." in clean
    assert "Pronto para transformar" not in clean
    assert "WhatsApp" not in clean
    assert "wa.me" not in clean


def test_backend_cta_guard_keeps_cta_only_when_explicitly_allowed():
    dirty_payload = {
        "answer": "Resposta.\n\nFalar com a equipe no WhatsApp: https://wa.me/5500000000000",
        "commercial_cta_allowed": True,
        "runtime_hints": {"routing": {"commercial_cta_allowed": True}},
    }
    clean, changed = enforce_backend_cta_policy(dirty_payload)
    assert changed is False
    assert "WhatsApp" in clean["answer"]
    assert clean["commercial_cta_allowed"] is True


def test_sse_contract_contains_status_chunk_agent_done_and_done():
    payload = build_chat_stream_precedence_payload({"message": R3_SCENARIO_1})
    events = list(iter_manus_ux_r3_1_sse_events(payload))
    assert len(events) == 4
    assert events[0].startswith("event: status")
    assert events[1].startswith("event: chunk")
    assert events[2].startswith("event: agent_done")
    assert events[3].startswith("event: done")

    done_data = events[3].split("data: ", 1)[1].strip()
    parsed = json.loads(done_data)
    assert parsed["handled"] is True
    assert parsed["stream_terminal"] is True
    assert parsed["category"] == "executive_strategy_mode"
