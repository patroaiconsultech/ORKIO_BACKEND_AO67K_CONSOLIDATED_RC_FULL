"""PATCH0100_28.3 — Idempotency keys for chat + realtime batch (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        ALTER TABLE messages
        ADD COLUMN IF NOT EXISTS client_message_id VARCHAR
    """))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_messages_org_thread_client_msg
        ON messages (org_slug, thread_id, client_message_id)
    """))

    bind.execute(sa.text("""
        ALTER TABLE realtime_events
        ADD COLUMN IF NOT EXISTS client_event_id VARCHAR
    """))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_realtime_events_org_sess_client_eid
        ON realtime_events (org_slug, session_id, client_event_id)
    """))


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("DROP INDEX IF EXISTS ux_realtime_events_org_sess_client_eid"))
    bind.execute(sa.text("DROP INDEX IF EXISTS ux_messages_org_thread_client_msg"))
    bind.execute(sa.text("ALTER TABLE realtime_events DROP COLUMN IF EXISTS client_event_id"))
    bind.execute(sa.text("ALTER TABLE messages DROP COLUMN IF EXISTS client_message_id"))
