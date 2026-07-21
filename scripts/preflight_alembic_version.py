"""Controlled Alembic version-table normalization.

This script runs only after the readonly migration-plan gate. It first inspects
``alembic_version`` without mutation. DDL is executed only when normalization is
required and ``ALLOW_ALEMBIC_VERSION_NORMALIZATION=true`` is explicitly set.

The application uses revision identifiers longer than Alembic's historical
VARCHAR(32) default, so a controlled VARCHAR(128) table is retained for
compatibility. No application migration is applied by this script.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Mapping

from sqlalchemy import create_engine, inspect, text


_TARGET_LENGTH = 128
_TRUTHY = {"1", "true", "yes", "y", "on"}
_FALSY = {"0", "false", "no", "n", "off"}


def _clean_env_value(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip('"').strip("'")


def _database_url(environ: Mapping[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    url = (
        _clean_env_value(env.get("DATABASE_PUBLIC_URL"))
        or _clean_env_value(env.get("DATABASE_URL_PUBLIC"))
        or _clean_env_value(env.get("DATABASE_URL"))
    )

    if not url:
        raise RuntimeError(
            "DATABASE URL not found. Set DATABASE_PUBLIC_URL, "
            "DATABASE_URL_PUBLIC, or DATABASE_URL."
        )

    url = url.replace("Postgres.railway.internal", "postgres.railway.internal")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    return url


def _normalization_policy(
    environ: Mapping[str, str] | None = None,
) -> tuple[bool, str]:
    env = os.environ if environ is None else environ
    raw = _clean_env_value(env.get("ALLOW_ALEMBIC_VERSION_NORMALIZATION"))
    if not raw:
        return False, "default_false"
    normalized = raw.lower()
    if normalized in _TRUTHY:
        return True, "ALLOW_ALEMBIC_VERSION_NORMALIZATION"
    if normalized in _FALSY:
        return False, "ALLOW_ALEMBIC_VERSION_NORMALIZATION"
    raise ValueError(
        "ALLOW_ALEMBIC_VERSION_NORMALIZATION must be true/false, "
        "1/0, yes/no, or on/off"
    )


def _inspect_on_connection(connection) -> dict[str, Any]:
    inspector = inspect(connection)
    table_exists = inspector.has_table("alembic_version")
    if not table_exists:
        return {
            "database_access_mode": "readonly",
            "table_exists": False,
            "version_num_exists": False,
            "current_length": None,
            "target_length": _TARGET_LENGTH,
            "required_actions": ["create_version_table"],
            "invalid_schema": False,
            "blocked_reason": None,
        }

    columns = {
        str(column.get("name")): column
        for column in inspector.get_columns("alembic_version")
    }
    version_column = columns.get("version_num")
    if version_column is None:
        return {
            "database_access_mode": "readonly",
            "table_exists": True,
            "version_num_exists": False,
            "current_length": None,
            "target_length": _TARGET_LENGTH,
            "required_actions": [],
            "invalid_schema": True,
            "blocked_reason": "alembic_version_missing_version_num",
        }

    column_type = version_column.get("type")
    current_length = getattr(column_type, "length", None)
    required_actions: list[str] = []
    if current_length is not None and int(current_length) < _TARGET_LENGTH:
        required_actions.append("widen_version_num_to_varchar_128")

    return {
        "database_access_mode": "readonly",
        "table_exists": True,
        "version_num_exists": True,
        "current_length": int(current_length) if current_length is not None else None,
        "target_length": _TARGET_LENGTH,
        "required_actions": required_actions,
        "invalid_schema": False,
        "blocked_reason": None,
    }


def inspect_normalization_plan(url: str) -> dict[str, Any]:
    """Inspect the control table using a read-only PostgreSQL transaction."""

    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            if connection.dialect.name == "postgresql":
                with connection.begin():
                    connection.execute(text("SET TRANSACTION READ ONLY"))
                    return _inspect_on_connection(connection)
            return _inspect_on_connection(connection)
    finally:
        engine.dispose()


def apply_normalization(url: str, plan: Mapping[str, Any]) -> None:
    actions = tuple(str(value) for value in plan.get("required_actions", ()))
    if not actions:
        return

    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            dialect = connection.dialect.name
            if "create_version_table" in actions:
                connection.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS alembic_version (
                            version_num VARCHAR(128) NOT NULL
                        )
                        """
                    )
                )

            if "widen_version_num_to_varchar_128" in actions:
                if dialect != "postgresql":
                    raise RuntimeError(
                        "Alembic version-column widening is supported only "
                        "for PostgreSQL in controlled startup."
                    )
                connection.execute(
                    text(
                        """
                        ALTER TABLE alembic_version
                        ALTER COLUMN version_num TYPE VARCHAR(128)
                        """
                    )
                )
    finally:
        engine.dispose()


def main() -> int:
    url = _database_url()
    allowed, policy_source = _normalization_policy()
    plan = inspect_normalization_plan(url)
    plan["normalization_allowed"] = bool(allowed)
    plan["policy_source"] = policy_source

    print(
        "ORKIO_ALEMBIC_VERSION_PLAN "
        + json.dumps(plan, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    )

    if plan["invalid_schema"]:
        print(
            "ALEMBIC_VERSION_PREFLIGHT_BLOCKED "
            f"reason={plan['blocked_reason']}",
            file=sys.stderr,
        )
        return 4

    if plan["required_actions"] and not allowed:
        print(
            "ALEMBIC_VERSION_PREFLIGHT_BLOCKED "
            "reason=normalization_required_but_not_allowed",
            file=sys.stderr,
        )
        return 4

    if plan["required_actions"]:
        apply_normalization(url, plan)
        verified = inspect_normalization_plan(url)
        if verified["invalid_schema"] or verified["required_actions"]:
            print(
                "ALEMBIC_VERSION_PREFLIGHT_BLOCKED "
                "reason=normalization_verification_failed",
                file=sys.stderr,
            )
            return 4
        print(
            "ALEMBIC_VERSION_PREFLIGHT_OK "
            "mode=controlled_write actions="
            + ",".join(plan["required_actions"])
        )
        return 0

    print("ALEMBIC_VERSION_PREFLIGHT_OK mode=readonly_noop")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            "ALEMBIC_VERSION_PREFLIGHT_FAILED "
            f"error_type={exc.__class__.__name__}",
            file=sys.stderr,
        )
        raise
