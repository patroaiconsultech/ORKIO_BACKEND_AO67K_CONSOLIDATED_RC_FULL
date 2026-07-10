from __future__ import annotations

from runtime.orkio_executive_guard import eos06_build_router_precedence_payload


COMPLEX_FINANCIAL = """
Analise esta empresa SaaS B2B sem me fazer perguntas adicionais.

Dados:
- Receita mensal: R$ 350.000
- Margem bruta: 60%
- Despesas fixas mensais: R$ 280.000
- Churn mensal: 4%
- CAC: R$ 12.000
- Ticket médio mensal: R$ 4.000
- Prazo médio de permanência: 18 meses
- Crescimento de novos clientes: 8 por mês
- Caixa disponível: R$ 900.000
- Dívida: R$ 1.200.000
- Custo da dívida: 1,4% ao mês

Entregue:
1. diagnóstico executivo;
2. margem de contribuição;
3. resultado operacional estimado;
4. LTV nominal;
5. relação LTV/CAC;
6. payback do CAC;
7. impacto do churn;
8. runway;
9. três riscos prioritários;
10. decisão recomendada;
11. plano de ação para 90 dias.

Explique premissas e sinalize qualquer inconsistência matemática.
"""

SCENARIO_SENSITIVITY = """
Uma empresa possui três alternativas para os próximos 12 meses:

Cenário A:
- investimento inicial: R$ 1.500.000
- receita esperada: R$ 3.000.000
- margem operacional: 22%
- probabilidade de sucesso: 70%

Cenário B:
- investimento inicial: R$ 800.000
- receita esperada: R$ 1.900.000
- margem operacional: 30%
- probabilidade de sucesso: 55%

Cenário C:
- investimento inicial: R$ 2.200.000
- receita esperada: R$ 5.500.000
- margem operacional: 18%
- probabilidade de sucesso: 40%

Considere custo de capital de 15% ao ano.

Calcule o resultado operacional esperado, ajuste pelo risco, compare retorno
sobre o capital investido e recomende uma alternativa. Depois faça uma análise
de sensibilidade alterando cada probabilidade em mais ou menos 10 pontos percentuais.
"""

COMPLEX_EXECUTIVE = """
Atue como conselho executivo de uma plataforma de inteligência artificial B2B.

A plataforma possui:
- chat com agentes;
- múltiplos tenants;
- upload de arquivos;
- voz;
- streaming SSE;
- painel administrativo;
- integração futura com WhatsApp;
- memória persistente;
- orquestração entre agentes.

Problemas atuais:
- histórico de patches sucessivos;
- risco de regressão;
- documentação incompleta;
- dependência de um arquivo principal muito grande;
- observabilidade insuficiente;
- experiência de voz ainda não premium;
- necessidade de demonstrar a plataforma para investidores.

Crie:
1. diagnóstico técnico;
2. diagnóstico de produto;
3. matriz de prioridades P0, P1 e P2;
4. roadmap de 30, 60 e 90 dias;
5. critérios objetivos de GO/NO-GO;
6. indicadores técnicos;
7. indicadores de produto;
8. riscos e mitigações;
9. recomendação final para apresentação a investidores.

Não misture correções de estabilidade com melhorias premium.
"""


def _assert_full_runtime(prompt: str) -> None:
    payload = eos06_build_router_precedence_payload(prompt)
    assert payload["handled"] is False
    assert payload["category"] == "full_llm_runtime_required"
    assert payload["route_family"] == "context_aware_llm_answer"


def test_complex_financial_bypasses_templates() -> None:
    _assert_full_runtime(COMPLEX_FINANCIAL)


def test_scenario_sensitivity_bypasses_templates() -> None:
    _assert_full_runtime(SCENARIO_SENSITIVITY)


def test_complex_executive_bypasses_templates() -> None:
    _assert_full_runtime(COMPLEX_EXECUTIVE)


def test_short_narrow_strategy_still_uses_template() -> None:
    payload = eos06_build_router_precedence_payload(
        "Quais são os três principais riscos de uma empresa SaaS B2B?"
    )
    assert payload["handled"] is True
    assert payload["route_family"] == "executive_strategy_answer"
