"""PATCH v3.3.1a — onboarding profile fields (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0020_patch_v331a_onboarding_profile"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS company VARCHAR,
        ADD COLUMN IF NOT EXISTS profile_role VARCHAR,
        ADD COLUMN IF NOT EXISTS user_type VARCHAR,
        ADD COLUMN IF NOT EXISTS intent VARCHAR,
        ADD COLUMN IF NOT EXISTS notes TEXT,
        ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT false
    """))
    bind.execute(sa.text("UPDATE users SET onboarding_completed = false WHERE onboarding_completed IS NULL"))


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS onboarding_completed,
        DROP COLUMN IF EXISTS notes,
        DROP COLUMN IF EXISTS intent,
        DROP COLUMN IF EXISTS user_type,
        DROP COLUMN IF EXISTS profile_role,
        DROP COLUMN IF EXISTS company
    """))
