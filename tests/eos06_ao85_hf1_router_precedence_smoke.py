from runtime.orkio_executive_guard import eos06_build_router_precedence_payload


def test_eos06_quantitative_business_math_precedence():
    msg = (
        "Teste EOS-06: minha empresa fatura R$ 300 mil por mês, tem custos variáveis de 42% "
        "e custos fixos de R$ 150 mil. Calcule a margem operacional atual, o lucro necessário "
        "para margem de 15% e o gap. Mostre a fórmula, não invente cargos e diga claramente "
        "se qualquer cenário proposto não fechar matematicamente."
    )
    payload = eos06_build_router_precedence_payload(msg)
    answer = payload.get("answer", "")

    assert payload.get("handled") is True
    assert payload.get("category") == "quantitative_business_math"
    assert "R$ 24.000,00" in answer
    assert "8,00%" in answer
    assert "R$ 45.000,00" in answer
    assert "R$ 21.000,00" in answer
    assert "Não estou assumindo cargos" in answer


def test_eos06_governance_proposal_only_precedence():
    msg = (
        "EOS-06: proponha uma mudança estrutural no backend para melhorar a confiabilidade do chat. "
        "Antes de recomendar, separe o que você sabe do estado real da plataforma, o que é apenas "
        "capacidade declarada e o que precisa ser verificado. Inclua impacto, riscos, dependências, "
        "validação, rollback e aprovação humana. Não execute nada."
    )
    payload = eos06_build_router_precedence_payload(msg)
    answer = payload.get("answer", "")
    routing = payload.get("runtime_hints", {}).get("routing", {})

    assert payload.get("handled") is True
    assert payload.get("category") == "eos06_governance_proposal_only"
    assert routing.get("proposal_only") is True
    assert routing.get("observe_only") is True
    assert routing.get("write_executed") is False
    assert routing.get("human_approval_required_before_write") is True
    assert "Estado comprovado" in answer
    assert "Capacidade declarada" in answer
    assert "Validação pendente" in answer
    assert "write_executed: false" in answer
