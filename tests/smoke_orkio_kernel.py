from runtime.orkio_kernel import build_orkio_kernel_response

def assert_contains(text: str, expected: str) -> None:
    if expected not in text:
        raise AssertionError(f"Expected {expected!r} in response. Got: {text[:300]!r}")

def main() -> None:
    r1 = build_orkio_kernel_response(
        "Minha empresa fatura R$ 300 mil por mês, tem custos variáveis de 42% e custos fixos de R$ 150 mil. Calcule margem atual, lucro-alvo para 15% e gap."
    )
    assert r1.handled
    assert r1.classification.category == "quantitative_business_math"
    assert_contains(r1.response_text, "8,00%")
    assert_contains(r1.response_text, "R$ 21.000,00")

    r2 = build_orkio_kernel_response(
        "Proponha uma evolução estrutural para o Orkio. Permaneça em observe_only e proposal_only=true. Inclua impacto, riscos, validação, rollback e aprovação humana. Não execute nada."
    )
    assert r2.handled
    assert r2.governance_flags["proposal_only"] is True
    assert r2.governance_flags["write_executed"] is False
    assert_contains(r2.response_text, "proposal_only=true")

    r3 = build_orkio_kernel_response("O que é o Orkio hoje? Separe produção, beta, roadmap e proposta.")
    assert r3.handled
    assert r3.classification.category == "platform_capability_question"
    assert_contains(r3.response_text, "PRODUCTION")
    assert_contains(r3.response_text, "ROADMAP")

    print("SMOKE_ORKIO_KERNEL_OK")

if __name__ == "__main__":
    main()
