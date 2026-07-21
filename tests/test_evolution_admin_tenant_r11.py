from __future__ import annotations

import importlib
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
def tenant_db(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE admin_evolution_proposals (
                proposal_id TEXT PRIMARY KEY,
                org_slug TEXT NOT NULL,
                status TEXT NOT NULL,
                title TEXT,
                summary TEXT,
                risk TEXT,
                target_files_json TEXT,
                rollback_plan TEXT,
                checklist_json TEXT,
                source TEXT,
                source_thread_id TEXT,
                created_by TEXT,
                approved_by TEXT,
                rejected_by TEXT,
                created_at BIGINT,
                updated_at BIGINT,
                approved_at BIGINT,
                rejected_at BIGINT,
                execution_id TEXT,
                execution_status TEXT,
                write_allowed BOOLEAN,
                execution_allowed BOOLEAN,
                human_approval_required BOOLEAN
            )
        """))
        conn.execute(text("""
            CREATE TABLE admin_evolution_executions (
                execution_id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL,
                org_slug TEXT NOT NULL,
                status TEXT NOT NULL,
                mode TEXT,
                created_by TEXT,
                approved_by TEXT,
                risk TEXT,
                rollback_plan TEXT,
                smoke_checklist_json TEXT,
                result_json TEXT,
                created_at BIGINT,
                updated_at BIGINT,
                started_at BIGINT,
                finished_at BIGINT
            )
        """))

        rows = [
            {
                "proposal_id": "prop-a-pending",
                "org_slug": "tenant-a",
                "status": "pending_approval",
                "updated_at": 100,
            },
            {
                "proposal_id": "prop-a-approved",
                "org_slug": "tenant-a",
                "status": "approved",
                "updated_at": 101,
            },
            {
                "proposal_id": "prop-b-pending",
                "org_slug": "tenant-b",
                "status": "pending_approval",
                "updated_at": 102,
            },
            {
                "proposal_id": "prop-b-approved",
                "org_slug": "tenant-b",
                "status": "approved",
                "updated_at": 103,
            },
        ]
        for row in rows:
            conn.execute(text("""
                INSERT INTO admin_evolution_proposals (
                    proposal_id, org_slug, status, title, summary, risk,
                    target_files_json, rollback_plan, checklist_json,
                    source, source_thread_id, created_by, created_at, updated_at,
                    execution_status, write_allowed, execution_allowed,
                    human_approval_required
                ) VALUES (
                    :proposal_id, :org_slug, :status, :proposal_id, '', 'low',
                    '[]', 'rollback', '[]',
                    'test', 'thread-test', 'tester', 1, :updated_at,
                    'not_started', FALSE, FALSE, TRUE
                )
            """), row)

        conn.execute(text("""
            INSERT INTO admin_evolution_executions (
                execution_id, proposal_id, org_slug, status, mode,
                smoke_checklist_json, result_json, created_at, updated_at
            ) VALUES (
                'exec-a', 'prop-a-approved', 'tenant-a', 'dry_run_completed',
                'controlled_dry_run_no_write', '[]', '{}', 1, 1
            )
        """))
        conn.execute(text("""
            INSERT INTO admin_evolution_executions (
                execution_id, proposal_id, org_slug, status, mode,
                smoke_checklist_json, result_json, created_at, updated_at
            ) VALUES (
                'exec-b', 'prop-b-approved', 'tenant-b', 'dry_run_completed',
                'controlled_dry_run_no_write', '[]', '{}', 1, 1
            )
        """))

    monkeypatch.setattr(main, "SessionLocal", SessionLocal)
    monkeypatch.setattr(main, "_admin_evolution_bootstrap_db_schema", lambda: True)
    return SessionLocal


def _status(SessionLocal, proposal_id: str) -> str:
    with SessionLocal() as db:
        return str(db.execute(
            text(
                "SELECT status FROM admin_evolution_proposals "
                "WHERE proposal_id = :proposal_id"
            ),
            {"proposal_id": proposal_id},
        ).scalar_one())


def test_proposal_lookup_is_tenant_bound(tenant_db):
    assert main._admin_evolution_get_proposal(
        "prop-a-pending",
        org_slug="tenant-a",
    )["org_slug"] == "tenant-a"

    assert main._admin_evolution_get_proposal(
        "prop-a-pending",
        org_slug="tenant-b",
    ) is None


def test_proposal_list_is_tenant_bound(tenant_db):
    rows = main._admin_evolution_list_proposals(org_slug="tenant-a")
    assert {row["proposal_id"] for row in rows} == {
        "prop-a-pending",
        "prop-a-approved",
    }
    assert all(row["org_slug"] == "tenant-a" for row in rows)


def test_execution_list_is_tenant_bound(tenant_db):
    rows = main._admin_evolution_list_executions(org_slug="tenant-a")
    assert [row["execution_id"] for row in rows] == ["exec-a"]
    assert rows[0]["org_slug"] == "tenant-a"


def test_detail_route_rejects_header_tenant_mismatch(tenant_db):
    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposal_detail(
            "prop-a-pending",
            x_org_slug="tenant-b",
            _admin={"org": "tenant-a", "role": "admin"},
        )
    assert exc.value.status_code == 403
    assert exc.value.detail == "Tenant mismatch"


def test_detail_route_hides_other_tenant_identifier(tenant_db):
    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposal_detail(
            "prop-b-pending",
            x_org_slug="tenant-a",
            _admin={"org": "tenant-a", "role": "admin"},
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == "proposal_not_found"


def test_approve_updates_only_canonical_tenant(tenant_db):
    result = main.admin_evolution_proposal_approve(
        "prop-a-pending",
        x_org_slug="tenant-a",
        _admin={
            "org": "tenant-a",
            "role": "admin",
            "email": "admin-a@example.test",
        },
    )

    assert result["proposal"]["status"] == "approved"
    assert result["proposal"]["org_slug"] == "tenant-a"
    assert result["tenant_guard"] == "canonical"
    assert _status(tenant_db, "prop-a-pending") == "approved"
    assert _status(tenant_db, "prop-b-pending") == "pending_approval"


def test_approve_cannot_target_other_tenant(tenant_db):
    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposal_approve(
            "prop-b-pending",
            x_org_slug="tenant-a",
            _admin={"org": "tenant-a", "role": "admin"},
        )
    assert exc.value.status_code == 404
    assert _status(tenant_db, "prop-b-pending") == "pending_approval"


def test_dry_run_cannot_target_other_tenant(tenant_db):
    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposal_dry_run(
            "prop-b-approved",
            x_org_slug="tenant-a",
            _admin={"org": "tenant-a", "role": "admin"},
        )
    assert exc.value.status_code == 404

    with tenant_db() as db:
        count = db.execute(text(
            "SELECT COUNT(*) FROM admin_evolution_executions "
            "WHERE org_slug = 'tenant-a' AND proposal_id = 'prop-b-approved'"
        )).scalar_one()
    assert count == 0


def test_dry_run_updates_proposal_inside_same_tenant(tenant_db):
    result = main.admin_evolution_proposal_dry_run(
        "prop-a-approved",
        x_org_slug="tenant-a",
        _admin={
            "org": "tenant-a",
            "role": "admin",
            "email": "admin-a@example.test",
        },
    )

    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["write_allowed"] is False
    assert result["proposal"]["org_slug"] == "tenant-a"

    with tenant_db() as db:
        proposal = db.execute(text("""
            SELECT org_slug, execution_status
            FROM admin_evolution_proposals
            WHERE proposal_id = 'prop-a-approved'
        """)).mappings().one()
        execution = db.execute(text("""
            SELECT org_slug, proposal_id
            FROM admin_evolution_executions
            WHERE execution_id = :execution_id
        """), {"execution_id": result["execution_id"]}).mappings().one()

    assert proposal["org_slug"] == "tenant-a"
    assert proposal["execution_status"] == "dry_run_completed"
    assert execution["org_slug"] == "tenant-a"
    assert execution["proposal_id"] == "prop-a-approved"


def test_admin_evolution_database_failure_is_fail_closed(monkeypatch):
    monkeypatch.setattr(main, "_admin_evolution_bootstrap_db_schema", lambda: False)

    with pytest.raises(HTTPException) as exc:
        main._admin_evolution_get_proposal(
            "prop-a-pending",
            org_slug="tenant-a",
        )
    assert exc.value.status_code == 503
    assert exc.value.detail == "evolution_schema_unavailable"

    with pytest.raises(HTTPException) as exc:
        main._admin_evolution_list_proposals(org_slug="tenant-a")
    assert exc.value.status_code == 503
    assert exc.value.detail == "evolution_schema_unavailable"
