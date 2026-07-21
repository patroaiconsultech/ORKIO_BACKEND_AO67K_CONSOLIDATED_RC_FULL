import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.evolution_intelligence_service import (
    capture_health_snapshot,
    invalidate_health_snapshot,
    list_health_snapshot_events,
    list_health_snapshots,
)


def _db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE evolution_health_snapshots (
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, objective_id TEXT,
                captured_at INTEGER NOT NULL, window_start INTEGER NOT NULL,
                window_end INTEGER NOT NULL, project_health_score REAL,
                confidence REAL NOT NULL, data_coverage REAL NOT NULL,
                status TEXT NOT NULL, production_go BOOLEAN NOT NULL,
                dimensions_json TEXT NOT NULL, missing_kpis_json TEXT NOT NULL,
                blocker_kpis_json TEXT NOT NULL, release_id TEXT, commit_sha TEXT,
                deployment_id TEXT, runtime_main_sha256 TEXT,
                formula_version TEXT NOT NULL, captured_by TEXT NOT NULL,
                capture_reason TEXT NOT NULL, created_at INTEGER NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE evolution_health_snapshot_provenance (
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, snapshot_id TEXT NOT NULL UNIQUE,
                collector_version TEXT NOT NULL, source_version TEXT NOT NULL,
                release_id TEXT, commit_sha TEXT, deployment_id TEXT,
                window_start INTEGER NOT NULL, window_end INTEGER NOT NULL,
                sample_size INTEGER NOT NULL, confidence REAL NOT NULL,
                provenance_json TEXT NOT NULL, content_sha256 TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE evolution_health_snapshot_events (
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, snapshot_id TEXT NOT NULL,
                event_type TEXT NOT NULL, reason TEXT NOT NULL,
                approval_id TEXT NOT NULL, actor_ref TEXT NOT NULL,
                metadata_json TEXT NOT NULL, created_at INTEGER NOT NULL,
                UNIQUE(snapshot_id, event_type)
            )
        """))
        for table_name in (
            "evolution_health_snapshots",
            "evolution_health_snapshot_provenance",
            "evolution_health_snapshot_events",
        ):
            conn.execute(text(f"""
                CREATE TRIGGER trg_{table_name}_immutable_update
                BEFORE UPDATE ON {table_name}
                BEGIN
                    SELECT RAISE(ABORT, 'ORKIO_IMMUTABLE_RECORD:{table_name}');
                END
            """))
            conn.execute(text(f"""
                CREATE TRIGGER trg_{table_name}_immutable_delete
                BEFORE DELETE ON {table_name}
                BEGIN
                    SELECT RAISE(ABORT, 'ORKIO_IMMUTABLE_RECORD:{table_name}');
                END
            """))
    return Session(engine)


def _health():
    return {
        "formula_version": "ORKIO-EVOLUTION-HEALTH-R1.1",
        "generated_at": 1_000,
        "window_start": 100,
        "window_end": 1_000,
        "score": 88.0,
        "confidence": 0.8,
        "coverage": 0.85,
        "health_coverage": 0.85,
        "status": "warning",
        "production_go": True,
        "dimensions": {"technical": {"score": 90}},
        "missing_kpis": ["product_signal"],
        "unknown_kpis": ["product_signal"],
        "stale_kpis": [],
        "missing_dimensions": ["product"],
        "blocker_kpis": [],
        "blockers": [],
        "release_identity": {
            "release_id": "orkio-test",
            "commit_sha": "a" * 40,
            "deployment_id": "deploy-test",
            "runtime_main_sha256": "b" * 64,
        },
        "provenance": {
            "collector_version": "ORKIO-EVOLUTION-COLLECTORS-R2",
            "source_version": "ORKIO-EVOLUTION-SOURCES-R2",
            "release_id": "orkio-test",
            "commit_sha": "a" * 40,
            "deployment_id": "deploy-test",
            "window_start": 100,
            "window_end": 1_000,
            "sample_size": 42,
            "confidence": 0.8,
            "kpis": [],
        },
    }


def test_snapshot_is_append_only_and_has_provenance():
    db = _db()
    result = capture_health_snapshot(
        db,
        snapshot_id="snapshot-1",
        provenance_id="provenance-1",
        org_slug="tenant-a",
        objective_id=None,
        health=_health(),
        actor_ref="actor:a",
        reason="Captura aprovada para baseline.",
        now_ts=1_000,
    )
    db.commit()

    assert result["immutable"] is True
    assert len(result["content_sha256"]) == 64
    rows = list_health_snapshots(
        db,
        org_slug="tenant-a",
        objective_id=None,
        limit=10,
    )
    assert len(rows) == 1
    assert rows[0]["valid"] is True
    assert rows[0]["collector_version"] == "ORKIO-EVOLUTION-COLLECTORS-R2"
    assert rows[0]["sample_size"] == 42
    assert rows[0]["content_sha256"] == result["content_sha256"]

    with pytest.raises(Exception):
        db.execute(
            text(
                "UPDATE evolution_health_snapshots "
                "SET status='critical' WHERE id='snapshot-1'"
            )
        )
        db.commit()
    db.rollback()


def test_invalidation_is_an_event_and_preserves_snapshot():
    db = _db()
    capture_health_snapshot(
        db,
        snapshot_id="snapshot-1",
        provenance_id="provenance-1",
        org_slug="tenant-a",
        objective_id=None,
        health=_health(),
        actor_ref="actor:a",
        reason="Captura aprovada para baseline.",
        now_ts=1_000,
    )
    db.commit()

    event = invalidate_health_snapshot(
        db,
        event_id="event-1",
        org_slug="tenant-a",
        snapshot_id="snapshot-1",
        actor_ref="actor:a",
        reason="Fonte posteriormente considerada inválida.",
        approval_id="approval-1",
        now_ts=1_100,
    )
    db.commit()
    assert event["valid"] is False

    rows = list_health_snapshots(
        db,
        org_slug="tenant-a",
        objective_id=None,
        limit=10,
    )
    assert rows[0]["valid"] is False
    assert rows[0]["invalidation_event_id"] == "event-1"
    assert rows[0]["status"] == "warning"

    events = list_health_snapshot_events(
        db,
        org_slug="tenant-a",
        snapshot_id="snapshot-1",
        limit=10,
    )
    assert len(events) == 1
    assert events[0]["approval_id"] == "approval-1"

    with pytest.raises(LookupError):
        invalidate_health_snapshot(
            db,
            event_id="event-b",
            org_slug="tenant-b",
            snapshot_id="snapshot-1",
            actor_ref="actor:b",
            reason="Tentativa cross-tenant bloqueada.",
            approval_id="approval-b",
            now_ts=1_200,
        )
