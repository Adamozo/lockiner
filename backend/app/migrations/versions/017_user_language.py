"""Add language field to users table.

Revision ID: 017_user_language
Revises: 016_workout_timer
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '017_user_language'
down_revision: Union[str, None] = '016_workout_timer'
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
    if not column_exists("users", "language"):
        op.add_column(
            "users",
            sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        )


def downgrade() -> None:
    op.drop_column("users", "language")
