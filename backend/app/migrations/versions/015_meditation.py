"""Add meditation sessions table.

Revision ID: 015_meditation
Revises: 014_body_measurements
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '015_meditation'
down_revision: Union[str, None] = '014_body_measurements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
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
    if not table_exists("meditation_sessions"):
        op.create_table(
            "meditation_sessions",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("date", sa.String, nullable=False, index=True),
            sa.Column("started_at", sa.String, nullable=False),
            sa.Column("duration_seconds", sa.Integer, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("completed", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("created_at", sa.String, nullable=False),
        )
        op.create_index("idx_meditation_sessions_user", "meditation_sessions", ["user_id"])
        op.create_index("idx_meditation_sessions_date", "meditation_sessions", ["date"])
        op.create_index("idx_meditation_sessions_completed", "meditation_sessions", ["completed"])


def downgrade() -> None:
    op.drop_table("meditation_sessions")
