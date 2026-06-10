"""Patch Irresistivel v3 runtime signal hardening (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0024_patch_irresistivel_v3_runtime_signal_hardening"
down_revision = "0023_patch_irresistivel_v2_planner_analytics"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE trial_states
        ADD COLUMN IF NOT EXISTS last_activation_score INTEGER
    """))


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE trial_states
        DROP COLUMN IF EXISTS last_activation_score
    """))
