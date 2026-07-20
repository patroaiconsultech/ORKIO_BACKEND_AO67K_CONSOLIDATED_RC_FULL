from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import uuid

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


DATABASE_URL = os.getenv("AUTH_RESET_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="AUTH_RESET_TEST_DATABASE_URL is required for disposable PostgreSQL validation",
)

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_PATH = ROOT / "alembic" / "versions" / "0038_patch_auth_password_reset_tokens.py"


def _load_migration():
    spec = importlib.util.spec_from_file_location("auth_reset_001_r2_pg", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ops(connection):
    return Operations(MigrationContext.configure(connection))


def test_postgresql_upgrade_downgrade_reupgrade_in_isolated_schema():
    migration = _load_migration()
    schema = f"auth_reset_001_{uuid.uuid4().hex[:12]}"
    engine = sa.create_engine(DATABASE_URL, future=True)

    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")
        connection.execute(sa.text(f'CREATE SCHEMA "{schema}"'))
        try:
            connection.execute(sa.text(f'SET search_path TO "{schema}"'))
            migration.op = _ops(connection)

            migration.upgrade()
            assert connection.execute(sa.text("SELECT to_regclass('password_reset_tokens')")).scalar_one()
            migration.downgrade()
            assert connection.execute(sa.text("SELECT to_regclass('password_reset_tokens')")).scalar_one() is None
            migration.upgrade()
            assert connection.execute(sa.text("SELECT to_regclass('password_reset_tokens')")).scalar_one()
        finally:
            connection.execute(sa.text("SET search_path TO public"))
            connection.execute(sa.text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))


def test_postgresql_existing_table_in_other_schema_fails_closed():
    migration = _load_migration()
    target = f"auth_reset_target_{uuid.uuid4().hex[:10]}"
    other = f"auth_reset_other_{uuid.uuid4().hex[:10]}"
    engine = sa.create_engine(DATABASE_URL, future=True)

    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")
        connection.execute(sa.text(f'CREATE SCHEMA "{target}"'))
        connection.execute(sa.text(f'CREATE SCHEMA "{other}"'))
        try:
            connection.execute(sa.text(
                f'CREATE TABLE "{other}".password_reset_tokens (id VARCHAR PRIMARY KEY)'
            ))
            connection.execute(sa.text(f'SET search_path TO "{target}"'))
            migration.op = _ops(connection)
            with pytest.raises(RuntimeError, match="AUTH_RESET_001_TABLE_ALREADY_EXISTS"):
                migration.upgrade()
            assert connection.execute(sa.text(
                f"SELECT to_regclass('{target}.password_reset_tokens')"
            )).scalar_one() is None
        finally:
            connection.execute(sa.text("SET search_path TO public"))
            connection.execute(sa.text(f'DROP SCHEMA IF EXISTS "{target}" CASCADE'))
            connection.execute(sa.text(f'DROP SCHEMA IF EXISTS "{other}" CASCADE'))
