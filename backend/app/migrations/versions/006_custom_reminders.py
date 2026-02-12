"""Add custom reminder columns to notification_schedules.

Revision ID: 006_custom_reminders
Revises: 005_notification_schedules
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_custom_reminders'
down_revision: Union[str, None] = '005_notification_schedules'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT EXISTS ("
            "SELECT FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column"
            ")"
        ),
        {"table": table_name, "column": column_name},
    )
    return result.scalar()


def upgrade() -> None:
    table = "notification_schedules"
    if not column_exists(table, "custom_name"):
        op.add_column(table, sa.Column("custom_name", sa.String(100), nullable=True))
    if not column_exists(table, "custom_icon"):
        op.add_column(table, sa.Column("custom_icon", sa.String(100), nullable=True))
    if not column_exists(table, "custom_title"):
        op.add_column(table, sa.Column("custom_title", sa.String(200), nullable=True))
    if not column_exists(table, "custom_body"):
        op.add_column(table, sa.Column("custom_body", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("notification_schedules", "custom_body")
    op.drop_column("notification_schedules", "custom_title")
    op.drop_column("notification_schedules", "custom_icon")
    op.drop_column("notification_schedules", "custom_name")
