"""Add journal module tables.

Revision ID: 008_journal
Revises: 007_two_factor_auth
Create Date: 2026-02-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_journal'
down_revision: Union[str, None] = '007_two_factor_auth'
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
    if not table_exists("journal_entries"):
        op.create_table(
            "journal_entries",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("date", sa.String, nullable=False),
            sa.Column("mood_score", sa.Integer, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_journal_entries_user", "journal_entries", ["user_id"])
        op.create_index("idx_journal_entries_date", "journal_entries", ["date"])
        op.create_unique_constraint("uq_journal_entries_user_date", "journal_entries", ["user_id", "date"])

    if not table_exists("journal_items"):
        op.create_table(
            "journal_items",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("entry_id", sa.Integer, sa.ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False),
            sa.Column("category", sa.String, nullable=False),
            sa.Column("position", sa.Integer, nullable=False),
            sa.Column("content", sa.Text, nullable=False),
        )
        op.create_index("idx_journal_items_entry", "journal_items", ["entry_id"])
        op.create_index("idx_journal_items_category", "journal_items", ["category"])

    if not table_exists("journal_reports"):
        op.create_table(
            "journal_reports",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("report_type", sa.String, nullable=False),
            sa.Column("period", sa.String, nullable=False),
            sa.Column("data", sa.Text, nullable=False),
            sa.Column("entry_count", sa.Integer, nullable=False, server_default="0"),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_journal_reports_user", "journal_reports", ["user_id"])
        op.create_unique_constraint("uq_journal_reports_user_type_period", "journal_reports", ["user_id", "report_type", "period"])


def downgrade() -> None:
    op.drop_table("journal_reports")
    op.drop_table("journal_items")
    op.drop_table("journal_entries")
