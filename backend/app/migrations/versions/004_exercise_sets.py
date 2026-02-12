"""Add exercise_sets table for per-set tracking.

Revision ID: 004_exercise_sets
Revises: 003_admin_notifications
Create Date: 2026-02-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_exercise_sets'
down_revision: Union[str, None] = '003_admin_notifications'
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
    if not table_exists("exercise_sets"):
        op.create_table(
            "exercise_sets",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "exercise_id",
                sa.Integer(),
                sa.ForeignKey("exercises.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("set_number", sa.Integer(), nullable=False),
            sa.Column("reps", sa.Integer(), nullable=False),
            sa.Column("weight_kg", sa.Float(), nullable=False),
            sa.Column("completed", sa.Boolean(), server_default=sa.False_()),
        )
        op.create_index("idx_exercise_sets_exercise", "exercise_sets", ["exercise_id"])


def downgrade() -> None:
    op.drop_index("idx_exercise_sets_exercise", table_name="exercise_sets")
    op.drop_table("exercise_sets")
