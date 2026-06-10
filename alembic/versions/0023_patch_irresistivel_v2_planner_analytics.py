"""Patch Irresistivel v2 planner analytics (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0023_patch_irresistivel_v2_planner_analytics"
down_revision = "0022_patch_irresistivel_v1_runtime_memory"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS trial_events (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            thread_id VARCHAR,
            event_name VARCHAR NOT NULL,
            payload_json TEXT,
            created_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_trial_events_org_user_created
        ON trial_events (org_slug, user_id, created_at)
    """))


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("DROP INDEX IF EXISTS ix_trial_events_org_user_created"))
