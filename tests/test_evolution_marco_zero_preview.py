from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

main = importlib.import_module("app.main")


@pytest.fixture()
def preview_db(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE admin_evolution_proposals (
                    proposal_id TEXT PRIMARY KEY,
                    org_slug TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at BIGINT NOT NULL
                )
                """
            )
        )
        for idx in range(75):
            conn.execute(
                text(
                    """
                    INSERT INTO admin_evolution_proposals
                        (proposal_id, org_slug, status, updated_at)
                    VALUES (:proposal_id, 'tenant-a', 'pending_approval', :updated_at)
                    """
                ),
                {"proposal_id": f"a-{idx:03d}", "updated_at": 1000 + idx},
            )
        for idx in range(3):
            conn.execute(
                text(
                    """
                    INSERT INTO admin_evolution_proposals
                        (proposal_id, org_slug, status, updated_at)
                    VALUES (:proposal_id, 'tenant-a', 'archived', :updated_at)
                    """
                ),
                {"proposal_id": f"archived-{idx}", "updated_at": 900 + idx},
            )
        for idx in range(4):
            conn.execute(
                text(
                    """
                    INSERT INTO admin_evolution_proposals
                        (proposal_id, org_slug, status, updated_at)
                    VALUES (:proposal_id, 'tenant-b', 'pending_approval', :updated_at)
                    """
                ),
                {"proposal_id": f"b-{idx}", "updated_at": 1000 + idx},
            )
        conn.execute(
            text(
                """
                INSERT INTO admin_evolution_proposals
                    (proposal_id, org_slug, status, updated_at)
                VALUES ('future-a', 'tenant-a', 'pending_approval', 5000)
                """
            )
        )

    monkeypatch.setattr(main, "SessionLocal", SessionLocal)
    return SessionLocal


def _counts(SessionLocal):
    with SessionLocal() as db:
        return {
            "tenant_a_total": db.execute(
                text(
                    "SELECT COUNT(*) FROM admin_evolution_proposals "
                    "WHERE org_slug = 'tenant-a'"
                )
            ).scalar_one(),
            "tenant_a_archived": db.execute(
                text(
                    "SELECT COUNT(*) FROM admin_evolution_proposals "
                    "WHERE org_slug = 'tenant-a' AND LOWER(status) = 'archived'"
                )
            ).scalar_one(),
            "tenant_b_total": db.execute(
                text(
                    "SELECT COUNT(*) FROM admin_evolution_proposals "
                    "WHERE org_slug = 'tenant-b'"
                )
            ).scalar_one(),
        }


def test_preview_is_exact_bounded_and_write_free(preview_db):
    before = _counts(preview_db)

    result = main._admin_evolution_archive_baseline(
        org_slug="tenant-a",
        actor="admin@example.test",
        dry_run=True,
        cutoff_at=2000,
    )

    after = _counts(preview_db)
    assert after == before
    assert result["candidate_count"] == 75
    assert result["already_archived_count"] == 3
    assert len(result["proposal_ids_preview"]) == 50
    assert result["preview_truncated"] is True
    assert result["cutoff_at"] == 2000
    assert result["write_enabled"] is False
    assert result["write_executed"] is False
    assert result["database_write_executed"] is False
    assert result["memory_fallback_used"] is False
    assert result["schema_bootstrap_executed"] is False
    assert "future-a" not in result["proposal_ids_preview"]
    assert not any(value.startswith("b-") for value in result["proposal_ids_preview"])


def test_real_apply_is_fail_closed_before_database_access(monkeypatch):
    def forbidden_session():
        raise AssertionError("database must not be touched for blocked write")

    monkeypatch.setattr(main, "SessionLocal", forbidden_session)

    with pytest.raises(HTTPException) as exc:
        main._admin_evolution_archive_baseline(
            org_slug="tenant-a",
            actor="admin@example.test",
            dry_run=False,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "EVOLUTION_MARCO_ZERO_WRITE_DISABLED"


def test_route_rejects_tenant_mismatch(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED", "true")

    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposals_archive_baseline(
            confirm="legacy-value-is-not-authority",
            dry_run=True,
            cutoff_at=2000,
            x_org_slug="tenant-b",
            _admin={
                "org": "tenant-a",
                "email": "admin@example.test",
                "role": "admin",
            },
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Tenant mismatch"


def test_route_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED", raising=False)

    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposals_archive_baseline(
            dry_run=True,
            x_org_slug="tenant-a",
            _admin={"org": "tenant-a", "role": "admin"},
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "EVOLUTION_MARCO_ZERO_PREVIEW_DISABLED"


def test_route_never_accepts_dry_run_false(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED", "true")

    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposals_archive_baseline(
            dry_run=False,
            x_org_slug="tenant-a",
            _admin={"org": "tenant-a", "role": "admin"},
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "EVOLUTION_MARCO_ZERO_WRITE_DISABLED"


def test_database_unavailable_is_503_without_memory_fallback(monkeypatch):
    def unavailable():
        raise RuntimeError("db unavailable")

    monkeypatch.setattr(main, "SessionLocal", unavailable)

    with pytest.raises(HTTPException) as exc:
        main._admin_evolution_archive_baseline(
            org_slug="tenant-a",
            actor="admin@example.test",
            dry_run=True,
            cutoff_at=2000,
        )

    assert exc.value.status_code == 503
    assert exc.value.detail == "EVOLUTION_MARCO_ZERO_DB_UNAVAILABLE"
