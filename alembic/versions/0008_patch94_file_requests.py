"""patch94: file requests for institutional uploads

Revision ID: 0008_patch94
Revises: 0007_patch93
Create Date: 2026-02-05

AO68C safety note:
This migration is intentionally idempotent for staging/RC environments where
schema boot/reconcile may have already created the file_requests table before
Alembic records the revision. It preserves the original schema contract while
avoiding DuplicateTable/DuplicateIndex crashes during deployment.
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_patch94"
down_revision = "0007_patch93"
branch_labels = None
depends_on = None


TABLE_NAME = "file_requests"


def _inspector():
    return sa.inspect(op.get_bind())


def _table_exists(table_name: str) -> bool:
    return table_name in _inspector().get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return column_name in {column["name"] for column in _inspector().get_columns(table_name)}


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    return index_name in {index["name"] for index in _inspector().get_indexes(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _column_exists(table_name, column.name):
        op.add_column(table_name, column)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if _table_exists(table_name) and not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns)


def upgrade():
    if not _table_exists(TABLE_NAME):
        op.create_table(
            TABLE_NAME,
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("org_slug", sa.String(), nullable=False),
            sa.Column("file_id", sa.String(), nullable=False),
            sa.Column("requested_by_user_id", sa.String(), nullable=True),
            sa.Column("requested_by_user_name", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="pending"),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
            sa.Column("resolved_at", sa.BigInteger(), nullable=True),
            sa.Column("resolved_by_admin_id", sa.String(), nullable=True),
        )
    else:
        _add_column_if_missing(TABLE_NAME, sa.Column("id", sa.String(), primary_key=True))
        _add_column_if_missing(TABLE_NAME, sa.Column("org_slug", sa.String(), nullable=False))
        _add_column_if_missing(TABLE_NAME, sa.Column("file_id", sa.String(), nullable=False))
        _add_column_if_missing(TABLE_NAME, sa.Column("requested_by_user_id", sa.String(), nullable=True))
        _add_column_if_missing(TABLE_NAME, sa.Column("requested_by_user_name", sa.String(), nullable=True))
        _add_column_if_missing(TABLE_NAME, sa.Column("status", sa.String(), nullable=False, server_default="pending"))
        _add_column_if_missing(TABLE_NAME, sa.Column("created_at", sa.BigInteger(), nullable=False))
        _add_column_if_missing(TABLE_NAME, sa.Column("resolved_at", sa.BigInteger(), nullable=True))
        _add_column_if_missing(TABLE_NAME, sa.Column("resolved_by_admin_id", sa.String(), nullable=True))

    _create_index_if_missing("ix_file_requests_org_slug", TABLE_NAME, ["org_slug"])
    _create_index_if_missing("ix_file_requests_file_id", TABLE_NAME, ["file_id"])
    _create_index_if_missing("ix_file_requests_status", TABLE_NAME, ["status"])


def downgrade():
    # Conservative rollback: only drop objects created by this migration when present.
    if _index_exists(TABLE_NAME, "ix_file_requests_status"):
        op.drop_index("ix_file_requests_status", table_name=TABLE_NAME)
    if _index_exists(TABLE_NAME, "ix_file_requests_file_id"):
        op.drop_index("ix_file_requests_file_id", table_name=TABLE_NAME)
    if _index_exists(TABLE_NAME, "ix_file_requests_org_slug"):
        op.drop_index("ix_file_requests_org_slug", table_name=TABLE_NAME)

    if _table_exists(TABLE_NAME):
        op.drop_table(TABLE_NAME)
