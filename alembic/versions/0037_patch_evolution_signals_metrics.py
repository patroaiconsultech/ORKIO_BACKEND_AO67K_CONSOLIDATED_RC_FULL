"""Add governed platform evolution metric snapshots and agent evaluations.

Revision ID: 0037_patch_evolution_signals_metrics
Revises: 0036_patch_file_requests_reconcile
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0037_patch_evolution_signals_metrics"
down_revision = "0036_patch_file_requests_reconcile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_evolution_metric_snapshots",
        sa.Column("snapshot_id", sa.String(length=96), primary_key=True),
        sa.Column("snapshot_group_id", sa.String(length=96), nullable=False),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("metric_key", sa.String(length=80), nullable=False),
        sa.Column("scope_type", sa.String(length=24), nullable=False),
        sa.Column("scope_id", sa.String(length=160), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sample_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("signal_status", sa.String(length=40), nullable=False),
        sa.Column("formula_version", sa.String(length=120), nullable=False),
        sa.Column("window_start", sa.BigInteger(), nullable=False),
        sa.Column("window_end", sa.BigInteger(), nullable=False),
        sa.Column("source_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("missing_sources_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("evidence_refs_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("captured_by", sa.String(length=180), nullable=False),
        sa.Column("capture_reason", sa.String(length=300), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 100)",
            name="ck_evolution_metric_snapshot_score",
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 100",
            name="ck_evolution_metric_snapshot_confidence",
        ),
        sa.CheckConstraint(
            "sample_count >= 0",
            name="ck_evolution_metric_snapshot_sample_count",
        ),
        sa.CheckConstraint(
            "scope_type IN ('platform', 'agent')",
            name="ck_evolution_metric_snapshot_scope_type",
        ),
    )
    op.create_index(
        "ix_platform_evolution_metric_org_metric_created",
        "platform_evolution_metric_snapshots",
        ["org_slug", "metric_key", "created_at"],
    )
    op.create_index(
        "ix_platform_evolution_metric_org_scope_created",
        "platform_evolution_metric_snapshots",
        ["org_slug", "scope_type", "scope_id", "created_at"],
    )
    op.create_index(
        "ix_platform_evolution_metric_group",
        "platform_evolution_metric_snapshots",
        ["snapshot_group_id"],
    )

    op.create_table(
        "agent_capability_evaluations",
        sa.Column("evaluation_id", sa.String(length=96), primary_key=True),
        sa.Column("org_slug", sa.String(length=160), nullable=False),
        sa.Column("agent_id", sa.String(length=160), nullable=False),
        sa.Column("capability_id", sa.String(length=160), nullable=False),
        sa.Column("evaluation_key", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("evidence_ref", sa.String(length=500), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("evaluator_ref", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "status IN ('passed', 'failed')",
            name="ck_agent_capability_evaluation_status",
        ),
        sa.CheckConstraint(
            "score >= 0 AND score <= 100",
            name="ck_agent_capability_evaluation_score",
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 100",
            name="ck_agent_capability_evaluation_confidence",
        ),
    )
    op.create_index(
        "ix_agent_capability_eval_org_agent_created",
        "agent_capability_evaluations",
        ["org_slug", "agent_id", "created_at"],
    )
    op.create_index(
        "ix_agent_capability_eval_org_capability_created",
        "agent_capability_evaluations",
        ["org_slug", "capability_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agent_capability_eval_org_capability_created",
        table_name="agent_capability_evaluations",
    )
    op.drop_index(
        "ix_agent_capability_eval_org_agent_created",
        table_name="agent_capability_evaluations",
    )
    op.drop_table("agent_capability_evaluations")

    op.drop_index(
        "ix_platform_evolution_metric_group",
        table_name="platform_evolution_metric_snapshots",
    )
    op.drop_index(
        "ix_platform_evolution_metric_org_scope_created",
        table_name="platform_evolution_metric_snapshots",
    )
    op.drop_index(
        "ix_platform_evolution_metric_org_metric_created",
        table_name="platform_evolution_metric_snapshots",
    )
    op.drop_table("platform_evolution_metric_snapshots")
