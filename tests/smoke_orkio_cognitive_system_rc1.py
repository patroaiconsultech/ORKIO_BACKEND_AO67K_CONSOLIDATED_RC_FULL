from runtime.orkio_cognitive_system import build_orkio_executive_answer, executive_system_smoke


def test_smoke_rc1():
    assert executive_system_smoke() == "ORKIO_EXECUTIVE_COGNITIVE_SYSTEM_RC1_OK"


def test_platform_capability_answer():
    result = build_orkio_executive_answer(
        "O que a plataforma Orkio faz hoje? Separe produção, beta e roadmap."
    )
    assert result["handled"] is True
    assert "Disponível agora" in result["answer"]
    assert "Beta" in result["answer"]
    assert "Roadmap" in result["answer"]
