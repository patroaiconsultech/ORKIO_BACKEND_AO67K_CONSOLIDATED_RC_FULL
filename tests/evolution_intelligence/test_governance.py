import pytest

from app.evolution.intelligence.governance import (
    EvolutionGovernanceError,
    load_evolution_governance_config,
    validate_evolution_governance_config,
)


def test_safe_defaults_are_proposal_only(monkeypatch):
    names = [
        "APP_ENV",
        "EVOLUTION_WRITE_ENABLED",
        "EVOLUTION_AUTO_APPLY_ENABLED",
        "EVOLUTION_HUMAN_APPROVAL_REQUIRED",
        "EVOLUTION_PROPOSAL_ONLY",
    ]
    for name in names:
        monkeypatch.delenv(name, raising=False)
    config = validate_evolution_governance_config(
        load_evolution_governance_config()
    )
    assert config["proposal_only"] is True
    assert config["write_enabled"] is False
    assert config["auto_apply_enabled"] is False
    assert config["human_approval_required"] is True


def test_code_write_is_blocked_in_foundation(monkeypatch):
    monkeypatch.setenv("EVOLUTION_WRITE_ENABLED", "true")
    with pytest.raises(EvolutionGovernanceError, match="code_write_not_allowed"):
        validate_evolution_governance_config(
            load_evolution_governance_config()
        )


def test_production_requires_human_approval(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("EVOLUTION_HUMAN_APPROVAL_REQUIRED", "false")
    with pytest.raises(EvolutionGovernanceError, match="production_requires_human"):
        validate_evolution_governance_config(
            load_evolution_governance_config()
        )
