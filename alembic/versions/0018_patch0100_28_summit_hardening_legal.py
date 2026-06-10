"""PATCH0100_28 — Summit Hardening + Legal Compliance (idempotent safe)

AO68J:
Replaces direct op.add_column/op.create_table calls with PostgreSQL idempotent DDL.
This prevents DuplicateColumn/DuplicateTable cascades during staging recovery.
"""
from alembic import op
import sqlalchemy as sa

revision = "0018"
down_revision = "0017_patch0100_27_1B_realtime_transcript_punct"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    bind.execute(sa.text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS signup_code_label VARCHAR,
        ADD COLUMN IF NOT EXISTS signup_source VARCHAR,
        ADD COLUMN IF NOT EXISTS usage_tier VARCHAR DEFAULT 'summit_standard',
        ADD COLUMN IF NOT EXISTS terms_accepted_at BIGINT,
        ADD COLUMN IF NOT EXISTS terms_version VARCHAR,
        ADD COLUMN IF NOT EXISTS marketing_consent BOOLEAN DEFAULT false
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS signup_codes (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            code_hash VARCHAR NOT NULL,
            label VARCHAR NOT NULL,
            source VARCHAR NOT NULL,
            expires_at BIGINT NOT NULL,
            max_uses INTEGER NOT NULL DEFAULT 500,
            used_count INTEGER NOT NULL DEFAULT 0,
            active BOOLEAN NOT NULL DEFAULT true,
            created_at BIGINT NOT NULL,
            created_by VARCHAR
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_signup_codes_org_slug ON signup_codes (org_slug)"))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            code_hash VARCHAR NOT NULL,
            expires_at BIGINT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            verified BOOLEAN NOT NULL DEFAULT false,
            created_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_otp_codes_user_id ON otp_codes (user_id)"))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            org_slug VARCHAR NOT NULL,
            login_at BIGINT NOT NULL,
            logout_at BIGINT,
            last_seen_at BIGINT NOT NULL,
            ended_reason VARCHAR,
            duration_seconds INTEGER,
            source_code_label VARCHAR,
            usage_tier VARCHAR,
            ip_address VARCHAR
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_user_sessions_user_id ON user_sessions (user_id)"))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_user_sessions_org_slug ON user_sessions (org_slug)"))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS usage_events (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            org_slug VARCHAR NOT NULL,
            event_type VARCHAR NOT NULL,
            tokens_used INTEGER,
            duration_seconds INTEGER,
            created_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_usage_events_user_id ON usage_events (user_id)"))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_usage_events_org_slug ON usage_events (org_slug)"))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS feature_flags (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            flag_key VARCHAR NOT NULL,
            flag_value VARCHAR NOT NULL DEFAULT 'true',
            updated_by VARCHAR,
            updated_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_feature_flags_org_slug ON feature_flags (org_slug)"))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_feature_flags_org_key
        ON feature_flags (org_slug, flag_key)
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS contact_requests (
            id VARCHAR PRIMARY KEY,
            full_name VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            whatsapp VARCHAR,
            subject VARCHAR NOT NULL,
            message TEXT NOT NULL,
            privacy_request_type VARCHAR,
            consent_terms BOOLEAN NOT NULL,
            consent_marketing BOOLEAN NOT NULL DEFAULT false,
            ip_address VARCHAR,
            user_agent VARCHAR,
            terms_version VARCHAR,
            status VARCHAR NOT NULL DEFAULT 'pending',
            retention_until BIGINT,
            created_at BIGINT NOT NULL
        )
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS marketing_consents (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR,
            contact_id VARCHAR,
            channel VARCHAR NOT NULL,
            opt_in_date BIGINT,
            opt_out_date BIGINT,
            ip VARCHAR,
            source VARCHAR,
            created_at BIGINT NOT NULL
        )
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS terms_acceptances (
            id VARCHAR PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            terms_version VARCHAR NOT NULL,
            accepted_at BIGINT NOT NULL,
            ip_address VARCHAR,
            user_agent VARCHAR
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_terms_acceptances_user_id ON terms_acceptances (user_id)"))


def downgrade():
    # Safety-first downgrade: do not drop legal/auth data in staging/prod.
    pass
