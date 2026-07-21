"""Readonly governed migration-plan preflight for container startup.

This script is the first database-aware step in the container boot sequence.
It performs inspection only: no CREATE, ALTER, INSERT, UPDATE, DELETE, Alembic
upgrade, or application migration is executed here.

Policy:
- Production requires an explicit ``ALLOW_AUTOMATIC_MIGRATIONS`` value.
- Outside production, an omitted value preserves the legacy ``true`` behavior
  and is reported as a compatibility default.
- Pending migrations block when automatic execution is disabled.
- Unknown database revisions and multiple code heads always block.
- A synchronized database continues regardless of the explicit true/false
  value, but production still requires the policy to be explicitly declared.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text


ROOT = Path(__file__).resolve().parents[1]
_TRUTHY = {"1", "true", "yes", "y", "on"}
_FALSY = {"0", "false", "no", "n", "off"}
_PRODUCTION_NAMES = {"prod", "production"}


def _clean_env_value(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip('"').strip("'")


def _environment_name(environ: Mapping[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    return (
        _clean_env_value(env.get("APP_ENV"))
        or _clean_env_value(env.get("ENVIRONMENT"))
        or _clean_env_value(env.get("RAILWAY_ENVIRONMENT_NAME"))
        or "unknown"
    ).lower()


def _environment_class(environ: Mapping[str, str] | None = None) -> str:
    return (
        "production"
        if _environment_name(environ) in _PRODUCTION_NAMES
        else "nonproduction"
    )


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


def _automatic_migration_policy(
    environ: Mapping[str, str] | None = None,
) -> tuple[bool, str]:
    env = os.environ if environ is None else environ
    raw_value = env.get("ALLOW_AUTOMATIC_MIGRATIONS")
    raw = _clean_env_value(raw_value)
    environment_class = _environment_class(env)

    if not raw:
        if environment_class == "production":
            return False, "production_policy_missing"
        return True, "nonproduction_legacy_default_true"

    normalized = raw.lower()
    if normalized in _TRUTHY:
        return True, "ALLOW_AUTOMATIC_MIGRATIONS"
    if normalized in _FALSY:
        return False, "ALLOW_AUTOMATIC_MIGRATIONS"
    raise ValueError(
        "ALLOW_AUTOMATIC_MIGRATIONS must be true/false, 1/0, yes/no, or on/off"
    )


def _automatic_migration_policy_explicit(
    environ: Mapping[str, str] | None = None,
) -> bool:
    env = os.environ if environ is None else environ
    return bool(_clean_env_value(env.get("ALLOW_AUTOMATIC_MIGRATIONS")))


def _automatic_migrations_allowed(
    environ: Mapping[str, str] | None = None,
) -> bool:
    allowed, _source = _automatic_migration_policy(environ)
    return allowed


def _code_inventory(root: Path = ROOT) -> tuple[tuple[str, ...], tuple[str, ...]]:
    config_path = root / "alembic.ini"
    script_path = root / "alembic"
    if not config_path.is_file():
        raise RuntimeError("alembic.ini not found")
    if not script_path.is_dir():
        raise RuntimeError("alembic script directory not found")

    config = Config(str(config_path))
    config.set_main_option("script_location", str(script_path))
    script = ScriptDirectory.from_config(config)
    heads = tuple(sorted(str(value) for value in script.get_heads()))
    known_revisions = tuple(
        sorted(
            {
                str(revision.revision)
                for revision in script.walk_revisions()
                if revision.revision
            }
        )
    )
    return heads, known_revisions


def _read_database_heads(connection) -> tuple[str, ...]:
    inspector = inspect(connection)
    if not inspector.has_table("alembic_version"):
        return ()
    result = connection.execute(
        text("SELECT version_num FROM alembic_version ORDER BY version_num")
    )
    return tuple(
        sorted(
            {
                str(value).strip()
                for value in result.scalars().all()
                if str(value or "").strip()
            }
        )
    )


def _database_heads(url: str) -> tuple[str, ...]:
    """Read current Alembic heads without mutating the database."""

    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            if connection.dialect.name == "postgresql":
                with connection.begin():
                    # Must be the first statement in this transaction.
                    connection.execute(text("SET TRANSACTION READ ONLY"))
                    return _read_database_heads(connection)
            return _read_database_heads(connection)
    finally:
        engine.dispose()


def build_migration_plan(
    *,
    current_heads: tuple[str, ...],
    target_heads: tuple[str, ...],
    known_revisions: tuple[str, ...] = (),
    automatic_allowed: bool,
    policy_source: str = "explicit_argument",
    policy_explicit: bool = True,
    environment_class: str = "nonproduction",
) -> dict[str, Any]:
    current = tuple(sorted(set(current_heads)))
    target = tuple(sorted(set(target_heads)))
    known = set(known_revisions)
    unknown_current = tuple(
        sorted(value for value in current if known and value not in known)
    )
    multiple_code_heads = len(target) != 1
    synchronized = current == target and not multiple_code_heads

    blocked_reason = None
    if multiple_code_heads:
        blocked_reason = "multiple_code_heads"
    elif unknown_current:
        blocked_reason = "unknown_database_revision"
    elif environment_class == "production" and not policy_explicit:
        blocked_reason = "automatic_migration_policy_not_explicit"
    elif not synchronized and not automatic_allowed:
        blocked_reason = "pending_migrations_automatic_execution_disabled"

    return {
        "database_access_mode": "readonly",
        "current_database_revisions": list(current),
        "target_code_heads": list(target),
        "code_head_count": len(target),
        "unknown_database_revisions": list(unknown_current),
        "pending_migrations": not synchronized,
        "migration_in_sync": synchronized,
        "automatic_migrations_allowed": bool(automatic_allowed),
        "automatic_migration_policy_explicit": bool(policy_explicit),
        "environment_class": environment_class,
        "policy_source": policy_source,
        "blocked": blocked_reason is not None,
        "blocked_reason": blocked_reason,
    }


def main() -> int:
    environment_class = _environment_class()
    allowed, policy_source = _automatic_migration_policy()
    policy_explicit = _automatic_migration_policy_explicit()
    current = _database_heads(_database_url())
    target, known = _code_inventory()
    plan = build_migration_plan(
        current_heads=current,
        target_heads=target,
        known_revisions=known,
        automatic_allowed=allowed,
        policy_source=policy_source,
        policy_explicit=policy_explicit,
        environment_class=environment_class,
    )

    print(
        "ORKIO_MIGRATION_PLAN "
        + json.dumps(plan, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    )

    if plan["blocked"]:
        print(
            "ORKIO_MIGRATION_PLAN_BLOCKED "
            f"reason={plan['blocked_reason']}",
            file=sys.stderr,
        )
        return 3

    print("ORKIO_MIGRATION_PLAN_OK access_mode=readonly")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            "ORKIO_MIGRATION_PLAN_FAILED "
            f"error_type={exc.__class__.__name__}",
            file=sys.stderr,
        )
        raise
