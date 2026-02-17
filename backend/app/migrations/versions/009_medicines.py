"""Add medicines/supplements module tables.

Revision ID: 009_medicines
Revises: 008_journal
Create Date: 2026-02-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009_medicines'
down_revision: Union[str, None] = '008_journal'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT EXISTS ("
            "SELECT FROM information_schema.tables "
            "WHERE table_name = :table"
            ")"
        ),
        {"table": table_name},
    )
    return result.scalar()


def upgrade() -> None:
    if not table_exists("medicines"):
        op.create_table(
            "medicines",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String, nullable=False),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("dosage", sa.String, nullable=True),
            sa.Column("unit", sa.String, nullable=True),
            sa.Column("color", sa.String, nullable=True),
            sa.Column("icon", sa.String, nullable=True),
            sa.Column("active", sa.Boolean, server_default="true"),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_medicines_user", "medicines", ["user_id"])
        op.create_index("idx_medicines_active", "medicines", ["active"])

    if not table_exists("medicine_schedules"):
        op.create_table(
            "medicine_schedules",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("medicine_id", sa.Integer, sa.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False),
            sa.Column("frequency_type", sa.String, nullable=False),
            sa.Column("frequency_value", sa.Integer, nullable=True),
            sa.Column("time_of_day", sa.String, nullable=False),
            sa.Column("days_of_week", sa.String, nullable=True),
            sa.Column("day_of_month", sa.Integer, nullable=True),
            sa.Column("notifications_enabled", sa.Boolean, server_default="true"),
            sa.Column("active", sa.Boolean, server_default="true"),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_medicine_schedules_medicine", "medicine_schedules", ["medicine_id"])
        op.create_index("idx_medicine_schedules_active", "medicine_schedules", ["active"])

    if not table_exists("medicine_logs"):
        op.create_table(
            "medicine_logs",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("medicine_id", sa.Integer, sa.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False),
            sa.Column("schedule_id", sa.Integer, sa.ForeignKey("medicine_schedules.id", ondelete="CASCADE"), nullable=False),
            sa.Column("scheduled_date", sa.String, nullable=False),
            sa.Column("scheduled_time", sa.String, nullable=False),
            sa.Column("taken", sa.Boolean, server_default="false"),
            sa.Column("taken_at", sa.String, nullable=True),
            sa.Column("created_at", sa.String, nullable=False),
        )
        op.create_index("idx_medicine_logs_medicine", "medicine_logs", ["medicine_id"])
        op.create_index("idx_medicine_logs_schedule", "medicine_logs", ["schedule_id"])
        op.create_index("idx_medicine_logs_date", "medicine_logs", ["scheduled_date"])
        op.create_unique_constraint("uq_medicine_logs_schedule_date", "medicine_logs", ["schedule_id", "scheduled_date"])


def downgrade() -> None:
    op.drop_table("medicine_logs")
    op.drop_table("medicine_schedules")
    op.drop_table("medicines")
