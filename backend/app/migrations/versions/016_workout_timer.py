"""Add workout timer fields to workouts table.

Revision ID: 016_workout_timer
Revises: 015_meditation
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '016_workout_timer'
down_revision: Union[str, None] = '015_meditation'
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
    if not column_exists("workouts", "timer_started_at"):
        op.add_column("workouts", sa.Column("timer_started_at", sa.String, nullable=True))
    if not column_exists("workouts", "timer_ended_at"):
        op.add_column("workouts", sa.Column("timer_ended_at", sa.String, nullable=True))
    if not column_exists("workouts", "timer_paused_at"):
        op.add_column("workouts", sa.Column("timer_paused_at", sa.String, nullable=True))
    if not column_exists("workouts", "total_paused_seconds"):
        op.add_column("workouts", sa.Column("total_paused_seconds", sa.Integer, nullable=False, server_default="0"))
    if not column_exists("workouts", "default_rest_seconds"):
        op.add_column("workouts", sa.Column("default_rest_seconds", sa.Integer, nullable=True))


def downgrade() -> None:
    op.drop_column("workouts", "default_rest_seconds")
    op.drop_column("workouts", "total_paused_seconds")
    op.drop_column("workouts", "timer_paused_at")
    op.drop_column("workouts", "timer_ended_at")
    op.drop_column("workouts", "timer_started_at")
