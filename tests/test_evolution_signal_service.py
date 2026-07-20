from __future__ import annotations

import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.evolution_signal_service import (
    build_current_snapshot,
    capture_snapshot,
    list_history,
)


def _create_schema(engine) -> None:
    statements = [
        """
        CREATE TABLE agents (
            id TEXT PRIMARY KEY,
            org_slug TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            system_prompt TEXT,
            provider TEXT,
            model TEXT,
            tool_policy TEXT,
            voice_id TEXT,
            avatar_url TEXT,
            strict_mode BOOLEAN,
            rag_enabled BOOLEAN
        )
        """,
        """
        CREATE TABLE agent_knowledge (
            id TEXT PRIMARY KEY,
            org_slug TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            file_id TEXT NOT NULL,
            enabled BOOLEAN NOT NULL,
            created_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE audit_logs (
            id TEXT PRIMARY KEY,
            org_slug TEXT NOT NULL,
            user_id TEXT,
            action TEXT NOT NULL,
            meta TEXT,
            request_id TEXT,
            path TEXT,
            status_code INTEGER,
            latency_ms INTEGER,
            created_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE admin_evolution_proposals (
            proposal_id TEXT PRIMARY KEY,
            org_slug TEXT NOT NULL,
            status TEXT NOT NULL,
            rollback_plan TEXT,
            checklist_json TEXT,
            write_allowed BOOLEAN NOT NULL,
            execution_allowed BOOLEAN NOT NULL,
            human_approval_required BOOLEAN NOT NULL,
            updated_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE admin_evolution_executions (
            execution_id TEXT PRIMARY KEY,
            proposal_id TEXT NOT NULL,
            org_slug TEXT NOT NULL,
            status TEXT NOT NULL,
            mode TEXT NOT NULL,
            result_json TEXT,
            started_at BIGINT,
            finished_at BIGINT,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE agent_capability_evaluations (
            evaluation_id TEXT PRIMARY KEY,
            org_slug TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            capability_id TEXT NOT NULL,
            evaluation_key TEXT NOT NULL,
            status TEXT NOT NULL,
            score INTEGER NOT NULL,
            confidence INTEGER NOT NULL,
            evidence_ref TEXT NOT NULL,
            notes TEXT,
            evaluator_ref TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE platform_evolution_metric_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            snapshot_group_id TEXT NOT NULL,
            org_slug TEXT NOT NULL,
            metric_key TEXT NOT NULL,
            scope_type TEXT NOT NULL,
            scope_id TEXT,
            score INTEGER,
            confidence INTEGER NOT NULL,
            sample_count INTEGER NOT NULL,
            signal_status TEXT NOT NULL,
            formula_version TEXT NOT NULL,
            window_start BIGINT NOT NULL,
            window_end BIGINT NOT NULL,
            source_json TEXT NOT NULL,
            missing_sources_json TEXT NOT NULL,
            evidence_refs_json TEXT NOT NULL,
            captured_by TEXT NOT NULL,
            capture_reason TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )
        """,
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def _seed(db: Session, now: int) -> None:
    db.execute(
        text(
            """
            INSERT INTO agents (
                id, org_slug, name, description, system_prompt, provider,
                model, tool_policy, voice_id, avatar_url, strict_mode, rag_enabled
            ) VALUES
            ('a1', 'public', 'Orion', 'Tech', 'prompt', 'openai', 'gpt', 'readonly', 'echo', '/orion.png', 1, 1),
            ('a2', 'other', 'Other Tenant Agent', 'Other', 'prompt', 'openai', 'gpt', 'readonly', 'echo', '/other.png', 1, 1)
            """
        )
    )
    db.execute(
        text(
            """
            INSERT INTO agent_knowledge (id, org_slug, agent_id, file_id, enabled, created_at)
            VALUES ('k1', 'public', 'a1', 'f1', 1, :now)
            """
        ),
        {"now": now},
    )
    db.execute(
        text(
            """
            INSERT INTO admin_evolution_proposals (
                proposal_id, org_slug, status, rollback_plan, checklist_json,
                write_allowed, execution_allowed, human_approval_required, updated_at
            ) VALUES (
                'p1', 'public', 'approved', 'rollback', '["smoke"]',
                0, 0, 1, :now
            )
            """
        ),
        {"now": now},
    )
    db.execute(
        text(
            """
            INSERT INTO admin_evolution_executions (
                execution_id, proposal_id, org_slug, status, mode, result_json,
                started_at, finished_at, created_at, updated_at
            ) VALUES
            ('e1', 'p1', 'public', 'dry_run_completed', 'controlled_dry_run', '{}', :start, :finish, :start, :finish),
            ('e2', 'p1', 'public', 'failed', 'controlled_dry_run', '{}', :start, :finish, :start, :finish)
            """
        ),
        {"start": now - 20, "finish": now - 10},
    )
    db.execute(
        text(
            """
            INSERT INTO audit_logs (
                id, org_slug, user_id, action, meta, request_id, path,
                status_code, latency_ms, created_at
            ) VALUES (
                'audit1', 'public', 'admin', 'test', '{}', 'req1', '/api/test',
                200, 15, :now
            )
            """
        ),
        {"now": now},
    )
    db.execute(
        text(
            """
            INSERT INTO agent_capability_evaluations (
                evaluation_id, org_slug, agent_id, capability_id, evaluation_key,
                status, score, confidence, evidence_ref, notes, evaluator_ref, created_at
            ) VALUES
            ('v1', 'public', 'a1', 'architecture', 'golden-1', 'passed', 90, 90, 'test:golden-1', NULL, 'admin', :now),
            ('v2', 'public', 'a1', 'architecture', 'golden-2', 'failed', 50, 80, 'test:golden-2', NULL, 'admin', :now)
            """
        ),
        {"now": now},
    )
    db.commit()


def test_current_snapshot_is_tenant_isolated_and_evidence_based(monkeypatch):
    monkeypatch.setenv("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", "true")
    monkeypatch.setenv("ORKIO_ALLOW_AGENT_AUTO_WRITE", "false")
    monkeypatch.setenv("ORKIO_ALLOW_AGENT_AUTO_DEPLOY", "false")
    monkeypatch.setenv("ACCESS_GATE_SERVER_SIDE_ONLY", "true")

    engine = create_engine("sqlite+pysqlite:///:memory:")
    _create_schema(engine)
    now = 1_800_000_000
    with Session(engine) as db:
        _seed(db, now)
        result = build_current_snapshot(db, org_slug="public", now_ts=now)

    assert result["write_executed"] is False
    assert result["historical_trend"] is False
    assert result["total_metrics"] == 7
    assert all(agent["agent_id"] != "a2" for agent in result["agents"])
    assert len(result["agents"]) == 1

    by_key = {metric["key"]: metric for metric in result["metrics"]}
    assert by_key["operational_reliability"]["score"] == 50
    assert by_key["operational_reliability"]["sample_count"] == 2
    assert by_key["agent_knowledge"]["score"] is not None
    assert by_key["agent_knowledge"]["sample_count"] == 2
    assert by_key["evidence_observability"]["sample_count"] == 3
    assert result["measured_metrics"] == 7
    assert result["coverage_percent"] == 100


def test_zero_evidence_never_becomes_fake_score():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    _create_schema(engine)
    now = 1_800_000_000
    with Session(engine) as db:
        result = build_current_snapshot(db, org_slug="public", now_ts=now)

    by_key = {metric["key"]: metric for metric in result["metrics"]}
    assert by_key["operational_reliability"]["score"] is None
    assert by_key["operational_reliability"]["confidence"] == 0
    assert by_key["agent_knowledge"]["score"] is None
    assert by_key["agent_knowledge"]["confidence"] == 0
    assert by_key["evidence_observability"]["score"] is None
    assert by_key["evidence_observability"]["confidence"] == 0


def test_get_style_snapshot_does_not_write():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    _create_schema(engine)
    now = 1_800_000_000
    with Session(engine) as db:
        before = db.execute(
            text("SELECT COUNT(*) FROM platform_evolution_metric_snapshots")
        ).scalar_one()
        build_current_snapshot(db, org_slug="public", now_ts=now)
        after = db.execute(
            text("SELECT COUNT(*) FROM platform_evolution_metric_snapshots")
        ).scalar_one()
    assert before == after == 0


def test_explicit_capture_persists_platform_and_agent_rows():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    _create_schema(engine)
    now = 1_800_000_000
    ids = iter(f"id-{index}" for index in range(100))
    with Session(engine) as db:
        _seed(db, now)
        snapshot = build_current_snapshot(db, org_slug="public", now_ts=now)
        metrics_count, agents_count = capture_snapshot(
            db,
            snapshot=snapshot,
            snapshot_group_id="group-1",
            org_slug="public",
            actor_ref="admin",
            reason="human approved test capture",
            now_ts=now,
            id_factory=lambda: next(ids),
        )
        db.commit()
        rows = list_history(
            db,
            org_slug="public",
            cutoff=now - 1,
            metric_key=None,
            scope_type=None,
            limit=100,
        )

    assert metrics_count == 7
    assert agents_count == 1
    assert len(rows) == 8
    assert {row["scope_type"] for row in rows} == {"platform", "agent"}


def test_history_is_tenant_isolated():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    _create_schema(engine)
    now = 1_800_000_000
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO platform_evolution_metric_snapshots (
                    snapshot_id, snapshot_group_id, org_slug, metric_key,
                    scope_type, scope_id, score, confidence, sample_count,
                    signal_status, formula_version, window_start, window_end,
                    source_json, missing_sources_json, evidence_refs_json,
                    captured_by, capture_reason, created_at
                ) VALUES
                ('s1', 'g1', 'public', 'security_governance', 'platform', NULL, 90, 90, 10, 'measured', 'v1', :now, :now, '[]', '[]', '[]', 'admin', 'test reason', :now),
                ('s2', 'g2', 'other', 'security_governance', 'platform', NULL, 10, 10, 10, 'measured', 'v1', :now, :now, '[]', '[]', '[]', 'admin', 'test reason', :now)
                """
            ),
            {"now": now},
        )
    with Session(engine) as db:
        rows = list_history(
            db,
            org_slug="public",
            cutoff=now - 1,
            metric_key=None,
            scope_type=None,
            limit=100,
        )
    assert [row["snapshot_id"] for row in rows] == ["s1"]
