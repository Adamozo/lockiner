"""Add notification_schedules table for per-user reminder configuration.

Revision ID: 005_notification_schedules
Revises: 004_exercise_sets
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_notification_schedules'
down_revision: Union[str, None] = '004_exercise_sets'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table)"
        ),
        {"table": table_name},
    )
    return result.scalar()


def upgrade() -> None:
    if not table_exists("notification_schedules"):
        op.create_table(
            "notification_schedules",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("reminder_type", sa.String(50), nullable=False),
            sa.Column("enabled", sa.Boolean(), server_default=sa.False_(), nullable=False),
            sa.Column("frequency", sa.String(20), nullable=False, server_default="daily"),
            sa.Column("hour", sa.Integer(), nullable=False, server_default=sa.text("9")),
            sa.Column("minute", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("day_of_week", sa.Integer(), nullable=True),
            sa.Column("day_of_month", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.String(), nullable=False),
            sa.Column("updated_at", sa.String(), nullable=True),
            sa.UniqueConstraint("user_id", "reminder_type", name="uq_user_reminder_type"),
        )
        op.create_index("idx_notification_schedules_user", "notification_schedules", ["user_id"])
        op.create_index("idx_notification_schedules_enabled", "notification_schedules", ["enabled"])


def downgrade() -> None:
    op.drop_index("idx_notification_schedules_enabled", table_name="notification_schedules")
    op.drop_index("idx_notification_schedules_user", table_name="notification_schedules")
    op.drop_table("notification_schedules")
