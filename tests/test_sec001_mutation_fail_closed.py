from __future__ import annotations

from app.evolution_os.governance.mutation_authority import mutation_authority_required


def test_mutation_authority_defaults_to_required(monkeypatch):
    monkeypatch.delenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", raising=False)
    assert mutation_authority_required() is True


def test_mutation_authority_can_only_be_disabled_explicitly(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", "false")
    assert mutation_authority_required() is False
