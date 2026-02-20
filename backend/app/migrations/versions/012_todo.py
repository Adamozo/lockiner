"""Add todo list module tables.

Revision ID: 012_todo
Revises: 011_backup_error_field
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '012_todo'
down_revision: Union[str, None] = '011_backup_error_field'
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
    if not table_exists("todo_lists"):
        op.create_table(
            "todo_lists",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String, nullable=False),
            sa.Column("date", sa.String, nullable=False),  # ISO 8601: YYYY-MM-DD
            sa.Column("created_in_advance_days", sa.Integer, nullable=False, server_default="0"),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_todo_lists_user", "todo_lists", ["user_id"])
        op.create_index("idx_todo_lists_date", "todo_lists", ["date"])
        op.create_unique_constraint("uq_todo_lists_user_date", "todo_lists", ["user_id", "date"])

    if not table_exists("todo_items"):
        op.create_table(
            "todo_items",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("list_id", sa.Integer, sa.ForeignKey("todo_lists.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String, nullable=False),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("completed", sa.Boolean, server_default="false"),
            sa.Column("completed_at", sa.String, nullable=True),
            sa.Column("estimated_minutes", sa.Integer, nullable=True),
            sa.Column("priority", sa.String, server_default="medium"),  # low / medium / high
            sa.Column("position", sa.Integer, nullable=False, server_default="0"),
            sa.Column("postponed_count", sa.Integer, nullable=False, server_default="0"),
            sa.Column("original_list_id", sa.Integer, sa.ForeignKey("todo_lists.id", ondelete="SET NULL"), nullable=True),
            sa.Column("item_reminder_enabled", sa.Boolean, server_default="false"),
            sa.Column("item_reminder_time", sa.String, nullable=True),  # "HH:MM"
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_todo_items_list", "todo_items", ["list_id"])
        op.create_index("idx_todo_items_user", "todo_items", ["user_id"])
        op.create_index("idx_todo_items_completed", "todo_items", ["completed"])

    if not table_exists("todo_postpone_logs"):
        op.create_table(
            "todo_postpone_logs",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("todo_item_id", sa.Integer, sa.ForeignKey("todo_items.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("from_list_id", sa.Integer, sa.ForeignKey("todo_lists.id", ondelete="SET NULL"), nullable=True),
            sa.Column("to_list_id", sa.Integer, sa.ForeignKey("todo_lists.id", ondelete="SET NULL"), nullable=True),
            sa.Column("excuse", sa.String, nullable=False, server_default="other"),  # busy / other
            sa.Column("postponed_at", sa.String, nullable=False),
        )
        op.create_index("idx_todo_postpone_logs_item", "todo_postpone_logs", ["todo_item_id"])
        op.create_index("idx_todo_postpone_logs_user", "todo_postpone_logs", ["user_id"])
        op.create_index("idx_todo_postpone_logs_date", "todo_postpone_logs", ["postponed_at"])

    if not table_exists("todo_notification_rules"):
        op.create_table(
            "todo_notification_rules",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("label", sa.String, nullable=True),
            # trigger_type: fixed_time | before_end_of_day | interval
            sa.Column("trigger_type", sa.String, nullable=False),
            sa.Column("fixed_time", sa.String, nullable=True),           # "HH:MM" for fixed_time
            sa.Column("minutes_before_end", sa.Integer, nullable=True),  # for before_end_of_day
            sa.Column("interval_minutes", sa.Integer, nullable=True),    # for interval
            sa.Column("window_start", sa.String, nullable=True),         # "HH:MM" for interval
            sa.Column("window_end", sa.String, nullable=True),           # "HH:MM" for interval
            sa.Column("notify_only_if_incomplete", sa.Boolean, server_default="true"),
            sa.Column("enabled", sa.Boolean, server_default="true"),
            sa.Column("last_sent_at", sa.String, nullable=True),         # ISO datetime
            sa.Column("created_at", sa.String, nullable=False),
        )
        op.create_index("idx_todo_notification_rules_user", "todo_notification_rules", ["user_id"])
        op.create_index("idx_todo_notification_rules_enabled", "todo_notification_rules", ["enabled"])


def downgrade() -> None:
    op.drop_table("todo_notification_rules")
    op.drop_table("todo_postpone_logs")
    op.drop_table("todo_items")
    op.drop_table("todo_lists")
