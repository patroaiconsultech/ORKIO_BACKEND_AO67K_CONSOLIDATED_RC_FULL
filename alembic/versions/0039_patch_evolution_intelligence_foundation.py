"""Add Evolution Intelligence Foundation objectives, targets and health snapshots.

Revision ID: 0039_patch_evolution_intelligence_foundation
Revises: 0038_patch_auth_password_reset_tokens
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0039_patch_evolution_intelligence_foundation"
down_revision = "0038_patch_auth_password_reset_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evolution_objectives",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="draft"),
        sa.Column("starts_at", sa.BigInteger(), nullable=True),
        sa.Column("ends_at", sa.BigInteger(), nullable=True),
        sa.Column("owner_ref", sa.String(length=180), nullable=False),
        sa.Column("success_definition", sa.Text(), nullable=False),
        sa.Column(
            "proposal_policy",
            sa.String(length=32),
            nullable=False,
            server_default="proposal_only",
        ),
        sa.Column(
            "human_approval_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(length=180), nullable=False),
        sa.Column("updated_by", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "priority >= 0 AND priority <= 100",
            name="ck_evolution_objective_priority",
        ),
        sa.CheckConstraint(
            "status IN ('draft','active','paused','completed')",
            name="ck_evolution_objective_status",
        ),
        sa.CheckConstraint(
            "proposal_policy = 'proposal_only'",
            name="ck_evolution_objective_proposal_only",
        ),
        sa.CheckConstraint(
            "human_approval_required = TRUE",
            name="ck_evolution_objective_human_approval",
        ),
        sa.CheckConstraint(
            "ends_at IS NULL OR starts_at IS NULL OR ends_at > starts_at",
            name="ck_evolution_objective_date_range",
        ),
        sa.UniqueConstraint(
            "id",
            "org_slug",
            name="ux_evolution_objective_id_org",
        ),
        sa.UniqueConstraint(
            "org_slug",
            "name",
            name="ux_evolution_objective_org_name",
        ),
    )
    op.create_index(
        "ix_evolution_objectives_org_status_priority",
        "evolution_objectives",
        ["org_slug", "status", "priority"],
    )
    op.create_index(
        "ix_evolution_objectives_org_updated",
        "evolution_objectives",
        ["org_slug", "updated_at"],
    )

    op.create_table(
        "evolution_kpi_targets",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("objective_id", sa.String(length=96), nullable=True),
        sa.Column(
            "scope_key",
            sa.String(length=96),
            nullable=False,
            server_default="__global__",
        ),
        sa.Column("kpi_code", sa.String(length=128), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("warning_threshold", sa.Float(), nullable=False),
        sa.Column("critical_threshold", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column(
            "minimum_sample_size",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "proposal_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "auto_apply_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("starts_at", sa.BigInteger(), nullable=True),
        sa.Column("ends_at", sa.BigInteger(), nullable=True),
        sa.Column("created_by", sa.String(length=180), nullable=False),
        sa.Column("updated_by", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "target_value >= 0 AND target_value <= 100",
            name="ck_evolution_kpi_target_value",
        ),
        sa.CheckConstraint(
            "critical_threshold >= 0 AND critical_threshold <= warning_threshold",
            name="ck_evolution_kpi_critical_threshold",
        ),
        sa.CheckConstraint(
            "warning_threshold <= target_value",
            name="ck_evolution_kpi_warning_threshold",
        ),
        sa.CheckConstraint(
            "weight > 0 AND weight <= 1",
            name="ck_evolution_kpi_weight",
        ),
        sa.CheckConstraint(
            "minimum_sample_size >= 0",
            name="ck_evolution_kpi_min_sample",
        ),
        sa.CheckConstraint(
            "auto_apply_enabled = FALSE",
            name="ck_evolution_kpi_auto_apply_disabled",
        ),
        sa.CheckConstraint(
            "(objective_id IS NULL AND scope_key = '__global__') "
            "OR (objective_id IS NOT NULL AND scope_key = objective_id)",
            name="ck_evolution_kpi_scope_key",
        ),
        sa.ForeignKeyConstraint(
            ["objective_id", "org_slug"],
            ["evolution_objectives.id", "evolution_objectives.org_slug"],
            name="fk_evolution_kpi_target_objective_org",
        ),
        sa.UniqueConstraint(
            "org_slug",
            "scope_key",
            "kpi_code",
            name="ux_evolution_kpi_target_scope",
        ),
    )
    op.create_index(
        "ix_evolution_kpi_targets_org_kpi",
        "evolution_kpi_targets",
        ["org_slug", "kpi_code"],
    )
    op.create_index(
        "ix_evolution_kpi_targets_org_objective",
        "evolution_kpi_targets",
        ["org_slug", "objective_id"],
    )

    op.create_table(
        "evolution_health_snapshots",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("objective_id", sa.String(length=96), nullable=True),
        sa.Column("captured_at", sa.BigInteger(), nullable=False),
        sa.Column("window_start", sa.BigInteger(), nullable=False),
        sa.Column("window_end", sa.BigInteger(), nullable=False),
        sa.Column("project_health_score", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("data_coverage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column(
            "production_go",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("dimensions_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("missing_kpis_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("blocker_kpis_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("release_id", sa.String(length=160), nullable=True),
        sa.Column("commit_sha", sa.String(length=64), nullable=True),
        sa.Column("deployment_id", sa.String(length=160), nullable=True),
        sa.Column("runtime_main_sha256", sa.String(length=64), nullable=True),
        sa.Column("formula_version", sa.String(length=160), nullable=False),
        sa.Column("captured_by", sa.String(length=180), nullable=False),
        sa.Column("capture_reason", sa.String(length=300), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "project_health_score IS NULL OR (project_health_score >= 0 AND project_health_score <= 100)",
            name="ck_evolution_health_score",
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_evolution_health_confidence",
        ),
        sa.CheckConstraint(
            "data_coverage >= 0 AND data_coverage <= 1",
            name="ck_evolution_health_coverage",
        ),
        sa.CheckConstraint(
            "status IN ('healthy','warning','critical','blocker','unknown')",
            name="ck_evolution_health_status",
        ),
        sa.ForeignKeyConstraint(
            ["objective_id", "org_slug"],
            ["evolution_objectives.id", "evolution_objectives.org_slug"],
            name="fk_evolution_health_objective_org",
        ),
    )
    op.create_index(
        "ix_evolution_health_org_captured",
        "evolution_health_snapshots",
        ["org_slug", "captured_at"],
    )
    op.create_index(
        "ix_evolution_health_org_objective_captured",
        "evolution_health_snapshots",
        ["org_slug", "objective_id", "captured_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_evolution_health_org_objective_captured",
        table_name="evolution_health_snapshots",
    )
    op.drop_index(
        "ix_evolution_health_org_captured",
        table_name="evolution_health_snapshots",
    )
    op.drop_table("evolution_health_snapshots")

    op.drop_index(
        "ix_evolution_kpi_targets_org_objective",
        table_name="evolution_kpi_targets",
    )
    op.drop_index(
        "ix_evolution_kpi_targets_org_kpi",
        table_name="evolution_kpi_targets",
    )
    op.drop_table("evolution_kpi_targets")

    op.drop_index(
        "ix_evolution_objectives_org_updated",
        table_name="evolution_objectives",
    )
    op.drop_index(
        "ix_evolution_objectives_org_status_priority",
        table_name="evolution_objectives",
    )
    op.drop_table("evolution_objectives")
