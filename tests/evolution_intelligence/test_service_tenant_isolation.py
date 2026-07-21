from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.evolution_intelligence_service import (
    create_objective,
    get_objective,
    list_objectives,
    list_target_history,
    upsert_target,
)


def _db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE evolution_objectives (
                id TEXT PRIMARY KEY,
                org_slug TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                starts_at INTEGER,
                ends_at INTEGER,
                owner_ref TEXT NOT NULL,
                success_definition TEXT NOT NULL,
                proposal_policy TEXT NOT NULL,
                human_approval_required BOOLEAN NOT NULL,
                version INTEGER NOT NULL,
                created_by TEXT NOT NULL,
                updated_by TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE evolution_kpi_targets (
                id TEXT PRIMARY KEY,
                org_slug TEXT NOT NULL,
                objective_id TEXT,
                scope_key TEXT NOT NULL,
                kpi_code TEXT NOT NULL,
                target_value REAL NOT NULL,
                warning_threshold REAL NOT NULL,
                critical_threshold REAL NOT NULL,
                weight REAL NOT NULL,
                minimum_sample_size INTEGER NOT NULL,
                enabled BOOLEAN NOT NULL,
                proposal_enabled BOOLEAN NOT NULL,
                auto_apply_enabled BOOLEAN NOT NULL,
                version INTEGER NOT NULL,
                starts_at INTEGER,
                ends_at INTEGER,
                created_by TEXT NOT NULL,
                updated_by TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE evolution_kpi_target_versions (
                id TEXT PRIMARY KEY,
                org_slug TEXT NOT NULL,
                target_id TEXT NOT NULL,
                objective_id TEXT,
                scope_key TEXT NOT NULL,
                kpi_code TEXT NOT NULL,
                version INTEGER NOT NULL,
                target_value REAL NOT NULL,
                warning_threshold REAL NOT NULL,
                critical_threshold REAL NOT NULL,
                weight REAL NOT NULL,
                minimum_sample_size INTEGER NOT NULL,
                enabled BOOLEAN NOT NULL,
                proposal_enabled BOOLEAN NOT NULL,
                auto_apply_enabled BOOLEAN NOT NULL,
                effective_from INTEGER NOT NULL,
                effective_to INTEGER,
                changed_by TEXT NOT NULL,
                change_reason TEXT NOT NULL,
                approval_id TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE evolution_health_snapshots (
                id TEXT PRIMARY KEY,
                org_slug TEXT NOT NULL
            )
        """))
    return Session(engine)


def _payload(name):
    return {
        "name": name,
        "description": "Descrição suficientemente detalhada.",
        "category": "technical_reliability",
        "priority": 90,
        "status": "active",
        "starts_at": None,
        "ends_at": None,
        "owner_ref": "CTO",
        "success_definition": "Saúde técnica acima de 90.",
    }


def test_objectives_are_tenant_isolated():
    db = _db()
    create_objective(
        db,
        org_slug="tenant-a",
        objective_id="obj-a",
        payload=_payload("Objetivo A"),
        actor_ref="actor:a",
        now_ts=1,
    )
    create_objective(
        db,
        org_slug="tenant-b",
        objective_id="obj-b",
        payload=_payload("Objetivo B"),
        actor_ref="actor:b",
        now_ts=1,
    )
    db.commit()
    assert [row["id"] for row in list_objectives(db, org_slug="tenant-a")] == ["obj-a"]
    assert get_objective(db, org_slug="tenant-b", objective_id="obj-a") is None


def test_target_cannot_bind_cross_tenant_objective():
    db = _db()
    create_objective(
        db,
        org_slug="tenant-a",
        objective_id="obj-a",
        payload=_payload("Objetivo A"),
        actor_ref="actor:a",
        now_ts=1,
    )
    db.commit()
    payload = {
        "objective_id": "obj-a",
        "kpi_code": "operational_reliability",
        "target_value": 99,
        "warning_threshold": 95,
        "critical_threshold": 90,
        "weight": 0.5,
        "minimum_sample_size": 20,
        "enabled": True,
        "proposal_enabled": True,
        "change_reason": "Ajuste aprovado para teste tenant.",
        "approval_id": "approval-test-1",
    }
    try:
        upsert_target(
            db,
            org_slug="tenant-b",
            target_id="target-b",
            payload=payload,
            actor_ref="actor:b",
            now_ts=2,
        )
    except LookupError as exc:
        assert str(exc) == "OBJECTIVE_NOT_FOUND"
    else:
        raise AssertionError("cross-tenant target binding should be blocked")


def test_active_objective_limit_is_five_per_tenant():
    db = _db()
    for index in range(5):
        create_objective(
            db,
            org_slug="tenant-a",
            objective_id=f"obj-{index}",
            payload=_payload(f"Objetivo {index}"),
            actor_ref="actor:a",
            now_ts=index + 1,
        )
        db.commit()
    try:
        create_objective(
            db,
            org_slug="tenant-a",
            objective_id="obj-6",
            payload=_payload("Objetivo 6"),
            actor_ref="actor:a",
            now_ts=7,
        )
    except ValueError as exc:
        assert str(exc) == "ACTIVE_OBJECTIVE_LIMIT_REACHED"
    else:
        raise AssertionError("sixth active objective should be blocked")


def test_target_changes_create_version_history():
    db = _db()
    base_payload = {
        "objective_id": None,
        "kpi_code": "operational_reliability",
        "target_value": 99,
        "warning_threshold": 95,
        "critical_threshold": 90,
        "weight": 0.5,
        "minimum_sample_size": 20,
        "enabled": True,
        "proposal_enabled": True,
        "change_reason": "Meta inicial aprovada pelo administrador.",
        "approval_id": "approval-001",
    }
    first = upsert_target(
        db,
        org_slug="tenant-a",
        target_id="target-a",
        version_id="version-a1",
        payload=base_payload,
        actor_ref="actor:a",
        now_ts=100,
    )
    db.commit()
    second_payload = {
        **base_payload,
        "target_value": 99.5,
        "change_reason": "Calibração após revisão da amostra real.",
        "approval_id": "approval-002",
    }
    second = upsert_target(
        db,
        org_slug="tenant-a",
        target_id="ignored-new-id",
        version_id="version-a2",
        payload=second_payload,
        actor_ref="actor:a",
        now_ts=200,
    )
    db.commit()

    assert first["id"] == second["id"] == "target-a"
    assert first["version"] == 1
    assert second["version"] == 2
    history = list_target_history(
        db,
        org_slug="tenant-a",
        kpi_code="operational_reliability",
    )
    assert [row["version"] for row in history] == [2, 1]
    assert history[0]["effective_to"] is None
    assert history[1]["effective_to"] == 200
    assert history[0]["approval_id"] == "approval-002"
    assert history[1]["target_value"] == 99
