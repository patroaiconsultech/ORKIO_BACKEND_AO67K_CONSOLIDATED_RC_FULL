"""patch93: user approval + cost events + message user fields

Revision ID: 0007_patch93
Revises: 0006_patch85_intent_and_message_agent
Create Date: 2026-02-05

AO68B safety note:
This migration is intentionally idempotent because some staging databases may
already have been partially reconciled by boot-time schema guards before Alembic
runs. The migration must not crash when a column/table/index already exists.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0007_patch93"
down_revision = "0006_patch85_intent_and_message_agent"
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return table_name in _inspector().get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(col.get("name") == column_name for col in _inspector().get_columns(table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return any(idx.get("name") == index_name for idx in _inspector().get_indexes(table_name))


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _table_exists(table_name):
        return
    if _column_exists(table_name, column.name):
        return
    with op.batch_alter_table(table_name) as batch:
        batch.add_column(column)


def _drop_column_if_exists(table_name: str, column_name: str) -> None:
    if not _column_exists(table_name, column_name):
        return
    with op.batch_alter_table(table_name) as batch:
        batch.drop_column(column_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _table_exists(table_name):
        return
    if _index_exists(table_name, index_name):
        return
    op.create_index(index_name, table_name, columns)


def _drop_index_if_exists(index_name: str, table_name: str) -> None:
    if not _index_exists(table_name, index_name):
        return
    op.drop_index(index_name, table_name=table_name)


def upgrade():
    # users.approved_at (nullable). Keep existing users approved by default.
    _add_column_if_missing(
        "users",
        sa.Column("approved_at", sa.BigInteger(), nullable=True),
    )

    if _column_exists("users", "approved_at") and _column_exists("users", "created_at"):
        op.execute("UPDATE users SET approved_at = created_at WHERE approved_at IS NULL")

    # messages.user_id + messages.user_name
    _add_column_if_missing(
        "messages",
        sa.Column("user_id", sa.String(), nullable=True),
    )
    _add_column_if_missing(
        "messages",
        sa.Column("user_name", sa.String(), nullable=True),
    )

    # cost_events
    if not _table_exists("cost_events"):
        op.create_table(
            "cost_events",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("org_slug", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=True),
            sa.Column("thread_id", sa.String(), nullable=True),
            sa.Column("message_id", sa.String(), nullable=True),
            sa.Column("agent_id", sa.String(), nullable=True),
            sa.Column("model", sa.String(), nullable=True),
            sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
        )

    _create_index_if_missing("ix_cost_events_org_slug", "cost_events", ["org_slug"])
    _create_index_if_missing("ix_cost_events_thread_id", "cost_events", ["thread_id"])
    _create_index_if_missing("ix_cost_events_message_id", "cost_events", ["message_id"])
    _create_index_if_missing("ix_cost_events_agent_id", "cost_events", ["agent_id"])


def downgrade():
    _drop_index_if_exists("ix_cost_events_agent_id", "cost_events")
    _drop_index_if_exists("ix_cost_events_message_id", "cost_events")
    _drop_index_if_exists("ix_cost_events_thread_id", "cost_events")
    _drop_index_if_exists("ix_cost_events_org_slug", "cost_events")

    if _table_exists("cost_events"):
        op.drop_table("cost_events")

    _drop_column_if_exists("messages", "user_name")
    _drop_column_if_exists("messages", "user_id")
    _drop_column_if_exists("users", "approved_at")
