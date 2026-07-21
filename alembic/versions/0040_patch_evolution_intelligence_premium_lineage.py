"""Add Evolution Intelligence premium lineage, immutable snapshots and target history.

Revision ID: 0040_patch_evolution_intelligence_premium_lineage
Revises: 0039_patch_evolution_intelligence_foundation
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0040_patch_evolution_intelligence_premium_lineage"
down_revision = "0039_patch_evolution_intelligence_foundation"
branch_labels = None
depends_on = None


_IMMUTABLE_TABLES = (
    "evolution_health_snapshots",
    "evolution_health_snapshot_provenance",
    "evolution_health_snapshot_events",
)


def _create_immutable_guards() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.execute(
            """
            CREATE OR REPLACE FUNCTION orkio_reject_immutable_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'ORKIO_IMMUTABLE_RECORD:%', TG_TABLE_NAME;
            END;
            $$ LANGUAGE plpgsql
            """
        )
        for table_name in _IMMUTABLE_TABLES:
            op.execute(
                f"""
                CREATE TRIGGER trg_{table_name}_immutable
                BEFORE UPDATE OR DELETE ON {table_name}
                FOR EACH ROW EXECUTE FUNCTION orkio_reject_immutable_mutation()
                """
            )
    elif dialect == "sqlite":
        for table_name in _IMMUTABLE_TABLES:
            op.execute(
                f"""
                CREATE TRIGGER trg_{table_name}_immutable_update
                BEFORE UPDATE ON {table_name}
                BEGIN
                    SELECT RAISE(ABORT, 'ORKIO_IMMUTABLE_RECORD:{table_name}');
                END
                """
            )
            op.execute(
                f"""
                CREATE TRIGGER trg_{table_name}_immutable_delete
                BEFORE DELETE ON {table_name}
                BEGIN
                    SELECT RAISE(ABORT, 'ORKIO_IMMUTABLE_RECORD:{table_name}');
                END
                """
            )


def _drop_immutable_guards() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        for table_name in _IMMUTABLE_TABLES:
            op.execute(
                f"DROP TRIGGER IF EXISTS trg_{table_name}_immutable ON {table_name}"
            )
        op.execute("DROP FUNCTION IF EXISTS orkio_reject_immutable_mutation()")
    elif dialect == "sqlite":
        for table_name in _IMMUTABLE_TABLES:
            op.execute(
                f"DROP TRIGGER IF EXISTS trg_{table_name}_immutable_update"
            )
            op.execute(
                f"DROP TRIGGER IF EXISTS trg_{table_name}_immutable_delete"
            )


def upgrade() -> None:
    op.create_table(
        "evolution_kpi_target_versions",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("target_id", sa.String(length=96), nullable=False),
        sa.Column("objective_id", sa.String(length=96), nullable=True),
        sa.Column("scope_key", sa.String(length=96), nullable=False),
        sa.Column("kpi_code", sa.String(length=128), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("warning_threshold", sa.Float(), nullable=False),
        sa.Column("critical_threshold", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("minimum_sample_size", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("proposal_enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "auto_apply_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("effective_from", sa.BigInteger(), nullable=False),
        sa.Column("effective_to", sa.BigInteger(), nullable=True),
        sa.Column("changed_by", sa.String(length=180), nullable=False),
        sa.Column("change_reason", sa.String(length=300), nullable=False),
        sa.Column("approval_id", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "version >= 1",
            name="ck_evolution_target_version_positive",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_evolution_target_version_range",
        ),
        sa.CheckConstraint(
            "auto_apply_enabled = FALSE",
            name="ck_evolution_target_version_auto_apply_disabled",
        ),
        sa.CheckConstraint(
            "(objective_id IS NULL AND scope_key = '__global__') "
            "OR (objective_id IS NOT NULL AND scope_key = objective_id)",
            name="ck_evolution_target_version_scope",
        ),
        sa.ForeignKeyConstraint(
            ["target_id"],
            ["evolution_kpi_targets.id"],
            name="fk_evolution_target_version_target",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["objective_id", "org_slug"],
            ["evolution_objectives.id", "evolution_objectives.org_slug"],
            name="fk_evolution_target_version_objective_org",
        ),
        sa.UniqueConstraint(
            "org_slug",
            "target_id",
            "version",
            name="ux_evolution_target_version_identity",
        ),
    )
    op.create_index(
        "ix_evolution_target_versions_org_scope_kpi",
        "evolution_kpi_target_versions",
        ["org_slug", "scope_key", "kpi_code", "version"],
    )
    op.create_index(
        "ix_evolution_target_versions_org_effective",
        "evolution_kpi_target_versions",
        ["org_slug", "effective_from", "effective_to"],
    )

    op.create_table(
        "evolution_health_snapshot_provenance",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("snapshot_id", sa.String(length=96), nullable=False),
        sa.Column("collector_version", sa.String(length=160), nullable=False),
        sa.Column("source_version", sa.String(length=160), nullable=False),
        sa.Column("release_id", sa.String(length=160), nullable=True),
        sa.Column("commit_sha", sa.String(length=64), nullable=True),
        sa.Column("deployment_id", sa.String(length=160), nullable=True),
        sa.Column("window_start", sa.BigInteger(), nullable=False),
        sa.Column("window_end", sa.BigInteger(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("provenance_json", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "sample_size >= 0",
            name="ck_evolution_snapshot_provenance_sample_size",
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_evolution_snapshot_provenance_confidence",
        ),
        sa.CheckConstraint(
            "window_end >= window_start",
            name="ck_evolution_snapshot_provenance_window",
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["evolution_health_snapshots.id"],
            name="fk_evolution_snapshot_provenance_snapshot",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "snapshot_id",
            name="ux_evolution_snapshot_provenance_snapshot",
        ),
    )
    op.create_index(
        "ix_evolution_snapshot_provenance_org_created",
        "evolution_health_snapshot_provenance",
        ["org_slug", "created_at"],
    )

    op.create_table(
        "evolution_health_snapshot_events",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("snapshot_id", sa.String(length=96), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("approval_id", sa.String(length=160), nullable=False),
        sa.Column("actor_ref", sa.String(length=180), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "event_type IN ('invalidated')",
            name="ck_evolution_snapshot_event_type",
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["evolution_health_snapshots.id"],
            name="fk_evolution_snapshot_event_snapshot",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "snapshot_id",
            "event_type",
            name="ux_evolution_snapshot_event_once",
        ),
    )
    op.create_index(
        "ix_evolution_snapshot_events_org_snapshot",
        "evolution_health_snapshot_events",
        ["org_slug", "snapshot_id", "created_at"],
    )

    _create_immutable_guards()


def downgrade() -> None:
    _drop_immutable_guards()

    op.drop_index(
        "ix_evolution_snapshot_events_org_snapshot",
        table_name="evolution_health_snapshot_events",
    )
    op.drop_table("evolution_health_snapshot_events")

    op.drop_index(
        "ix_evolution_snapshot_provenance_org_created",
        table_name="evolution_health_snapshot_provenance",
    )
    op.drop_table("evolution_health_snapshot_provenance")

    op.drop_index(
        "ix_evolution_target_versions_org_effective",
        table_name="evolution_kpi_target_versions",
    )
    op.drop_index(
        "ix_evolution_target_versions_org_scope_kpi",
        table_name="evolution_kpi_target_versions",
    )
    op.drop_table("evolution_kpi_target_versions")
