"""Alembic migration environment for Orkio API.

AO68A BOOT NAMESPACE FIX
- The AO67K consolidated repository is checked out at /app in Railway.
- Runtime code imports modules as `app.*` and uses package-relative imports.
- When Alembic executes from /app, Python's default sys.path points at /app,
  so `import app.db` looks for /app/app/db.py and fails.
- We insert the parent directory of the project root into sys.path so /app can
  be resolved as the `app` namespace package.

This file intentionally keeps the app-package import contract:
    from app.db import Base
    from app import models
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool


# ---------------------------------------------------------------------------
# AO68A namespace bootstrap
# ---------------------------------------------------------------------------
# /app/alembic/env.py -> project_root=/app -> parent=/
# With "/" on sys.path, Python can import /app as the namespace package `app`.
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[1]
_PROJECT_PARENT = _PROJECT_ROOT.parent

_project_parent_str = str(_PROJECT_PARENT)
if _project_parent_str not in sys.path:
    sys.path.insert(0, _project_parent_str)


from app.db import Base  # noqa: E402
from app import models  # noqa: F401,E402 - import registers ORM models on Base.metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _clean_database_url(raw: str | None) -> str:
    """Normalize DATABASE_* values copied from Railway or local env."""

    if raw is None:
        return ""

    url = str(raw).strip().strip('"').strip("'")
    if not url:
        return ""

    # Defensive normalization for Railway copy/paste casing mistakes.
    url = url.replace("Postgres.railway.internal", "postgres.railway.internal")

    # SQLAlchemy prefers postgresql:// over postgres://.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    return url


def _runtime_database_url() -> str:
    """Resolve the DB URL from runtime env, preferring public URL for Alembic.

    In Railway runtime, DATABASE_URL usually points to the internal network.
    DATABASE_PUBLIC_URL / DATABASE_URL_PUBLIC are useful for external/diagnostic
    execution. The fallback order below preserves the previous contract.
    """

    return (
        _clean_database_url(os.getenv("DATABASE_PUBLIC_URL"))
        or _clean_database_url(os.getenv("DATABASE_URL_PUBLIC"))
        or _clean_database_url(os.getenv("DATABASE_URL"))
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
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
