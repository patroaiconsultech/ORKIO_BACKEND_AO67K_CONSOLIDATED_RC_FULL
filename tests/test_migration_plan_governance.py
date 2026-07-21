from __future__ import annotations

from pathlib import Path

import pytest

from scripts.preflight_migration_plan import (
    _automatic_migration_policy,
    _automatic_migration_policy_explicit,
    _automatic_migrations_allowed,
    _database_heads,
    build_migration_plan,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, True),
        ("true", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("off", False),
    ],
)
def test_automatic_migration_policy_parsing_nonproduction(
    raw: str | None,
    expected: bool,
) -> None:
    environ = {"APP_ENV": "staging"}
    if raw is not None:
        environ["ALLOW_AUTOMATIC_MIGRATIONS"] = raw
    assert _automatic_migrations_allowed(environ) is expected


def test_policy_source_is_explicit_or_nonproduction_legacy_default() -> None:
    assert _automatic_migration_policy({"APP_ENV": "staging"}) == (
        True,
        "nonproduction_legacy_default_true",
    )
    assert _automatic_migration_policy(
        {
            "APP_ENV": "staging",
            "ALLOW_AUTOMATIC_MIGRATIONS": "false",
        }
    ) == (False, "ALLOW_AUTOMATIC_MIGRATIONS")


def test_production_missing_policy_is_fail_closed() -> None:
    environ = {"APP_ENV": "production"}
    assert _automatic_migration_policy(environ) == (
        False,
        "production_policy_missing",
    )
    assert _automatic_migration_policy_explicit(environ) is False

    plan = build_migration_plan(
        current_heads=("002",),
        target_heads=("002",),
        known_revisions=("001", "002"),
        automatic_allowed=False,
        policy_source="production_policy_missing",
        policy_explicit=False,
        environment_class="production",
    )
    assert plan["migration_in_sync"] is True
    assert plan["blocked"] is True
    assert plan["blocked_reason"] == "automatic_migration_policy_not_explicit"


def test_production_explicit_false_allows_synchronized_database() -> None:
    plan = build_migration_plan(
        current_heads=("002",),
        target_heads=("002",),
        known_revisions=("001", "002"),
        automatic_allowed=False,
        policy_source="ALLOW_AUTOMATIC_MIGRATIONS",
        policy_explicit=True,
        environment_class="production",
    )
    assert plan["migration_in_sync"] is True
    assert plan["blocked"] is False


def test_invalid_automatic_migration_policy_is_rejected() -> None:
    with pytest.raises(ValueError):
        _automatic_migrations_allowed(
            {
                "APP_ENV": "staging",
                "ALLOW_AUTOMATIC_MIGRATIONS": "sometimes",
            }
        )


def test_migration_plan_blocks_pending_revisions_when_disabled() -> None:
    plan = build_migration_plan(
        current_heads=("001",),
        target_heads=("002",),
        known_revisions=("001", "002"),
        automatic_allowed=False,
    )
    assert plan["pending_migrations"] is True
    assert plan["blocked"] is True
    assert (
        plan["blocked_reason"]
        == "pending_migrations_automatic_execution_disabled"
    )


def test_migration_plan_allows_pending_revisions_when_enabled() -> None:
    plan = build_migration_plan(
        current_heads=("001",),
        target_heads=("002",),
        known_revisions=("001", "002"),
        automatic_allowed=True,
    )
    assert plan["pending_migrations"] is True
    assert plan["blocked"] is False


def test_migration_plan_detects_synchronized_revisions() -> None:
    plan = build_migration_plan(
        current_heads=("002",),
        target_heads=("002",),
        known_revisions=("001", "002"),
        automatic_allowed=False,
    )
    assert plan["migration_in_sync"] is True
    assert plan["blocked"] is False


def test_unknown_database_revision_is_always_blocked() -> None:
    plan = build_migration_plan(
        current_heads=("external_revision",),
        target_heads=("002",),
        known_revisions=("001", "002"),
        automatic_allowed=True,
    )
    assert plan["blocked"] is True
    assert plan["blocked_reason"] == "unknown_database_revision"


def test_multiple_code_heads_are_always_blocked() -> None:
    plan = build_migration_plan(
        current_heads=("002",),
        target_heads=("002", "feature_head"),
        known_revisions=("001", "002", "feature_head"),
        automatic_allowed=True,
    )
    assert plan["blocked"] is True
    assert plan["blocked_reason"] == "multiple_code_heads"


def test_database_head_inspection_does_not_create_version_table(tmp_path: Path) -> None:
    database_path = tmp_path / "readonly.sqlite"
    url = f"sqlite:///{database_path}"

    assert _database_heads(url) == ()

    from sqlalchemy import create_engine, inspect

    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            assert inspect(connection).has_table("alembic_version") is False
    finally:
        engine.dispose()


def test_dockerfile_runs_readonly_plan_before_normalization_and_upgrade() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    plan_index = dockerfile.index("python scripts/preflight_migration_plan.py")
    normalization_index = dockerfile.index(
        "python scripts/preflight_alembic_version.py"
    )
    upgrade_index = dockerfile.index("alembic upgrade head")
    assert plan_index < normalization_index < upgrade_index
