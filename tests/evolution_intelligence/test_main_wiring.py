from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "main.py").read_text(encoding="utf-8")


def test_router_and_startup_governance_are_wired():
    assert "build_evolution_intelligence_router" in SOURCE
    assert "EvolutionIntelligenceRouterDeps" in SOURCE
    assert "_startup_evolution_intelligence_governance_r1" in SOURCE
    assert "EVOLUTION_INTELLIGENCE_GOVERNANCE_FAILED" in SOURCE
    assert "EVOLUTION_INTELLIGENCE_GOVERNANCE_OK" in SOURCE
    assert "actor_reference=actor_reference" in SOURCE
    assert "/api/admin/evolution/intelligence" not in SOURCE  # route path stays modular
