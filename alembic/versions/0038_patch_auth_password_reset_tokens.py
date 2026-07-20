"""Restore the password-reset token schema required by the auth runtime.

Revision ID: 0038_patch_auth_password_reset_tokens
Revises: 0037_patch_evolution_signals_metrics
Create Date: 2026-07-20

AUTH-RESET-001 R2 — proposal-only
---------------------------------
Safety properties:
- creates the table only when it is absent from every visible non-system schema;
- refuses to adopt or mutate a pre-existing table;
- creates the relation in PostgreSQL current_schema();
- validates the exact created contract and index definitions;
- downgrade validates the contract before dropping the relation;
- never bootstraps schema from an HTTP request.

The migration intentionally fails closed when baseline identity, schema ownership,
or the existing relation contract is ambiguous.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from alembic import op
import sqlalchemy as sa


revision = "0038_patch_auth_password_reset_tokens"
down_revision = "0037_patch_evolution_signals_metrics"
branch_labels = None
depends_on = None

_TABLE = "password_reset_tokens"
_SYSTEM_SCHEMAS = {"information_schema", "pg_catalog"}
_REQUIRED_COLUMNS = {
    "id": (sa.String, False),
    "lead_id": (sa.String, False),
    "token_hash": (sa.String, False),
    "expires_at": (sa.BigInteger, False),
    "used_at": (sa.BigInteger, True),
    "created_at": (sa.BigInteger, False),
}
_REQUIRED_INDEXES = {
    "ix_password_reset_tokens_lead": (["lead_id"], False),
    "ix_password_reset_tokens_token_hash": (["token_hash"], False),
}


def _bind():
    return op.get_bind()


def _inspector() -> sa.Inspector:
    return sa.inspect(_bind())


def _dialect_name() -> str:
    return str(_bind().dialect.name)


def _target_schema() -> str | None:
    if _dialect_name() != "postgresql":
        return None
    value = _bind().execute(sa.text("SELECT current_schema()")).scalar_one_or_none()
    schema = str(value).strip() if value is not None else ""
    if not schema or schema in _SYSTEM_SCHEMAS:
        raise RuntimeError(
            "AUTH_RESET_001_SCHEMA_UNRESOLVED "
            "current_schema_missing_or_system=true"
        )
    return schema


def _visible_table_locations() -> list[str]:
    inspector = _inspector()
    locations: list[str] = []
    try:
        schemas = inspector.get_schema_names()
    except Exception as exc:
        raise RuntimeError(
            "AUTH_RESET_001_SCHEMA_INSPECTION_FAILED"
        ) from exc

    for schema in schemas:
        schema_name = str(schema)
        if schema_name in _SYSTEM_SCHEMAS or schema_name.startswith("pg_"):
            continue
        try:
            names = inspector.get_table_names(schema=schema_name)
        except Exception:
            continue
        if _TABLE in names:
            locations.append(schema_name)
    return sorted(set(locations))


def _table_exists(schema: str | None) -> bool:
    return _TABLE in _inspector().get_table_names(schema=schema)


def _column_contract(schema: str | None) -> Mapping[str, Mapping[str, object]]:
    return {
        str(column["name"]): column
        for column in _inspector().get_columns(_TABLE, schema=schema)
    }


def _type_matches(actual: object, expected: type[sa.types.TypeEngine]) -> bool:
    return isinstance(actual, expected)


def _index_contract(schema: str | None) -> Mapping[str, tuple[list[str], bool]]:
    result: dict[str, tuple[list[str], bool]] = {}
    for index in _inspector().get_indexes(_TABLE, schema=schema):
        name = index.get("name")
        if not name:
            continue
        columns = [str(value) for value in (index.get("column_names") or [])]
        result[str(name)] = (columns, bool(index.get("unique", False)))
    return result


def _validate_contract(schema: str | None) -> None:
    columns = _column_contract(schema)
    expected_names = set(_REQUIRED_COLUMNS)
    actual_names = set(columns)
    if actual_names != expected_names:
        raise RuntimeError(
            "AUTH_RESET_001_SCHEMA_MISMATCH "
            f"columns_expected={sorted(expected_names)} "
            f"columns_actual={sorted(actual_names)}"
        )

    type_mismatches: list[str] = []
    nullable_mismatches: list[str] = []
    for name, (expected_type, expected_nullable) in _REQUIRED_COLUMNS.items():
        actual = columns[name]
        if not _type_matches(actual.get("type"), expected_type):
            type_mismatches.append(name)
        if bool(actual.get("nullable", True)) != expected_nullable:
            nullable_mismatches.append(name)

    if type_mismatches or nullable_mismatches:
        raise RuntimeError(
            "AUTH_RESET_001_SCHEMA_MISMATCH "
            f"type_mismatches={sorted(type_mismatches)} "
            f"nullable_mismatches={sorted(nullable_mismatches)}"
        )

    primary_key = _inspector().get_pk_constraint(_TABLE, schema=schema) or {}
    constrained = list(primary_key.get("constrained_columns") or [])
    if constrained != ["id"]:
        raise RuntimeError(
            "AUTH_RESET_001_SCHEMA_MISMATCH "
            f"primary_key={constrained}"
        )

    indexes = _index_contract(schema)
    for name, expected in _REQUIRED_INDEXES.items():
        if indexes.get(name) != expected:
            raise RuntimeError(
                "AUTH_RESET_001_SCHEMA_MISMATCH "
                f"index={name} expected={expected} actual={indexes.get(name)}"
            )


def upgrade() -> None:
    target_schema = _target_schema()
    locations = _visible_table_locations()
    if locations:
        raise RuntimeError(
            "AUTH_RESET_001_TABLE_ALREADY_EXISTS "
            f"schemas={','.join(locations)} manual_baseline_review_required=true"
        )

    op.create_table(
        _TABLE,
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("lead_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
        sa.Column("used_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        schema=target_schema,
    )
    for index_name, (columns, unique) in _REQUIRED_INDEXES.items():
        op.create_index(
            index_name,
            _TABLE,
            columns,
            unique=unique,
            schema=target_schema,
        )

    _validate_contract(target_schema)


def downgrade() -> None:
    target_schema = _target_schema()
    if not _table_exists(target_schema):
        raise RuntimeError(
            "AUTH_RESET_001_DOWNGRADE_REFUSED table_missing=true"
        )

    _validate_contract(target_schema)
    op.drop_table(_TABLE, schema=target_schema)
