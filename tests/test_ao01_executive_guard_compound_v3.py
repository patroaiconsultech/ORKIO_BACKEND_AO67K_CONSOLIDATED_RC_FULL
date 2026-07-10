from __future__ import annotations

from runtime.orkio_executive_guard import (
    ORKIO_EXECUTIVE_GUARD_VERSION,
    eos06_build_router_precedence_payload,
)


COMPLEX_PROMPT = """
Analise esta empresa SaaS B2B sem fazer perguntas adicionais.

Dados:
- MRR: R$ 720.000
- Margem bruta: 68%
- Despesas fixas mensais: R$ 410.000
- CAC: R$ 24.000
- Ticket médio mensal: R$ 8.000
- Churn mensal: 3,2%
- Expansão de receita mensal: 1,1%
- Novos clientes por mês: 9
- Caixa disponível: R$ 1.600.000
- Dívida: R$ 900.000
- Custo da dívida: 1,3% ao mês

Entregue:
1. diagnóstico executivo;
2. receita líquida após churn e expansão;
3. margem de contribuição;
4. resultado operacional mensal;
5. LTV por duas metodologias;
6. relação LTV/CAC;
7. payback do CAC;
8. impacto do churn;
9. runway;
10. três riscos prioritários;
11. decisão recomendada;
12. plano de ação para 90 dias.

Explique todas as fórmulas, preserve exatamente os números fornecidos e
sinalize qualquer inconsistência matemática.
"""


def test_compound_prompt_is_forced_to_full_llm_runtime() -> None:
    payload = eos06_build_router_precedence_payload(COMPLEX_PROMPT)

    assert ORKIO_EXECUTIVE_GUARD_VERSION == "AO01_EXECUTIVE_GUARD_COMPOUND_V3"
    assert payload["handled"] is False
    assert payload["category"] == "full_llm_runtime_required"
    assert payload["route_family"] == "context_aware_llm_answer"
    assert payload["force_full_llm_runtime"] is True
    assert payload["block_executive_templates"] is True
    assert payload["guard_version"] == "AO01_EXECUTIVE_GUARD_COMPOUND_V3"


def test_simple_financial_calculation_keeps_fast_template() -> None:
    payload = eos06_build_router_precedence_payload(
        "Calcule a margem operacional considerando receita de R$ 100.000 "
        "e lucro operacional de R$ 20.000."
    )

    assert payload["handled"] is True
    assert payload["route_family"] == "executive_quantitative_answer"


def test_simple_strategy_request_keeps_fast_template() -> None:
    payload = eos06_build_router_precedence_payload(
        "Quais são os três principais riscos de uma empresa SaaS B2B?"
    )

    assert payload["handled"] is True
    assert payload["route_family"] == "executive_strategy_answer"
