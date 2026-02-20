"""Add last_backup_error field to backup settings tables.

Revision ID: 011_backup_error_field
Revises: 010_backup_settings
Create Date: 2026-02-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '011_backup_error_field'
down_revision: Union[str, None] = '010_backup_settings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT EXISTS ("
            "SELECT FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :col"
            ")"
        ),
        {"table": table_name, "col": column_name},
    )
    return result.scalar()


def upgrade() -> None:
    if not column_exists("backup_settings", "last_backup_error"):
        op.add_column("backup_settings", sa.Column("last_backup_error", sa.Text, nullable=True))

    if not column_exists("household_backup_settings", "last_backup_error"):
        op.add_column("household_backup_settings", sa.Column("last_backup_error", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("household_backup_settings", "last_backup_error")
    op.drop_column("backup_settings", "last_backup_error")
