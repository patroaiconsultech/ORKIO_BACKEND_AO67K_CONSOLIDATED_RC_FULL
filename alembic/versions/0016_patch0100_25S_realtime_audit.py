"""PATCH0100_25S — Realtime sessions + events (auditability for WebRTC voice)

Revision ID: 0016_patch0100_25S_realtime_audit
Revises: 0015_patch0100_23_composite_indexes
Create Date: 2026-02-26

AO68H idempotent-safe version.

Operational goal:
- Avoid DuplicateTable when realtime_sessions / realtime_events were already
  created by schema boot/reconcile or a previous partial migration attempt.
- Avoid Alembic op.create_table() transaction aborts on PostgreSQL.
- Keep migration explicit and safe without importing app runtime.
"""

from alembic import op


revision = "0016_patch0100_25S_realtime_audit"
down_revision = "0015_patch0100_23_composite_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tables first. CREATE TABLE IF NOT EXISTS prevents PostgreSQL transaction abort
    # when the table already exists.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS realtime_sessions (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            thread_id VARCHAR NOT NULL,
            agent_id VARCHAR,
            agent_name VARCHAR,
            user_id VARCHAR,
            user_name VARCHAR,
            model VARCHAR,
            voice VARCHAR,
            started_at BIGINT NOT NULL,
            ended_at BIGINT,
            meta TEXT
        );
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS realtime_events (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            session_id VARCHAR NOT NULL,
            thread_id VARCHAR NOT NULL,
            role VARCHAR NOT NULL,
            agent_id VARCHAR,
            agent_name VARCHAR,
            event_type VARCHAR NOT NULL,
            content TEXT,
            created_at BIGINT NOT NULL,
            meta TEXT
        );
        """
    )

    # Column reconciliation for partially-created tables.
    op.execute(
        """
        ALTER TABLE realtime_sessions
            ADD COLUMN IF NOT EXISTS org_slug VARCHAR,
            ADD COLUMN IF NOT EXISTS thread_id VARCHAR,
            ADD COLUMN IF NOT EXISTS agent_id VARCHAR,
            ADD COLUMN IF NOT EXISTS agent_name VARCHAR,
            ADD COLUMN IF NOT EXISTS user_id VARCHAR,
            ADD COLUMN IF NOT EXISTS user_name VARCHAR,
            ADD COLUMN IF NOT EXISTS model VARCHAR,
            ADD COLUMN IF NOT EXISTS voice VARCHAR,
            ADD COLUMN IF NOT EXISTS started_at BIGINT,
            ADD COLUMN IF NOT EXISTS ended_at BIGINT,
            ADD COLUMN IF NOT EXISTS meta TEXT;
        """
    )

    op.execute(
        """
        ALTER TABLE realtime_events
            ADD COLUMN IF NOT EXISTS org_slug VARCHAR,
            ADD COLUMN IF NOT EXISTS session_id VARCHAR,
            ADD COLUMN IF NOT EXISTS thread_id VARCHAR,
            ADD COLUMN IF NOT EXISTS role VARCHAR,
            ADD COLUMN IF NOT EXISTS agent_id VARCHAR,
            ADD COLUMN IF NOT EXISTS agent_name VARCHAR,
            ADD COLUMN IF NOT EXISTS event_type VARCHAR,
            ADD COLUMN IF NOT EXISTS content TEXT,
            ADD COLUMN IF NOT EXISTS created_at BIGINT,
            ADD COLUMN IF NOT EXISTS meta TEXT;
        """
    )

    # Primary keys: only try to add if a PK is missing. This is best-effort and
    # intentionally does not validate data uniqueness if the table was created
    # externally with inconsistent rows.
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conrelid = 'realtime_sessions'::regclass
                  AND contype = 'p'
            ) THEN
                ALTER TABLE realtime_sessions ADD CONSTRAINT realtime_sessions_pkey PRIMARY KEY (id);
            END IF;
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END $$;
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conrelid = 'realtime_events'::regclass
                  AND contype = 'p'
            ) THEN
                ALTER TABLE realtime_events ADD CONSTRAINT realtime_events_pkey PRIMARY KEY (id);
            END IF;
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END $$;
        """
    )

    # Indexes. Includes indexes equivalent to SQLAlchemy index=True plus the
    # composite indexes from the original migration.
    op.execute("CREATE INDEX IF NOT EXISTS ix_realtime_sessions_org_slug ON realtime_sessions (org_slug);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_realtime_sessions_thread_id ON realtime_sessions (thread_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rt_sessions_org_thread ON realtime_sessions (org_slug, thread_id);")

    op.execute("CREATE INDEX IF NOT EXISTS ix_realtime_events_org_slug ON realtime_events (org_slug);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_realtime_events_session_id ON realtime_events (session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_realtime_events_thread_id ON realtime_events (thread_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rt_events_org_session ON realtime_events (org_slug, session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_rt_events_org_thread ON realtime_events (org_slug, thread_id);")


def downgrade() -> None:
    # Conservative rollback: remove indexes created by this migration, but avoid
    # dropping realtime audit tables automatically because they may contain
    # operational audit data or may have been created by schema reconciliation.
    op.execute("DROP INDEX IF EXISTS ix_rt_events_org_thread;")
    op.execute("DROP INDEX IF EXISTS ix_rt_events_org_session;")
    op.execute("DROP INDEX IF EXISTS ix_realtime_events_thread_id;")
    op.execute("DROP INDEX IF EXISTS ix_realtime_events_session_id;")
    op.execute("DROP INDEX IF EXISTS ix_realtime_events_org_slug;")

    op.execute("DROP INDEX IF EXISTS ix_rt_sessions_org_thread;")
    op.execute("DROP INDEX IF EXISTS ix_realtime_sessions_thread_id;")
    op.execute("DROP INDEX IF EXISTS ix_realtime_sessions_org_slug;")
