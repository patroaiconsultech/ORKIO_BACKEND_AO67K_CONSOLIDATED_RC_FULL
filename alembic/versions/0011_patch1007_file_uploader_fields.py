"""patch1007: file uploader provenance fields

Revision ID: 0011_patch1007_file_uploader_fields
Revises: 0010_patch1006
Create Date: 2026-02-12

AO68D: Idempotent-safe migration for staging/prod-like databases where
the runtime schema reconciler may already have created the uploader columns.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0011_patch1007_file_uploader_fields"
down_revision = "0010_patch1006"
branch_labels = None
depends_on = None


TABLE_NAME = "files"


def _table_exists(bind, table_name: str) -> bool:
    return bool(inspect(bind).has_table(table_name))


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    columns = inspect(bind).get_columns(table_name)
    return any(col.get("name") == column_name for col in columns)


def _add_column_if_missing(bind, table_name: str, column: sa.Column) -> None:
    if not _table_exists(bind, table_name):
        return
    if not _column_exists(bind, table_name, column.name):
        op.add_column(table_name, column)


def _drop_column_if_exists(bind, table_name: str, column_name: str) -> None:
    if _column_exists(bind, table_name, column_name):
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    bind = op.get_bind()

    _add_column_if_missing(
        bind,
        TABLE_NAME,
        sa.Column("uploader_id", sa.String(), nullable=True),
    )
    _add_column_if_missing(
        bind,
        TABLE_NAME,
        sa.Column("uploader_name", sa.String(), nullable=True),
    )
    _add_column_if_missing(
        bind,
        TABLE_NAME,
        sa.Column("uploader_email", sa.String(), nullable=True),
    )


def downgrade() -> None:
    bind = op.get_bind()

    _drop_column_if_exists(bind, TABLE_NAME, "uploader_email")
    _drop_column_if_exists(bind, TABLE_NAME, "uploader_name")
    _drop_column_if_exists(bind, TABLE_NAME, "uploader_id")
