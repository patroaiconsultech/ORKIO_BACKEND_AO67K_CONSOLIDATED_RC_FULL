from __future__ import annotations

import os

from evolution_os.governance.mutation_authority import authorize_proposal_snapshot


def _proposal(**overrides):
    base = {
        "id": "proposal_123",
        "status": "approved",
        "approved_by": "admin@example.com",
        "approved_at": 1_700_000_000,
        "execution_status": "dry_run_completed",
    }
    base.update(overrides)
    return base


def test_observe_only_mode_preserves_legacy_flow(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", "false")
    decision = authorize_proposal_snapshot(
        {},
        action="create_branch",
        actor="admin@example.com",
        target="evolution/test",
    )
    assert decision.allowed is True
    assert decision.legacy_mode is True


def test_strict_mode_requires_action_flag(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", "true")
    monkeypatch.setenv("EVOLUTION_ALLOW_CREATE_BRANCH", "false")
    decision = authorize_proposal_snapshot(
        _proposal(),
        action="create_branch",
        actor="admin@example.com",
        target="evolution/test",
        approval_id="proposal_123",
        require_dry_run=True,
        now=1_700_000_100,
    )
    assert decision.allowed is False
    assert decision.reason.startswith("action_disabled:")


def test_strict_mode_authorizes_fresh_scoped_approval(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", "true")
    monkeypatch.setenv("EVOLUTION_ALLOW_CREATE_BRANCH", "true")
    monkeypatch.setenv("EVOLUTION_APPROVAL_TTL_SECONDS", "3600")
    decision = authorize_proposal_snapshot(
        _proposal(),
        action="create_branch",
        actor="executor@example.com",
        target="evolution/test",
        approval_id="proposal_123",
        require_dry_run=True,
        now=1_700_000_100,
    )
    assert decision.allowed is True
    assert decision.reason == "governed_mutation_authorized"


def test_expired_approval_is_denied(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", "true")
    monkeypatch.setenv("EVOLUTION_ALLOW_OPEN_PR", "true")
    monkeypatch.setenv("EVOLUTION_APPROVAL_TTL_SECONDS", "300")
    decision = authorize_proposal_snapshot(
        _proposal(),
        action="open_pr",
        actor="executor@example.com",
        target="evolution/test",
        approval_id="proposal_123",
        require_dry_run=True,
        now=1_700_001_000,
    )
    assert decision.allowed is False
    assert decision.reason == "approval_expired"


def test_rollback_remains_available_after_approval_ttl(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", "true")
    monkeypatch.setenv("EVOLUTION_ALLOW_ROLLBACK", "true")
    decision = authorize_proposal_snapshot(
        _proposal(status="executed"),
        action="rollback",
        actor="executor@example.com",
        target="restore_point_1",
        approval_id="proposal_123",
        now=1_800_000_000,
    )
    assert decision.allowed is True
