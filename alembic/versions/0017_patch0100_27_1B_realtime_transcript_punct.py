"""PATCH0100_27.1B — Add transcript_punct to realtime_events (idempotent safe)

AO68J:
This migration is additive and safe for databases where realtime_events already
received transcript_punct through a previous boot reconcile or failed migration.
"""
from alembic import op
import sqlalchemy as sa

revision = "0017_patch0100_27_1B_realtime_transcript_punct"
down_revision = "0016_patch0100_25S_realtime_audit"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE realtime_events
        ADD COLUMN IF NOT EXISTS transcript_punct TEXT
    """))


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE realtime_events
        DROP COLUMN IF EXISTS transcript_punct
    """))
