"""PATCH0100_27.1B — Add transcript_punct to realtime_events

Revision ID: 0017_patch0100_27_1B_realtime_transcript_punct
Revises: 0016_patch0100_25S_realtime_audit
Create Date: 2026-02-28

AO68I — idempotent-safe migration.

Why:
- Staging already contains realtime_events.transcript_punct.
- The original migration used op.add_column(...), which fails with DuplicateColumn.
- This version uses PostgreSQL ADD COLUMN IF NOT EXISTS.

Operational rule:
- Do not import app/runtime/models here.
- Keep this migration DDL-only and reversible.
"""

from alembic import op


revision = "0017_patch0100_27_1B_realtime_transcript_punct"
down_revision = "0016_patch0100_25S_realtime_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add transcript_punct if it is not already present."""
    op.execute(
        """
        ALTER TABLE realtime_events
        ADD COLUMN IF NOT EXISTS transcript_punct TEXT;
        """
    )


def downgrade() -> None:
    """Drop transcript_punct only if it exists."""
    op.execute(
        """
        ALTER TABLE realtime_events
        DROP COLUMN IF EXISTS transcript_punct;
        """
    )
