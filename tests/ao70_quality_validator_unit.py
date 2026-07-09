\
from runtime.quality import ao70_should_apply_quality_engine, ao70_validate_response

PROMPT = """
Sou CEO de um SaaS B2B. Tenho MRR de R$ 100 mil, custos de R$ 70 mil, caixa de R$ 300 mil,
CAC de R$ 2 mil, ticket médio de R$ 1 mil/mês, churn de 3% e preciso crescer 35% sem captação.
Calcule lucro operacional, margem, runway, LTV, LTV/CAC e entregue plano 30-60-90 com riscos.
"""

BAD = "Para começar, me diga qual é o seu principal objetivo e quais métricas você acompanha hoje."

GOOD = """
Diagnóstico executivo: receita mensal R$ 100 mil e custo mensal R$ 70 mil geram lucro operacional
de R$ 30 mil e margem de 30%. Com caixa de R$ 300 mil e operação positiva, o runway é superior
a 10 meses mesmo em cenário de reinvestimento. LTV estimado: R$ 1.000 / 3% = R$ 33.333.
LTV/CAC: 33.333 / 2.000 = 16,7x. Plano 30-60-90: nos primeiros 30 dias corrigir pricing e funil;
em 60 dias escalar canais com payback curto; em 90 dias consolidar expansão sem captação.
Riscos: churn, pressão de suporte, CAC marginal e perda de qualidade na expansão.
"""

def test_ao70_detects_executive_prompt():
    assert ao70_should_apply_quality_engine(PROMPT, response_control=None) is True

def test_ao70_rejects_generic_answer():
    result = ao70_validate_response(PROMPT, BAD)
    assert result["passed"] is False
    assert result["score"] < 85
    assert "operating_profit" in result["missing_items"]

def test_ao70_accepts_complete_answer():
    result = ao70_validate_response(PROMPT, GOOD)
    assert result["passed"] is True
    assert result["score"] >= 85
