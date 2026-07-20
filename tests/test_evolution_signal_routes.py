from __future__ import annotations

import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.routes.evolution_signals import (
    EvolutionSignalsRouterDeps,
    build_evolution_signals_router,
)


def _schema(engine) -> None:
    statements = [
        """
        CREATE TABLE agents (
            id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, name TEXT NOT NULL,
            description TEXT, system_prompt TEXT, provider TEXT, model TEXT,
            tool_policy TEXT, voice_id TEXT, avatar_url TEXT,
            strict_mode BOOLEAN, rag_enabled BOOLEAN
        )
        """,
        """
        CREATE TABLE agent_knowledge (
            id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, agent_id TEXT NOT NULL,
            file_id TEXT NOT NULL, enabled BOOLEAN NOT NULL, created_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE audit_logs (
            id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, user_id TEXT,
            action TEXT NOT NULL, meta TEXT, request_id TEXT, path TEXT,
            status_code INTEGER, latency_ms INTEGER, created_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE admin_evolution_proposals (
            proposal_id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, status TEXT NOT NULL,
            rollback_plan TEXT, checklist_json TEXT, write_allowed BOOLEAN NOT NULL,
            execution_allowed BOOLEAN NOT NULL, human_approval_required BOOLEAN NOT NULL,
            updated_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE admin_evolution_executions (
            execution_id TEXT PRIMARY KEY, proposal_id TEXT NOT NULL,
            org_slug TEXT NOT NULL, status TEXT NOT NULL, mode TEXT NOT NULL,
            result_json TEXT, started_at BIGINT, finished_at BIGINT,
            created_at BIGINT NOT NULL, updated_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE agent_capability_evaluations (
            evaluation_id TEXT PRIMARY KEY, org_slug TEXT NOT NULL,
            agent_id TEXT NOT NULL, capability_id TEXT NOT NULL,
            evaluation_key TEXT NOT NULL, status TEXT NOT NULL,
            score INTEGER NOT NULL, confidence INTEGER NOT NULL,
            evidence_ref TEXT NOT NULL, notes TEXT, evaluator_ref TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )
        """,
        """
        CREATE TABLE platform_evolution_metric_snapshots (
            snapshot_id TEXT PRIMARY KEY, snapshot_group_id TEXT NOT NULL,
            org_slug TEXT NOT NULL, metric_key TEXT NOT NULL, scope_type TEXT NOT NULL,
            scope_id TEXT, score INTEGER, confidence INTEGER NOT NULL,
            sample_count INTEGER NOT NULL, signal_status TEXT NOT NULL,
            formula_version TEXT NOT NULL, window_start BIGINT NOT NULL,
            window_end BIGINT NOT NULL, source_json TEXT NOT NULL,
            missing_sources_json TEXT NOT NULL, evidence_refs_json TEXT NOT NULL,
            captured_by TEXT NOT NULL, capture_reason TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )
        """,
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
        conn.execute(
            text(
                """
                INSERT INTO agents (
                    id, org_slug, name, description, system_prompt, provider,
                    model, tool_policy, voice_id, avatar_url, strict_mode, rag_enabled
                ) VALUES (
                    'a1', 'public', 'Orion', 'Tech', 'prompt', 'openai',
                    'gpt', 'readonly', 'echo', '/orion.png', 1, 1
                )
                """
            )
        )


def _app(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    _schema(engine)
    SessionLocal = sessionmaker(bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def require_admin_access(
        authorization: str | None = Header(default=None),
    ):
        if authorization != "Bearer admin-token":
            raise HTTPException(status_code=401, detail="unauthorized")
        return {"id": "admin-1", "org": "public", "role": "admin"}

    def get_request_org(user, x_org_slug):
        org = str(user.get("org") or "")
        if x_org_slug and x_org_slug != org:
            raise HTTPException(status_code=403, detail="TENANT_MISMATCH")
        return org

    counter = {"value": 0}

    def new_id():
        counter["value"] += 1
        return f"id-{counter['value']}"

    app = FastAPI()
    app.include_router(
        build_evolution_signals_router(
            EvolutionSignalsRouterDeps(
                get_db=get_db,
                require_admin_access=require_admin_access,
                get_request_org=get_request_org,
                new_id=new_id,
                now_ts=lambda: 1_800_000_000,
                logger=type(
                    "Logger",
                    (),
                    {"exception": staticmethod(lambda *args, **kwargs: None)},
                )(),
            )
        )
    )
    return app, engine


def test_current_requires_admin_and_is_readonly(monkeypatch):
    app, engine = _app(monkeypatch)
    client = TestClient(app)

    assert client.get("/api/admin/evolution/signals/current").status_code == 401
    response = client.get(
        "/api/admin/evolution/signals/current",
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["write_executed"] is False
    assert body["org_slug"] == "public"
    with engine.begin() as conn:
        assert conn.execute(
            text("SELECT COUNT(*) FROM platform_evolution_metric_snapshots")
        ).scalar_one() == 0


def test_current_blocks_tenant_mismatch(monkeypatch):
    app, _ = _app(monkeypatch)
    client = TestClient(app)
    response = client.get(
        "/api/admin/evolution/signals/current",
        headers={
            "Authorization": "Bearer admin-token",
            "X-Org-Slug": "other",
        },
    )
    assert response.status_code == 403


def test_writes_are_disabled_by_default(monkeypatch):
    monkeypatch.delenv("EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED", raising=False)
    monkeypatch.delenv("EVOLUTION_AGENT_EVAL_WRITE_ENABLED", raising=False)
    app, _ = _app(monkeypatch)
    client = TestClient(app)
    headers = {"Authorization": "Bearer admin-token"}

    capture = client.post(
        "/api/admin/evolution/signals/snapshots/capture",
        headers=headers,
        json={"approved": True, "reason": "controlled capture test"},
    )
    assert capture.status_code == 403
    assert capture.json()["detail"] == "EVOLUTION_SIGNAL_CAPTURE_DISABLED"

    evaluation = client.post(
        "/api/admin/evolution/agent-evaluations",
        headers=headers,
        json={
            "agent_id": "a1",
            "capability_id": "architecture",
            "evaluation_key": "golden-1",
            "status": "passed",
            "score": 90,
            "confidence": 90,
            "evidence_ref": "test:golden-1",
        },
    )
    assert evaluation.status_code == 403
    assert evaluation.json()["detail"] == "EVOLUTION_AGENT_EVAL_WRITE_DISABLED"


def test_explicit_evaluation_and_capture_are_audited(monkeypatch):
    monkeypatch.setenv("EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED", "true")
    monkeypatch.setenv("EVOLUTION_AGENT_EVAL_WRITE_ENABLED", "true")
    app, engine = _app(monkeypatch)
    client = TestClient(app)
    headers = {"Authorization": "Bearer admin-token"}

    evaluation = client.post(
        "/api/admin/evolution/agent-evaluations",
        headers=headers,
        json={
            "agent_id": "a1",
            "capability_id": "architecture",
            "evaluation_key": "golden-1",
            "status": "passed",
            "score": 90,
            "confidence": 90,
            "evidence_ref": "test:golden-1",
        },
    )
    assert evaluation.status_code == 200
    assert evaluation.json()["write_executed"] is True

    current = client.get(
        "/api/admin/evolution/signals/current",
        headers=headers,
    )
    assert current.status_code == 200
    agent = current.json()["agents"][0]
    assert agent["score"] == 90
    assert agent["sample_count"] == 1

    capture = client.post(
        "/api/admin/evolution/signals/snapshots/capture",
        headers=headers,
        json={"approved": True, "reason": "controlled capture test"},
    )
    assert capture.status_code == 200
    assert capture.json()["write_executed"] is True

    history = client.get(
        "/api/admin/evolution/signals/history",
        headers=headers,
    )
    assert history.status_code == 200
    assert history.json()["count"] == 8

    with engine.begin() as conn:
        actions = {
            row[0]
            for row in conn.execute(
                text("SELECT action FROM audit_logs ORDER BY created_at")
            ).all()
        }
    assert "evolution_signals.agent_evaluation.recorded" in actions
    assert "evolution_signals.snapshot.captured" in actions
