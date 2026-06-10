"""Alembic migration environment for Orkio API.

AO68F CASCADE ROOT GUARD
========================

Operational goal:
- Run Alembic migrations without importing the runtime application package.
- Avoid triggering boot-time schema reconcilers before Alembic.
- Keep /app importability for migrations that explicitly need it, but do not
  import app.db, app.models, app.main, services, runtime, or other side-effect
  modules from env.py.

Why this matters:
- The previous env.py imported `from app import models`.
- In the AO67K consolidated runtime, importing runtime/model modules can trigger
  boot schema reconciliation before Alembic runs.
- That creates tables/columns first, then migrations try to create them again,
  causing DuplicateTable/DuplicateColumn cascades.

This env.py is migration-only and intentionally sets target_metadata=None.
Alembic upgrade does not require ORM metadata to apply explicit migration files.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool


# ---------------------------------------------------------------------------
# Namespace bootstrap without importing the runtime app.
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[1]      # /app
_PROJECT_PARENT = _PROJECT_ROOT.parent     # /

for _path in (str(_PROJECT_PARENT), str(_PROJECT_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Deliberately do not import app.db/Base/models here.
# Explicit migration scripts are the source of truth for `alembic upgrade`.
target_metadata = None


def _clean_database_url(raw: str | None) -> str:
    """Normalize DATABASE_* values copied from Railway or local env."""

    if raw is None:
        return ""

    url = str(raw).strip().strip('"').strip("'")
    if not url:
        return ""

    url = url.replace("Postgres.railway.internal", "postgres.railway.internal")

    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    return url


def _runtime_database_url() -> str:
    """Resolve DB URL from runtime env.

    Prefer DATABASE_URL inside Railway. Keep public aliases as fallback for
    local/diagnostic execution.
    """

    return (
        _clean_database_url(os.getenv("DATABASE_URL"))
        or _clean_database_url(os.getenv("DATABASE_PUBLIC_URL"))
        or _clean_database_url(os.getenv("DATABASE_URL_PUBLIC"))
    )


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = _runtime_database_url() or config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        transaction_per_migration=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    runtime_url = _runtime_database_url()
    section = config.get_section(config.config_ini_section, {})

    if runtime_url:
        section = dict(section)
        section["sqlalchemy.url"] = runtime_url

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            transaction_per_migration=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
