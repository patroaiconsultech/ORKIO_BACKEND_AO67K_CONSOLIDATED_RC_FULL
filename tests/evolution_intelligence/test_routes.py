from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.routes.evolution_intelligence import (
    EvolutionIntelligenceRouterDeps,
    build_evolution_intelligence_router,
)


def _engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE evolution_objectives (
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, name TEXT NOT NULL,
                description TEXT NOT NULL, category TEXT NOT NULL,
                priority INTEGER NOT NULL, status TEXT NOT NULL,
                starts_at INTEGER, ends_at INTEGER, owner_ref TEXT NOT NULL,
                success_definition TEXT NOT NULL, proposal_policy TEXT NOT NULL,
                human_approval_required BOOLEAN NOT NULL, version INTEGER NOT NULL,
                created_by TEXT NOT NULL, updated_by TEXT NOT NULL,
                created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE evolution_kpi_targets (
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, objective_id TEXT,
                scope_key TEXT NOT NULL,
                kpi_code TEXT NOT NULL, target_value REAL NOT NULL,
                warning_threshold REAL NOT NULL, critical_threshold REAL NOT NULL,
                weight REAL NOT NULL, minimum_sample_size INTEGER NOT NULL,
                enabled BOOLEAN NOT NULL, proposal_enabled BOOLEAN NOT NULL,
                auto_apply_enabled BOOLEAN NOT NULL, version INTEGER NOT NULL,
                starts_at INTEGER, ends_at INTEGER, created_by TEXT NOT NULL,
                updated_by TEXT NOT NULL, created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE evolution_kpi_target_versions (
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, target_id TEXT NOT NULL,
                objective_id TEXT, scope_key TEXT NOT NULL, kpi_code TEXT NOT NULL,
                version INTEGER NOT NULL, target_value REAL NOT NULL,
                warning_threshold REAL NOT NULL, critical_threshold REAL NOT NULL,
                weight REAL NOT NULL, minimum_sample_size INTEGER NOT NULL,
                enabled BOOLEAN NOT NULL, proposal_enabled BOOLEAN NOT NULL,
                auto_apply_enabled BOOLEAN NOT NULL, effective_from INTEGER NOT NULL,
                effective_to INTEGER, changed_by TEXT NOT NULL,
                change_reason TEXT NOT NULL, approval_id TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
        """))
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
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL,
                snapshot_id TEXT NOT NULL UNIQUE,
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
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL,
                snapshot_id TEXT NOT NULL, event_type TEXT NOT NULL,
                reason TEXT NOT NULL, approval_id TEXT NOT NULL,
                actor_ref TEXT NOT NULL, metadata_json TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                UNIQUE(snapshot_id, event_type)
            )
        """))
        conn.execute(text("""
            CREATE TABLE audit_logs (
                id TEXT PRIMARY KEY, org_slug TEXT NOT NULL, user_id TEXT,
                action TEXT, meta TEXT, request_id TEXT, path TEXT,
                status_code INTEGER, latency_ms INTEGER, created_at INTEGER
            )
        """))
    return engine


def _app():
    engine = _engine()
    sequence = iter(range(1000))

    def get_db():
        db = Session(engine)
        try:
            yield db
        finally:
            db.close()

    def require_admin_access():
        return {"sub": "admin-a", "org_slug": "tenant-a", "role": "admin"}

    def get_request_org(admin, requested):
        canonical = admin["org_slug"]
        if requested and requested != canonical:
            raise HTTPException(status_code=403, detail="TENANT_SCOPE_MISMATCH")
        return canonical

    app = FastAPI()
    app.state.runtime_identity = {
        "release_id": "orkio-test",
        "commit_sha": "a" * 40,
        "deployment_id": "deploy-test",
        "runtime_main_sha256": "b" * 64,
        "migration_in_sync": True,
    }
    app.state.evolution_intelligence_status = "validated"
    app.state.evolution_intelligence_config = {
        "version": "ORKIO-EVOLUTION-INTELLIGENCE-R1.1",
        "environment": "unknown",
        "center_enabled": True,
        "kpi_collection_enabled": True,
        "config_write_enabled": False,
        "health_snapshot_write_enabled": False,
        "proposal_generation_enabled": False,
        "proposal_only": True,
        "diff_preview_enabled": True,
        "write_enabled": False,
        "auto_apply_enabled": False,
        "human_approval_required": True,
        "rollback_required": True,
        "valid": True,
        "violations": [],
    }
    app.include_router(
        build_evolution_intelligence_router(
            EvolutionIntelligenceRouterDeps(
                get_db=get_db,
                require_admin_access=require_admin_access,
                get_request_org=get_request_org,
                new_id=lambda: f"id{next(sequence):08d}",
                now_ts=lambda: 1_700_000_000,
                actor_reference=lambda value: f"actor:{value or 'unknown'}",
                logger=__import__("logging").getLogger("test"),
            )
        )
    )
    return app, engine


def test_readonly_inventory_and_health(monkeypatch):
    monkeypatch.setenv("EVOLUTION_CONFIG_WRITE_ENABLED", "false")
    app, _ = _app()
    with TestClient(app) as client:
        inventory = client.get("/api/admin/evolution/intelligence/inventory")
        assert inventory.status_code == 200
        assert inventory.json()["count"] == 7
        assert inventory.json()["write_executed"] is False

        health = client.get("/api/admin/evolution/intelligence/health/preview")
        assert health.status_code == 200
        assert health.json()["release_identity"]["release_id"] == "orkio-test"
        assert health.json()["provenance"]["collector_version"] == "ORKIO-EVOLUTION-COLLECTORS-R2"
        assert health.json()["provenance"]["source_version"] == "ORKIO-EVOLUTION-SOURCES-R2"
        assert "health_coverage" in health.json()
        assert "unknown_kpis" in health.json()
        assert health.json()["write_executed"] is False


def test_tenant_header_mismatch_is_blocked():
    app, _ = _app()
    with TestClient(app) as client:
        response = client.get(
            "/api/admin/evolution/intelligence/objectives",
            headers={"X-Org-Slug": "tenant-b"},
        )
        assert response.status_code == 403


def test_config_write_disabled_by_default():
    app, _ = _app()
    with TestClient(app) as client:
        response = client.post(
            "/api/admin/evolution/intelligence/objectives",
            json={
                "approved": True,
                "name": "Confiabilidade operacional",
                "description": "Aumentar a confiabilidade operacional da plataforma.",
                "category": "technical_reliability",
                "priority": 100,
                "status": "active",
                "owner_ref": "CTO",
                "success_definition": "Saúde técnica acima de 90 por 30 dias.",
                "proposal_policy": "proposal_only",
                "human_approval_required": True,
            },
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "EVOLUTION_CONFIG_WRITE_DISABLED"


def test_objective_write_requires_flag_and_is_audited(monkeypatch):
    monkeypatch.setenv("EVOLUTION_CONFIG_WRITE_ENABLED", "true")
    app, engine = _app()
    with TestClient(app) as client:
        response = client.post(
            "/api/admin/evolution/intelligence/objectives",
            json={
                "approved": True,
                "name": "Confiabilidade operacional",
                "description": "Aumentar a confiabilidade operacional da plataforma.",
                "category": "technical_reliability",
                "priority": 100,
                "status": "active",
                "owner_ref": "CTO",
                "success_definition": "Saúde técnica acima de 90 por 30 dias.",
                "proposal_policy": "proposal_only",
                "human_approval_required": True,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["org_slug"] == "tenant-a"
        assert body["write_executed"] is True
        with engine.connect() as conn:
            audit_count = conn.execute(
                text(
                    "SELECT COUNT(*) FROM audit_logs "
                    "WHERE org_slug='tenant-a' "
                    "AND action='evolution_intelligence.objective.created'"
                )
            ).scalar_one()
        assert audit_count == 1
        audit_response = client.get(
            "/api/admin/evolution/intelligence/audit"
        )
        assert audit_response.status_code == 200
        assert audit_response.json()["count"] == 1
        assert (
            audit_response.json()["items"][0]["action"]
            == "evolution_intelligence.objective.created"
        )


def test_runtime_exposes_governance_identity():
    app, _ = _app()
    with TestClient(app) as client:
        response = client.get("/api/admin/evolution/intelligence/runtime")
        assert response.status_code == 200
        body = response.json()
        assert body["evolution_center_enabled"] is True
        assert body["evolution_proposal_only"] is True
        assert body["evolution_write_enabled"] is False
        assert body["evolution_auto_apply_enabled"] is False
        assert body["evolution_governance_validated"] is True
        assert body["evolution_governance_consistent"] is True
        assert body["kpi_registry_version"] == "ORKIO-EVOLUTION-KPI-REGISTRY-R2"


def test_target_version_and_snapshot_event_routes(monkeypatch):
    monkeypatch.setenv("EVOLUTION_CONFIG_WRITE_ENABLED", "true")
    monkeypatch.setenv("EVOLUTION_HEALTH_SNAPSHOT_WRITE_ENABLED", "true")
    app, _ = _app()
    with TestClient(app) as client:
        target = client.put(
            "/api/admin/evolution/intelligence/targets",
            json={
                "approved": True,
                "objective_id": None,
                "kpi_code": "operational_reliability",
                "target_value": 99,
                "warning_threshold": 95,
                "critical_threshold": 90,
                "weight": 0.5,
                "minimum_sample_size": 20,
                "enabled": True,
                "proposal_enabled": True,
                "auto_apply_enabled": False,
                "change_reason": "Meta inicial aprovada no staging.",
                "approval_id": "approval-target-1",
            },
        )
        assert target.status_code == 200
        assert target.json()["version"] == 1

        history = client.get(
            "/api/admin/evolution/intelligence/targets/history",
            params={"kpi_code": "operational_reliability"},
        )
        assert history.status_code == 200
        assert history.json()["count"] == 1
        assert history.json()["items"][0]["approval_id"] == "approval-target-1"

        captured = client.post(
            "/api/admin/evolution/intelligence/health/snapshots/capture",
            json={
                "approved": True,
                "reason": "Captura inicial aprovada no staging.",
                "objective_id": None,
            },
        )
        assert captured.status_code == 200
        snapshot_id = captured.json()["id"]
        assert captured.json()["immutable"] is True

        invalidated = client.post(
            f"/api/admin/evolution/intelligence/health/snapshots/{snapshot_id}/invalidate",
            json={
                "approved": True,
                "reason": "Fonte invalidada após revisão administrativa.",
                "approval_id": "approval-invalidate-1",
            },
        )
        assert invalidated.status_code == 200
        assert invalidated.json()["valid"] is False

        snapshots = client.get(
            "/api/admin/evolution/intelligence/health/snapshots"
        )
        assert snapshots.status_code == 200
        assert snapshots.json()["items"][0]["valid"] is False

        events = client.get(
            "/api/admin/evolution/intelligence/health/snapshots/events",
            params={"snapshot_id": snapshot_id},
        )
        assert events.status_code == 200
        assert events.json()["count"] == 1
