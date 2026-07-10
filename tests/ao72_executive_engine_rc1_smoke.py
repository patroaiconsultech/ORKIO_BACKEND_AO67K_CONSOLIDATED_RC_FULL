from runtime.executive import build_executive_preflight, build_execution_plan
from runtime.quality import ao70_validate_response


def test_operational_status_blocks_public_journey_without_executive_quality():
    result = build_executive_preflight(
        "Olá, Orkio. Confirme que está operacional e responda em uma frase."
    )
    assert result["block_public_journey_fastpath"] is True
    assert result["intent"] == "operational_direct_answer"
    assert result["applies"] is False


def test_board_decision_requires_full_structure():
    prompt = (
        "Sou CEO e preciso decidir se contrato mais 6 vendedores agora. "
        "Temos MRR de R$ 1,2 milhão, crescimento mensal de 4%, churn de 2,8%, "
        "CAC payback de 11 meses, caixa para 10 meses e NRR de 108%. "
        "Estruture uma recomendação para board com tese, riscos, métricas de decisão "
        "e gatilhos de parada."
    )
    result = build_executive_preflight(prompt)
    assert result["applies"] is True
    assert result["block_public_journey_fastpath"] is True
    assert result["intent"] == "executive_board_decision"
    for required in ("thesis", "risks", "decision_metrics", "stop_triggers", "recommendation"):
        assert required in result["required_outputs"]

    incomplete = (
        "Há riscos de crescimento e execução. Revise ICP e eficiência comercial."
    )
    validation = ao70_validate_response(prompt, incomplete)
    assert validation["passed"] is False
    assert "thesis" in validation["missing_items"]
    assert "decision_metrics" in validation["missing_items"]
    assert "stop_triggers" in validation["missing_items"]

    complete = (
        "Tese executiva: contratação em duas ondas, condicionada à eficiência. "
        "Recomendação: contratar 3 agora e 3 após validação. "
        "Riscos: payback de 11 meses, runway de 10 meses e possível queda de produtividade. "
        "Métricas de decisão: CAC payback <= 12 meses, NRR >= 108%, churn <= 2,8% "
        "e pipeline coverage >= 3x. "
        "Gatilhos de parada: pausar se payback superar 14 meses, NRR cair abaixo de 105% "
        "ou runway projetado ficar abaixo de 8 meses."
    )
    validation = ao70_validate_response(prompt, complete)
    assert validation["passed"] is True


def test_marketplace_prompt_extracts_requested_sections():
    prompt = (
        "Analise esta empresa sem inventar dados: marketplace B2B com GMV mensal de "
        "R$ 5 milhões, take rate de 9%, margem operacional negativa de R$ 120 mil/mês, "
        "caixa de R$ 900 mil e crescimento de GMV de 6% ao mês. "
        "Separe fatos, inferências, dados faltantes, riscos e próximos passos de gestão."
    )
    result = build_executive_preflight(prompt)
    assert result["applies"] is True
    for required in ("facts", "inferences", "missing_data", "risks", "next_steps"):
        assert required in result["required_outputs"]


if __name__ == "__main__":
    test_operational_status_blocks_public_journey_without_executive_quality()
    test_board_decision_requires_full_structure()
    test_marketplace_prompt_extracts_requested_sections()
    print("AO72_EXECUTIVE_ENGINE_RC1_SMOKE_PASS")
