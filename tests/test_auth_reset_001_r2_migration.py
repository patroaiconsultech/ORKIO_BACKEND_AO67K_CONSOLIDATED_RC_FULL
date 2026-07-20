from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


ROOT = Path(__file__).resolve().parents[1]
MIGRATION_PATH = ROOT / "alembic" / "versions" / "0038_patch_auth_password_reset_tokens.py"


def _load_migration():
    spec = importlib.util.spec_from_file_location("auth_reset_001_r2_migration", MIGRATION_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _operations(connection):
    return Operations(MigrationContext.configure(connection))


def _create_compatible_table(connection):
    connection.execute(sa.text("""
        CREATE TABLE password_reset_tokens (
            id VARCHAR NOT NULL PRIMARY KEY,
            lead_id VARCHAR NOT NULL,
            token_hash VARCHAR NOT NULL,
            expires_at BIGINT NOT NULL,
            used_at BIGINT NULL,
            created_at BIGINT NOT NULL
        )
    """))


def test_revision_contract_is_linear_from_0037():
    migration = _load_migration()
    assert migration.revision == "0038_patch_auth_password_reset_tokens"
    assert migration.down_revision == "0037_patch_evolution_signals_metrics"
    assert migration.branch_labels is None
    assert migration.depends_on is None


def test_upgrade_creates_exact_contract_and_indexes():
    migration = _load_migration()
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        migration.op = _operations(connection)
        migration.upgrade()
        inspector = sa.inspect(connection)
        columns = {column["name"]: column for column in inspector.get_columns("password_reset_tokens")}
        assert set(columns) == {"id", "lead_id", "token_hash", "expires_at", "used_at", "created_at"}
        assert columns["used_at"]["nullable"] is True
        assert all(columns[name]["nullable"] is False for name in set(columns) - {"used_at"})
        assert inspector.get_pk_constraint("password_reset_tokens")["constrained_columns"] == ["id"]
        indexes = {i["name"]: (i["column_names"], i["unique"]) for i in inspector.get_indexes("password_reset_tokens")}
        assert indexes == {
            "ix_password_reset_tokens_lead": (["lead_id"], 0),
            "ix_password_reset_tokens_token_hash": (["token_hash"], 0),
        }


def test_existing_compatible_table_fails_closed_and_is_preserved():
    migration = _load_migration()
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        _create_compatible_table(connection)
        connection.execute(sa.text("""
            INSERT INTO password_reset_tokens
            (id, lead_id, token_hash, expires_at, used_at, created_at)
            VALUES ('existing', 'lead', 'hash', 10, NULL, 1)
        """))
        migration.op = _operations(connection)
        with pytest.raises(RuntimeError, match="AUTH_RESET_001_TABLE_ALREADY_EXISTS"):
            migration.upgrade()
        assert connection.execute(sa.text("SELECT COUNT(*) FROM password_reset_tokens")).scalar_one() == 1


def test_existing_incompatible_table_fails_closed_and_is_preserved():
    migration = _load_migration()
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE password_reset_tokens (id VARCHAR PRIMARY KEY)"))
        migration.op = _operations(connection)
        with pytest.raises(RuntimeError, match="AUTH_RESET_001_TABLE_ALREADY_EXISTS"):
            migration.upgrade()
        assert "password_reset_tokens" in sa.inspect(connection).get_table_names()


def test_same_name_wrong_index_definition_is_rejected_before_downgrade():
    migration = _load_migration()
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        migration.op = _operations(connection)
        migration.upgrade()
        connection.execute(sa.text("DROP INDEX ix_password_reset_tokens_token_hash"))
        connection.execute(sa.text(
            "CREATE INDEX ix_password_reset_tokens_token_hash ON password_reset_tokens (lead_id)"
        ))
        with pytest.raises(RuntimeError, match="AUTH_RESET_001_SCHEMA_MISMATCH"):
            migration.downgrade()
        assert "password_reset_tokens" in sa.inspect(connection).get_table_names()


def test_type_mismatch_is_rejected_by_contract_validator():
    migration = _load_migration()
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("""
            CREATE TABLE password_reset_tokens (
                id VARCHAR NOT NULL PRIMARY KEY,
                lead_id VARCHAR NOT NULL,
                token_hash VARCHAR NOT NULL,
                expires_at VARCHAR NOT NULL,
                used_at BIGINT NULL,
                created_at BIGINT NOT NULL
            )
        """))
        connection.execute(sa.text(
            "CREATE INDEX ix_password_reset_tokens_lead ON password_reset_tokens (lead_id)"
        ))
        connection.execute(sa.text(
            "CREATE INDEX ix_password_reset_tokens_token_hash ON password_reset_tokens (token_hash)"
        ))
        migration.op = _operations(connection)
        with pytest.raises(RuntimeError, match="type_mismatches"):
            migration._validate_contract(None)


def test_downgrade_removes_only_created_reset_token_table():
    migration = _load_migration()
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE users (id VARCHAR PRIMARY KEY)"))
        migration.op = _operations(connection)
        migration.upgrade()
        migration.downgrade()
        tables = set(sa.inspect(connection).get_table_names())
        assert "password_reset_tokens" not in tables
        assert "users" in tables


def test_downgrade_refuses_when_table_missing():
    migration = _load_migration()
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        migration.op = _operations(connection)
        with pytest.raises(RuntimeError, match="AUTH_RESET_001_DOWNGRADE_REFUSED"):
            migration.downgrade()
