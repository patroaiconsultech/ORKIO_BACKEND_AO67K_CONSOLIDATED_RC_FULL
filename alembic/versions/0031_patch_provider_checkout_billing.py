"""PATCH v6.9.0 — provider checkout billing (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0031_patch_provider_checkout_billing"
down_revision = "0030_patch_billing_actuals_for_valuation"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS billing_checkouts (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            full_name VARCHAR,
            company VARCHAR,
            plan_code VARCHAR NOT NULL,
            plan_name VARCHAR NOT NULL,
            amount_brl NUMERIC(12,2) NOT NULL DEFAULT 0,
            currency VARCHAR NOT NULL DEFAULT 'BRL',
            status VARCHAR NOT NULL DEFAULT 'pending',
            access_source VARCHAR NOT NULL DEFAULT 'payment',
            provider VARCHAR NOT NULL DEFAULT 'asaas',
            provider_checkout_id VARCHAR,
            provider_payment_id VARCHAR,
            provider_url VARCHAR,
            callback_success_url VARCHAR,
            metadata TEXT,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL,
            confirmed_at BIGINT
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_billing_checkouts_org_email ON billing_checkouts (org_slug, email)"))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_billing_checkouts_provider_checkout ON billing_checkouts (provider, provider_checkout_id)"))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS billing_webhook_events (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR,
            provider VARCHAR NOT NULL DEFAULT 'asaas',
            provider_event_key VARCHAR NOT NULL,
            event_type VARCHAR NOT NULL,
            payload TEXT,
            processed BOOLEAN NOT NULL DEFAULT false,
            processed_at BIGINT,
            created_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_billing_webhooks_provider_event
        ON billing_webhook_events (provider, provider_event_key)
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS billing_entitlements (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            full_name VARCHAR,
            plan_code VARCHAR NOT NULL,
            plan_name VARCHAR NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'active',
            access_source VARCHAR NOT NULL DEFAULT 'payment',
            checkout_id VARCHAR,
            provider_customer_id VARCHAR,
            provider_subscription_id VARCHAR,
            starts_at BIGINT,
            expires_at BIGINT,
            last_payment_at BIGINT,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_billing_entitlements_org_email
        ON billing_entitlements (org_slug, email)
    """))


def downgrade():
    # Safety-first downgrade: do not drop billing data.
    pass
