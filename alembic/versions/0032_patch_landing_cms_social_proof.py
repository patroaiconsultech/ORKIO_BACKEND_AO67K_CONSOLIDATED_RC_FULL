"""PATCH v7.1.0 — landing cms and social proof (idempotent safe)"""
from alembic import op
import sqlalchemy as sa

revision = "0032_patch_landing_cms_social_proof"
down_revision = "0031_patch_provider_checkout_billing"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS social_proof_items (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            page_key VARCHAR NOT NULL DEFAULT 'landing_home',
            kind VARCHAR NOT NULL DEFAULT 'testimonial',
            status VARCHAR NOT NULL DEFAULT 'draft',
            featured BOOLEAN NOT NULL DEFAULT false,
            title VARCHAR,
            subtitle VARCHAR,
            summary TEXT,
            quote TEXT,
            person_name VARCHAR,
            person_role VARCHAR,
            company_name VARCHAR,
            company_site VARCHAR,
            image_url VARCHAR,
            logo_url VARCHAR,
            href VARCHAR,
            region VARCHAR,
            market_segment VARCHAR,
            metrics_json TEXT,
            tags_json TEXT,
            proof_code VARCHAR,
            sort_order INTEGER NOT NULL DEFAULT 100,
            starts_at BIGINT,
            ends_at BIGINT,
            created_by VARCHAR,
            updated_by VARCHAR,
            published_at BIGINT,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_social_proof_items_org_kind_status ON social_proof_items (org_slug, kind, status)"))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_social_proof_items_org_sort ON social_proof_items (org_slug, sort_order, created_at)"))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_social_proof_items_org_featured ON social_proof_items (org_slug, featured, created_at)"))

    bind.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS landing_content_blocks (
            id VARCHAR PRIMARY KEY,
            org_slug VARCHAR NOT NULL,
            page_key VARCHAR NOT NULL DEFAULT 'landing_home',
            block_key VARCHAR NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'draft',
            title VARCHAR,
            subtitle VARCHAR,
            body TEXT,
            cta_label VARCHAR,
            cta_href VARCHAR,
            payload_json TEXT,
            sort_order INTEGER NOT NULL DEFAULT 100,
            starts_at BIGINT,
            ends_at BIGINT,
            created_by VARCHAR,
            updated_by VARCHAR,
            published_at BIGINT,
            created_at BIGINT NOT NULL,
            updated_at BIGINT NOT NULL
        )
    """))
    bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_landing_content_blocks_org_page_sort ON landing_content_blocks (org_slug, page_key, sort_order)"))
    bind.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_landing_content_blocks_org_page_key
        ON landing_content_blocks (org_slug, page_key, block_key)
    """))


def downgrade():
    # Safety-first downgrade: do not drop CMS/social proof data.
    pass
