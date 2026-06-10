"""patch0100_14 costs USD enterprise-grade (immutable at persist time) - idempotent safe

Revision ID: 0014_patch0100_14_costs_usd_persisted
Revises: 0013_patch0100_14_thread_acl
Create Date: 2026-02-18

AO68G notes:
- This migration must not use sa.Column(..., None), because that generates
  SQLAlchemy NullType and crashes before SQL reaches PostgreSQL.
- Use PostgreSQL-native DDL with IF NOT EXISTS to avoid DuplicateColumn.
- Keep all operations idempotent and transaction-safe.
"""

from alembic import op
from sqlalchemy import text as sa_text


revision = "0014_patch0100_14_costs_usd_persisted"
down_revision = "0013_patch0100_14_thread_acl"
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        sa_text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = current_schema()
              AND table_name = :table_name
            LIMIT 1
            """
        ),
        {"table_name": table_name},
    ).fetchone()
    return row is not None


def upgrade() -> None:
    conn = op.get_bind()

    # Defensive guard. In the intended chain, cost_events is created earlier.
    # If it is not present, do not create a partial incompatible table here.
    if not _table_exists(conn, "cost_events"):
        return

    # PostgreSQL-native idempotent DDL. Avoid Alembic op.add_column with a
    # dynamic/None type, because that emits NullType and fails at compile time.
    conn.execute(
        sa_text(
            """
            ALTER TABLE cost_events
              ADD COLUMN IF NOT EXISTS input_cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0,
              ADD COLUMN IF NOT EXISTS output_cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0,
              ADD COLUMN IF NOT EXISTS total_cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0,
              ADD COLUMN IF NOT EXISTS pricing_version VARCHAR(64) NOT NULL DEFAULT '2026-02-18',
              ADD COLUMN IF NOT EXISTS pricing_snapshot TEXT
            """
        )
    )

    conn.execute(
        sa_text(
            """
            CREATE INDEX IF NOT EXISTS ix_cost_events_org_created
            ON cost_events (org_slug, created_at)
            """
        )
    )

    # Best-effort backfill. Guard each source column because consolidated DBs
    # may have partial historical schemas.
    conn.execute(
        sa_text(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'cost_events'
                  AND column_name = 'cost_usd'
              ) THEN
                UPDATE cost_events
                   SET total_cost_usd = COALESCE(NULLIF(total_cost_usd, 0), cost_usd),
                       input_cost_usd = COALESCE(input_cost_usd, 0),
                       output_cost_usd = CASE
                         WHEN COALESCE(output_cost_usd, 0) = 0
                         THEN COALESCE(cost_usd, 0)
                         ELSE output_cost_usd
                       END
                 WHERE COALESCE(total_cost_usd, 0) = 0
                   AND COALESCE(cost_usd, 0) > 0;
              END IF;
            END $$;
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa_text("DROP INDEX IF EXISTS ix_cost_events_org_created"))

    if _table_exists(conn, "cost_events"):
        conn.execute(
            sa_text(
                """
                ALTER TABLE cost_events
                  DROP COLUMN IF EXISTS pricing_snapshot,
                  DROP COLUMN IF EXISTS pricing_version,
                  DROP COLUMN IF EXISTS total_cost_usd,
                  DROP COLUMN IF EXISTS output_cost_usd,
                  DROP COLUMN IF EXISTS input_cost_usd
                """
            )
        )
