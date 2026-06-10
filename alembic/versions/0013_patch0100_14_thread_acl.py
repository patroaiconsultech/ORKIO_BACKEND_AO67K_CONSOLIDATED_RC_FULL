"""patch0100_14 thread ACL (multiusuários) - idempotent safe

Revision ID: 0013_patch0100_14_thread_acl
Revises: 0012_patch1008_leads
Create Date: 2026-02-18

AO68E_MIGRATION_CASCADE_GUARD:
- Safe if thread_members already exists.
- Safe if columns already exist.
- Safe if indexes already exist.
- Seed is idempotent.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy import text as sa_text

revision = "0013_patch0100_14_thread_acl"
down_revision = "0012_patch1008_leads"
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    try:
        return inspect(bind).has_table(table_name)
    except Exception:
        row = bind.execute(
            sa_text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = :table_name
                LIMIT 1
                """
            ),
            {"table_name": table_name},
        ).fetchone()
        return row is not None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    row = bind.execute(
        sa_text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
            LIMIT 1
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone()
    return row is not None


def _index_exists(bind, index_name: str) -> bool:
    row = bind.execute(
        sa_text(
            """
            SELECT 1
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND indexname = :index_name
            LIMIT 1
            """
        ),
        {"index_name": index_name},
    ).fetchone()
    return row is not None


def _constraint_exists(bind, constraint_name: str) -> bool:
    row = bind.execute(
        sa_text(
            """
            SELECT 1
            FROM information_schema.table_constraints
            WHERE constraint_schema = 'public'
              AND constraint_name = :constraint_name
            LIMIT 1
            """
        ),
        {"constraint_name": constraint_name},
    ).fetchone()
    return row is not None


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    if not _column_exists(bind, table_name, column.name):
        with op.batch_alter_table(table_name) as batch:
            batch.add_column(column)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    bind = op.get_bind()
    if not _index_exists(bind, index_name):
        op.create_index(index_name, table_name, columns)


def _ensure_thread_members_schema() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "thread_members"):
        op.create_table(
            "thread_members",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("org_slug", sa.String(), nullable=False),
            sa.Column("thread_id", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("role", sa.String(), nullable=False),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
            sa.UniqueConstraint("thread_id", "user_id", name="uq_thread_members_thread_user"),
            sa.CheckConstraint(
                "role IN ('owner','admin','member','viewer')",
                name="ck_thread_members_role",
            ),
        )
    else:
        _add_column_if_missing("thread_members", sa.Column("id", sa.String(), nullable=True))
        _add_column_if_missing("thread_members", sa.Column("org_slug", sa.String(), nullable=True))
        _add_column_if_missing("thread_members", sa.Column("thread_id", sa.String(), nullable=True))
        _add_column_if_missing("thread_members", sa.Column("user_id", sa.String(), nullable=True))
        _add_column_if_missing("thread_members", sa.Column("role", sa.String(), nullable=True))
        _add_column_if_missing("thread_members", sa.Column("created_at", sa.BigInteger(), nullable=True))

        if not _constraint_exists(bind, "uq_thread_members_thread_user"):
            try:
                op.create_unique_constraint(
                    "uq_thread_members_thread_user",
                    "thread_members",
                    ["thread_id", "user_id"],
                )
            except Exception as exc:
                import logging

                logging.getLogger("alembic").warning(
                    "THREAD_MEMBERS_UNIQUE_CONSTRAINT_SKIPPED: %s", str(exc)
                )

        if not _constraint_exists(bind, "ck_thread_members_role"):
            try:
                op.create_check_constraint(
                    "ck_thread_members_role",
                    "thread_members",
                    "role IN ('owner','admin','member','viewer')",
                )
            except Exception as exc:
                import logging

                logging.getLogger("alembic").warning(
                    "THREAD_MEMBERS_ROLE_CHECK_SKIPPED: %s", str(exc)
                )

    _create_index_if_missing("ix_thread_members_org_slug", "thread_members", ["org_slug"])
    _create_index_if_missing("ix_thread_members_thread_id", "thread_members", ["thread_id"])
    _create_index_if_missing("ix_thread_members_user_id", "thread_members", ["user_id"])


def _seed_existing_thread_owners() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "threads") or not _table_exists(bind, "messages"):
        return

    try:
        rows = bind.execute(
            sa_text(
                """
                SELECT
                    t.id AS thread_id,
                    t.org_slug,
                    (
                        SELECT m.user_id
                        FROM messages m
                        WHERE m.thread_id = t.id
                          AND m.user_id IS NOT NULL
                        ORDER BY m.created_at ASC
                        LIMIT 1
                    ) AS creator_id
                FROM threads t
                """
            )
        ).fetchall()

        import time
        import uuid

        now_ms = int(time.time() * 1000)

        for row in rows:
            thread_id = row[0]
            org_slug = row[1]
            creator_id = row[2]

            if not thread_id or not creator_id:
                continue

            existing = bind.execute(
                sa_text(
                    """
                    SELECT 1
                    FROM thread_members
                    WHERE thread_id = :thread_id
                      AND user_id = :user_id
                    LIMIT 1
                    """
                ),
                {"thread_id": thread_id, "user_id": creator_id},
            ).fetchone()

            if existing:
                continue

            bind.execute(
                sa_text(
                    """
                    INSERT INTO thread_members
                        (id, org_slug, thread_id, user_id, role, created_at)
                    VALUES
                        (:id, :org_slug, :thread_id, :user_id, 'owner', :created_at)
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "org_slug": org_slug or "public",
                    "thread_id": thread_id,
                    "user_id": creator_id,
                    "created_at": now_ms,
                },
            )
    except Exception as exc:
        import logging

        logging.getLogger("alembic").warning("THREAD_ACL_SEED_PARTIAL: %s", str(exc))


def upgrade() -> None:
    _ensure_thread_members_schema()
    _seed_existing_thread_owners()


def downgrade() -> None:
    bind = op.get_bind()

    if _index_exists(bind, "ix_thread_members_user_id"):
        op.drop_index("ix_thread_members_user_id", table_name="thread_members")
    if _index_exists(bind, "ix_thread_members_thread_id"):
        op.drop_index("ix_thread_members_thread_id", table_name="thread_members")
    if _index_exists(bind, "ix_thread_members_org_slug"):
        op.drop_index("ix_thread_members_org_slug", table_name="thread_members")

    if _table_exists(bind, "thread_members"):
        op.drop_table("thread_members")
