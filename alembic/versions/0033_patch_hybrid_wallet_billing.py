"""PATCH v7.2.0 — hybrid wallet billing (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0033_patch_hybrid_wallet_billing"
down_revision = "0032_patch_landing_cms_social_proof"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS billing_wallets (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            user_id VARCHAR,
            email VARCHAR NOT NULL,
            full_name VARCHAR,
            currency VARCHAR NOT NULL DEFAULT 'USD',
            balance_usd NUMERIC(12,4) NOT NULL DEFAULT 0,
            lifetime_credited_usd NUMERIC(12,4) NOT NULL DEFAULT 0,
            lifetime_debited_usd NUMERIC(12,4) NOT NULL DEFAULT 0,
            auto_recharge_enabled BOOLEAN NOT NULL DEFAULT false,
            auto_recharge_pack_code VARCHAR,
            auto_recharge_threshold_usd NUMERIC(12,4),
            low_balance_threshold_usd NUMERIC(12,4) DEFAULT 3,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_billing_wallets_org_email
        ON billing_wallets (org_slug, email)
    """))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS billing_wallet_ledger (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            wallet_id VARCHAR NOT NULL,
            user_id VARCHAR,
            email VARCHAR NOT NULL,
            direction VARCHAR NOT NULL DEFAULT 'credit',
            source VARCHAR NOT NULL DEFAULT 'manual',
            action_key VARCHAR,
            quantity NUMERIC(12,4),
            unit_price_usd NUMERIC(12,4),
            amount_usd NUMERIC(12,4) NOT NULL DEFAULT 0,
            balance_after_usd NUMERIC(12,4) NOT NULL DEFAULT 0,
            currency VARCHAR NOT NULL DEFAULT 'USD',
            provider VARCHAR,
            external_ref VARCHAR,
            related_checkout_id VARCHAR,
            related_tx_id VARCHAR,
            metadata TEXT,
            created_by VARCHAR,
            created_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_billing_wallet_ledger_wallet_created ON billing_wallet_ledger (wallet_id, created_at)"))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_billing_wallet_ledger_org_email_created ON billing_wallet_ledger (org_slug, email, created_at)"))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_billing_wallet_ledger_external_ref ON billing_wallet_ledger (org_slug, external_ref)"))


def downgrade():
    # Safety-first downgrade: do not drop wallet/billing data.
    pass
