"""Patch Irresistivel v1 runtime persistence (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0022_patch_irresistivel_v1_runtime_memory"
down_revision = "0021_patch_v340_thread_meta"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS runtime_memories (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            thread_id VARCHAR,
            memory_key VARCHAR NOT NULL,
            memory_value TEXT NOT NULL,
            source VARCHAR,
            confidence NUMERIC(4,2),
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_runtime_memories_org_user_key
        ON runtime_memories (org_slug, user_id, memory_key)
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS trial_states (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            trial_started_at BIGINT NOT NULL,
            last_seen_at BIGINT NOT NULL,
            activation_level VARCHAR,
            conversion_readiness VARCHAR,
            recommended_next_action VARCHAR,
            numerology_invited_at BIGINT
        )
    """))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_trial_states_org_user
        ON trial_states (org_slug, user_id)
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS numerology_profiles (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            preferred_name VARCHAR,
            full_name VARCHAR NOT NULL,
            birth_date VARCHAR NOT NULL,
            context VARCHAR,
            profile_json TEXT NOT NULL,
            consent BOOLEAN NOT NULL DEFAULT false,
            confirmed_at BIGINT,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_numerology_profiles_org_user
        ON numerology_profiles (org_slug, user_id)
    """))


def downgrade():
    # Safety-first downgrade: no table drops for runtime memory/trial data.
    pass
