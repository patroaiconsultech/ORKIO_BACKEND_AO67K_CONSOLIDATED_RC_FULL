"""PATCH v3.4.0 — thread meta (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0021_patch_v340_thread_meta"
down_revision = "0020_patch_v331a_onboarding_profile"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE threads
        ADD COLUMN IF NOT EXISTS meta TEXT
    """))


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE threads
        DROP COLUMN IF EXISTS meta
    """))
