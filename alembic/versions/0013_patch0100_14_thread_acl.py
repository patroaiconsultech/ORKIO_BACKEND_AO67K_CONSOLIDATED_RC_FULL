"""patch0100_14 thread ACL (multiusuários) - AO68F transaction-safe idempotent guard.

Revision ID: 0013_patch0100_14_thread_acl
Revises: 0012_patch1008_leads
Create Date: 2026-02-18

AO68F fixes:
- Uses PostgreSQL IF NOT EXISTS / DO blocks instead of failing Alembic ops.
- Avoids catching DBAPI errors in Python after a failed statement, because in
  PostgreSQL that leaves the whole transaction aborted.
- Keeps the migration safe when schema boot/reconcile already created
  thread_members or its constraints.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0013_patch0100_14_thread_acl"
down_revision = "0012_patch1008_leads"
branch_labels = None
depends_on = None


def _execute(sql: str) -> None:
    op.execute(sa.text(sql))


def upgrade() -> None:
    # 1) Base table. IF NOT EXISTS prevents DuplicateTable.
    _execute(
        """
        CREATE TABLE IF NOT EXISTS thread_members (
            id VARCHAR NOT NULL,
            org_slug VARCHAR NOT NULL,
            thread_id VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            role VARCHAR NOT NULL,
            created_at BIGINT NOT NULL,
            PRIMARY KEY (id)
        )
        """
    )

    # 2) Column reconciliation for partially existing tables.
    # Existing NOT NULL constraints are preserved. Missing columns are added as
    # nullable to avoid failing on already populated tables.
    _execute("ALTER TABLE thread_members ADD COLUMN IF NOT EXISTS id VARCHAR")
    _execute("ALTER TABLE thread_members ADD COLUMN IF NOT EXISTS org_slug VARCHAR")
    _execute("ALTER TABLE thread_members ADD COLUMN IF NOT EXISTS thread_id VARCHAR")
    _execute("ALTER TABLE thread_members ADD COLUMN IF NOT EXISTS user_id VARCHAR")
    _execute("ALTER TABLE thread_members ADD COLUMN IF NOT EXISTS role VARCHAR")
    _execute("ALTER TABLE thread_members ADD COLUMN IF NOT EXISTS created_at BIGINT")

    # 3) Index/constraint-safe guards.
    # A UNIQUE CONSTRAINT normally creates an index with the same name. Using a
    # unique index here is safer across partially reconciled schemas.
    _execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_thread_members_thread_user
        ON thread_members (thread_id, user_id)
        """
    )
    _execute(
        """
        CREATE INDEX IF NOT EXISTS ix_thread_members_org_slug
        ON thread_members (org_slug)
        """
    )
    _execute(
        """
        CREATE INDEX IF NOT EXISTS ix_thread_members_thread_id
        ON thread_members (thread_id)
        """
    )
    _execute(
        """
        CREATE INDEX IF NOT EXISTS ix_thread_members_user_id
        ON thread_members (user_id)
        """
    )

    # Check constraints do not support IF NOT EXISTS in ALTER TABLE.
    # The DO block catches duplicate_object inside PostgreSQL, preserving the
    # outer Alembic transaction.
    _execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'ck_thread_members_role'
                  AND conrelid = 'thread_members'::regclass
            ) THEN
                ALTER TABLE thread_members
                ADD CONSTRAINT ck_thread_members_role
                CHECK (role IN ('owner','admin','member','viewer'));
            END IF;
        EXCEPTION
            WHEN duplicate_object THEN
                RAISE WARNING 'THREAD_MEMBERS_ROLE_CHECK_ALREADY_EXISTS';
            WHEN undefined_table THEN
                RAISE WARNING 'THREAD_MEMBERS_ROLE_CHECK_SKIPPED_TABLE_MISSING';
            WHEN others THEN
                RAISE WARNING 'THREAD_MEMBERS_ROLE_CHECK_SKIPPED: %', SQLERRM;
        END $$;
        """
    )

    # 4) Best-effort seed inside a PostgreSQL exception block.
    # Any failure is handled inside the database block, so it does not poison
    # the Alembic transaction.
    _execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'threads'
            )
            AND EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'messages'
            ) THEN
                INSERT INTO thread_members (
                    id,
                    org_slug,
                    thread_id,
                    user_id,
                    role,
                    created_at
                )
                SELECT
                    CONCAT('tm_', md5(t.id::text || ':' || src.creator_id::text)) AS id,
                    COALESCE(t.org_slug, 'public') AS org_slug,
                    t.id AS thread_id,
                    src.creator_id AS user_id,
                    'owner' AS role,
                    FLOOR(EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT AS created_at
                FROM threads t
                CROSS JOIN LATERAL (
                    SELECT m.user_id AS creator_id
                    FROM messages m
                    WHERE m.thread_id = t.id
                      AND m.user_id IS NOT NULL
                    ORDER BY m.created_at ASC NULLS LAST
                    LIMIT 1
                ) src
                WHERE src.creator_id IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM thread_members tm
                      WHERE tm.thread_id = t.id
                        AND tm.user_id = src.creator_id
                  )
                ON CONFLICT DO NOTHING;
            END IF;
        EXCEPTION
            WHEN others THEN
                RAISE WARNING 'THREAD_ACL_SEED_SKIPPED: %', SQLERRM;
        END $$;
        """
    )


def downgrade() -> None:
    # Conservative downgrade: do not drop ACL data automatically.
    # If rollback is required, use an explicit manual rollback plan.
    pass
