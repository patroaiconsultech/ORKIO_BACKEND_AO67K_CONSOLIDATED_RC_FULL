from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import create_engine, text

from runtime.release_identity import (
    CONTRACT_VERSION,
    actor_reference,
    build_release_identity,
    detect_database_revisions,
    detect_migration_heads,
    emit_boot_identity,
)


def _write_migration(path: Path, revision: str, down_revision):
    path.write_text(
        "\n".join(
            [
                f"revision = {revision!r}",
                f"down_revision = {down_revision!r}",
            ]
        ),
        encoding="utf-8",
    )


def _database_with_revision(revision: str):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(64) NOT NULL)"))
        conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:revision)"),
            {"revision": revision},
        )
    return engine


def test_detect_migration_heads(tmp_path):
    versions = tmp_path / "alembic" / "versions"
    versions.mkdir(parents=True)
    _write_migration(versions / "0001.py", "0001", None)
    _write_migration(versions / "0002.py", "0002", "0001")
    _write_migration(versions / "0003.py", "0003", "0002")

    assert detect_migration_heads(tmp_path) == ("0003",)


def test_detect_database_revisions_is_read_only():
    engine = _database_with_revision("0038")
    revisions, status = detect_database_revisions(engine)
    assert revisions == ("0038",)
    assert status == "ok"

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM alembic_version")).scalar_one()
    assert count == 1


def test_build_release_identity_correlates_code_and_database(tmp_path):
    main_path = tmp_path / "main.py"
    main_path.write_text("app = object()\n", encoding="utf-8")
    versions = tmp_path / "alembic" / "versions"
    versions.mkdir(parents=True)
    _write_migration(
        versions / "0038.py",
        "0038_patch_auth_password_reset_tokens",
        None,
    )
    engine = _database_with_revision("0038_patch_auth_password_reset_tokens")

    app = SimpleNamespace(routes=[1, 2, 3])
    env = {
        "APP_ENV": "staging",
        "RAILWAY_GIT_COMMIT_SHA": "A" * 40,
        "RAILWAY_GIT_BRANCH": "feature/release identity",
        "RAILWAY_DEPLOYMENT_ID": "deploy-123",
        "ORKIO_RELEASE_ID": "release/test",
        "EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED": "true",
        "EVOLUTION_MARCO_ZERO_WRITE_ENABLED": "false",
        "EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED": "0",
        "EVOLUTION_AGENT_EVAL_WRITE_ENABLED": "no",
        "DATABASE_URL": "postgresql://must-not-leak",
        "JWT_SECRET": "must-not-leak",
    }

    identity = build_release_identity(
        app,
        app_version="2.4.0",
        repo_root=tmp_path,
        runtime_main_path=main_path,
        environ=env,
        database=engine,
        authenticated_org="tenant-a",
        authority_scope="tenant_admin",
    )

    assert identity["contract_version"] == CONTRACT_VERSION
    assert identity["release_id"] == "release/test"
    assert identity["commit_sha"] == "a" * 40
    assert identity["branch"] == "feature/release_identity"
    assert identity["route_count"] == 3
    assert identity["migration_code_heads"] == [
        "0038_patch_auth_password_reset_tokens"
    ]
    assert identity["migration_database_revisions"] == [
        "0038_patch_auth_password_reset_tokens"
    ]
    assert identity["migration_database_revision"] == (
        "0038_patch_auth_password_reset_tokens"
    )
    assert identity["migration_database_status"] == "ok"
    assert identity["migration_in_sync"] is True
    assert identity["authenticated_org"] == "tenant-a"
    assert identity["authority_scope"] == "tenant_admin"
    assert len(identity["runtime_main_sha256"]) == 64
    assert identity["governance_flags"] == {
        "EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED": True,
        "EVOLUTION_MARCO_ZERO_WRITE_ENABLED": False,
        "EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED": False,
        "EVOLUTION_AGENT_EVAL_WRITE_ENABLED": False,
    }

    serialized = repr(identity)
    assert "postgresql://must-not-leak" not in serialized
    assert "must-not-leak" not in serialized


def test_migration_mismatch_is_observable(tmp_path):
    main_path = tmp_path / "main.py"
    main_path.write_text("# test\n", encoding="utf-8")
    versions = tmp_path / "alembic" / "versions"
    versions.mkdir(parents=True)
    _write_migration(versions / "0038.py", "0038", None)
    engine = _database_with_revision("0037")

    identity = build_release_identity(
        SimpleNamespace(routes=[]),
        app_version="x",
        repo_root=tmp_path,
        runtime_main_path=main_path,
        database=engine,
    )
    assert identity["migration_code_heads"] == ["0038"]
    assert identity["migration_database_revisions"] == ["0037"]
    assert identity["migration_in_sync"] is False


def test_database_failure_is_sanitized(tmp_path):
    main_path = tmp_path / "main.py"
    main_path.write_text("# test\n", encoding="utf-8")
    engine = create_engine("sqlite+pysqlite:///:memory:")

    identity = build_release_identity(
        SimpleNamespace(routes=[]),
        app_version="x",
        repo_root=tmp_path,
        runtime_main_path=main_path,
        database=engine,
    )
    assert identity["migration_database_revisions"] == []
    assert identity["migration_database_status"].startswith("error:")
    assert identity["migration_in_sync"] is None
    assert "SELECT" not in repr(identity)


def test_invalid_commit_and_actor_are_sanitized(tmp_path):
    main_path = tmp_path / "main.py"
    main_path.write_text("# test\n", encoding="utf-8")
    app = SimpleNamespace(routes=[])

    identity = build_release_identity(
        app,
        app_version="x",
        repo_root=tmp_path,
        runtime_main_path=main_path,
        environ={"RAILWAY_GIT_COMMIT_SHA": "not a sha; secret=abc"},
    )

    assert identity["commit_sha"] == "unknown"
    assert identity["release_id"].startswith("orkio-file-")
    assert actor_reference("admin@example.test").startswith("actor_sha256:")
    assert "admin@example.test" not in actor_reference("admin@example.test")


def test_emit_boot_identity_logs_only_sanitized_fields(tmp_path, caplog):
    main_path = tmp_path / "main.py"
    main_path.write_text("# boot\n", encoding="utf-8")
    versions = tmp_path / "alembic" / "versions"
    versions.mkdir(parents=True)
    _write_migration(versions / "0038.py", "0038", None)
    engine = _database_with_revision("0038")
    app = SimpleNamespace(routes=[1])
    logger = logging.getLogger("release-identity-r11-test")

    with caplog.at_level(logging.INFO, logger=logger.name):
        identity = emit_boot_identity(
            logger,
            app,
            app_version="2.4.0",
            repo_root=tmp_path,
            runtime_main_path=main_path,
            database=engine,
            environ={
                "ORKIO_COMMIT_SHA": "b" * 40,
                "DATABASE_URL": "postgresql://never-log",
                "EVOLUTION_MARCO_ZERO_WRITE_ENABLED": "false",
            },
        )

    assert identity["commit_sha"] == "b" * 40
    output = "\n".join(caplog.messages)
    assert "ORKIO_BOOT_IDENTITY" in output
    assert "postgresql://never-log" not in output
    assert "migration_in_sync=True" in output
    assert "marco_zero_write_enabled=False" in output
