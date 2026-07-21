from __future__ import annotations

import importlib
import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

main = importlib.import_module("app.main")

POSTGRES_URL = os.getenv("ORKIO_TEST_POSTGRES_URL", "").strip()
pytestmark = pytest.mark.skipif(
    not POSTGRES_URL,
    reason="ORKIO_TEST_POSTGRES_URL is required for PostgreSQL tenant integration",
)


@pytest.fixture()
def postgres_tenant_db(monkeypatch):
    schema = "phase_a_r11_" + uuid.uuid4().hex[:16]
    engine = create_engine(POSTGRES_URL, pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def _set_search_path(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(f'SET search_path TO "{schema}", public')
        finally:
            cursor.close()

    # Create schema before the listener's search_path can reference it.
    bootstrap = create_engine(POSTGRES_URL, pool_pre_ping=True)
    with bootstrap.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    bootstrap.dispose()

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE admin_evolution_proposals (
                proposal_id VARCHAR PRIMARY KEY,
                org_slug VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                title TEXT,
                summary TEXT,
                risk VARCHAR,
                target_files_json TEXT,
                rollback_plan TEXT,
                checklist_json TEXT,
                source VARCHAR,
                source_thread_id VARCHAR,
                created_by VARCHAR,
                approved_by VARCHAR,
                rejected_by VARCHAR,
                created_at BIGINT,
                updated_at BIGINT,
                approved_at BIGINT,
                rejected_at BIGINT,
                execution_id VARCHAR,
                execution_status VARCHAR,
                write_allowed BOOLEAN,
                execution_allowed BOOLEAN,
                human_approval_required BOOLEAN
            )
        """))
        conn.execute(text("""
            CREATE TABLE admin_evolution_executions (
                execution_id VARCHAR PRIMARY KEY,
                proposal_id VARCHAR NOT NULL,
                org_slug VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                mode VARCHAR,
                created_by VARCHAR,
                approved_by VARCHAR,
                risk VARCHAR,
                rollback_plan TEXT,
                smoke_checklist_json TEXT,
                result_json TEXT,
                created_at BIGINT,
                updated_at BIGINT,
                started_at BIGINT,
                finished_at BIGINT
            )
        """))
        for proposal_id, org_slug, status, updated_at in (
            ("proposal-a", "tenant-a", "pending_approval", 100),
            ("proposal-b", "tenant-b", "pending_approval", 101),
            ("proposal-race", "tenant-a", "pending_approval", 102),
        ):
            conn.execute(text("""
                INSERT INTO admin_evolution_proposals (
                    proposal_id, org_slug, status, title, summary, risk,
                    target_files_json, rollback_plan, checklist_json,
                    source, source_thread_id, created_by, created_at, updated_at,
                    execution_status, write_allowed, execution_allowed,
                    human_approval_required
                ) VALUES (
                    :proposal_id, :org_slug, :status, :proposal_id, '', 'low',
                    '[]', 'rollback', '[]', 'test', 'thread-test', 'tester',
                    1, :updated_at, 'not_started', FALSE, FALSE, TRUE
                )
            """), {
                "proposal_id": proposal_id,
                "org_slug": org_slug,
                "status": status,
                "updated_at": updated_at,
            })

    monkeypatch.setattr(main, "SessionLocal", SessionLocal)
    monkeypatch.setattr(main, "_admin_evolution_bootstrap_db_schema", lambda: True)
    monkeypatch.setattr(main, "tenant_mode", lambda: "multi")

    try:
        yield SessionLocal
    finally:
        engine.dispose()
        cleanup = create_engine(POSTGRES_URL, pool_pre_ping=True)
        with cleanup.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        cleanup.dispose()


def _status(SessionLocal, proposal_id: str) -> str:
    with SessionLocal() as db:
        return str(db.execute(
            text(
                "SELECT status FROM admin_evolution_proposals "
                "WHERE proposal_id = :proposal_id"
            ),
            {"proposal_id": proposal_id},
        ).scalar_one())


def _counts(SessionLocal, org_slug: str):
    with SessionLocal() as db:
        proposals = int(db.execute(
            text("SELECT COUNT(*) FROM admin_evolution_proposals WHERE org_slug=:org"),
            {"org": org_slug},
        ).scalar_one())
        executions = int(db.execute(
            text("SELECT COUNT(*) FROM admin_evolution_executions WHERE org_slug=:org"),
            {"org": org_slug},
        ).scalar_one())
    return proposals, executions


def test_postgres_cross_tenant_reads_and_mutations_fail_closed(postgres_tenant_db):
    before = _counts(postgres_tenant_db, "tenant-b")

    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposal_detail(
            "proposal-b",
            x_org_slug="tenant-a",
            _admin={"org": "tenant-a", "role": "admin"},
        )
    assert exc.value.status_code in {403, 404}

    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposal_approve(
            "proposal-b",
            x_org_slug="tenant-a",
            _admin={"org": "tenant-a", "role": "admin"},
        )
    assert exc.value.status_code in {403, 404}

    with pytest.raises(HTTPException) as exc:
        main.admin_evolution_proposals(
            x_org_slug="tenant-b",
            _admin={"org": "tenant-a", "role": "admin"},
        )
    assert exc.value.status_code == 403
    assert exc.value.detail == "Tenant mismatch"

    assert _status(postgres_tenant_db, "proposal-b") == "pending_approval"
    assert _counts(postgres_tenant_db, "tenant-b") == before


def test_postgres_concurrent_approval_has_single_winner(postgres_tenant_db):
    def approve(actor: str):
        try:
            result = main._admin_evolution_update_status(
                "proposal-race",
                status="approved",
                actor=actor,
                org_slug="tenant-a",
            )
            return ("ok", result["status"])
        except HTTPException as exc:
            return ("error", exc.status_code)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(approve, ("admin-a", "admin-b")))

    assert sorted(results) == [("error", 409), ("ok", "approved")]
    assert _status(postgres_tenant_db, "proposal-race") == "approved"
