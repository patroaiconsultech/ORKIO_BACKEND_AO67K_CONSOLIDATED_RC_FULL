from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from scripts.preflight_alembic_version import (
    _normalization_policy,
    apply_normalization,
    inspect_normalization_plan,
)


def test_normalization_policy_defaults_fail_closed() -> None:
    assert _normalization_policy({}) == (False, "default_false")
    assert _normalization_policy(
        {"ALLOW_ALEMBIC_VERSION_NORMALIZATION": "true"}
    ) == (True, "ALLOW_ALEMBIC_VERSION_NORMALIZATION")
    assert _normalization_policy(
        {"ALLOW_ALEMBIC_VERSION_NORMALIZATION": "false"}
    ) == (False, "ALLOW_ALEMBIC_VERSION_NORMALIZATION")


def test_invalid_normalization_policy_is_rejected() -> None:
    with pytest.raises(ValueError):
        _normalization_policy(
            {"ALLOW_ALEMBIC_VERSION_NORMALIZATION": "sometimes"}
        )


def test_readonly_inspection_does_not_create_missing_table(tmp_path: Path) -> None:
    database_path = tmp_path / "missing.sqlite"
    url = f"sqlite:///{database_path}"

    plan = inspect_normalization_plan(url)
    assert plan["database_access_mode"] == "readonly"
    assert plan["required_actions"] == ["create_version_table"]

    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            assert inspect(connection).has_table("alembic_version") is False
    finally:
        engine.dispose()


def test_explicit_application_creates_version_table(tmp_path: Path) -> None:
    database_path = tmp_path / "create.sqlite"
    url = f"sqlite:///{database_path}"

    plan = inspect_normalization_plan(url)
    apply_normalization(url, plan)
    verified = inspect_normalization_plan(url)

    assert verified["required_actions"] == []
    assert verified["table_exists"] is True
    assert verified["current_length"] == 128


def test_existing_wide_table_is_readonly_noop(tmp_path: Path) -> None:
    database_path = tmp_path / "wide.sqlite"
    url = f"sqlite:///{database_path}"
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE alembic_version "
                    "(version_num VARCHAR(128) NOT NULL)"
                )
            )
    finally:
        engine.dispose()

    plan = inspect_normalization_plan(url)
    assert plan["required_actions"] == []
    assert plan["invalid_schema"] is False


def test_missing_version_column_is_blocked(tmp_path: Path) -> None:
    database_path = tmp_path / "invalid.sqlite"
    url = f"sqlite:///{database_path}"
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE alembic_version (wrong_column VARCHAR(128))")
            )
    finally:
        engine.dispose()

    plan = inspect_normalization_plan(url)
    assert plan["invalid_schema"] is True
    assert plan["blocked_reason"] == "alembic_version_missing_version_num"
