from __future__ import annotations

from runtime.orkio_executive_guard import eos06_build_router_precedence_payload


def test_eos06_hf2_quantitative_business_math_owns_turn():
    msg = (
        "Teste EOS-06: minha empresa fatura R$ 300 mil por mês, tem custos variáveis "
        "de 42% e custos fixos de R$ 150 mil. Calcule a margem operacional atual, "
        "o lucro necessário para margem de 15% e o gap. Mostre a fórmula, não invente cargos "
        "e diga claramente se qualquer cenário proposto não fechar matematicamente."
    )
    payload = eos06_build_router_precedence_payload(msg)
    assert payload["handled"] is True
    assert payload["category"] == "quantitative_business_math"
    answer = payload["answer"]
    assert "R$ 24.000,00" in answer
    assert "8,00%" in answer
    assert "R$ 45.000,00" in answer
    assert "R$ 21.000,00" in answer
    routing = payload["runtime_hints"]["routing"]
    assert routing["turn_owner"] == "EOS06_AO85"
    assert routing["block_public_deterministic_fastpaths"] is True


def test_eos06_hf2_governance_proposal_only_owns_turn():
    msg = (
        "EOS-06: proponha uma mudança estrutural no backend para melhorar a confiabilidade "
        "do chat. Antes de recomendar, separe o que você sabe do estado real da plataforma, "
        "o que é apenas capacidade declarada e o que precisa ser verificado. Inclua impacto, "
        "riscos, dependências, validação, rollback e aprovação humana. Não execute nada."
    )
    payload = eos06_build_router_precedence_payload(msg)
    assert payload["handled"] is True
    assert payload["category"] == "eos06_governance_proposal_only"
    answer = payload["answer"]
    assert "Estado comprovado" in answer
    assert "Capacidade declarada" in answer
    assert "Validação pendente" in answer
    assert "Rollback" in answer
    routing = payload["runtime_hints"]["routing"]
    assert routing["proposal_only"] is True
    assert routing["observe_only"] is True
    assert routing["write_executed"] is False
    assert routing["turn_owner"] == "EOS06_AO85"
    assert routing["block_public_deterministic_fastpaths"] is True
