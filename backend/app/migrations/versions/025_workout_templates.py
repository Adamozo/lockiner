"""Add workout_templates and workout_template_exercises tables.

Revision ID: 025_workout_templates
Revises: 024_dek
Create Date: 2026-04-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = '025_workout_templates'
down_revision: Union[str, None] = '024_dek'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    return table in insp.get_table_names()


def upgrade() -> None:
    if not table_exists("workout_templates"):
        op.create_table(
            "workout_templates",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("workout_type", sa.String(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.String(), nullable=False),
            sa.Column("updated_at", sa.String(), nullable=True),
        )

    if not table_exists("workout_template_exercises"):
        op.create_table(
            "workout_template_exercises",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("template_id", sa.Integer(), sa.ForeignKey("workout_templates.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("sets", sa.Integer(), nullable=False),
            sa.Column("reps", sa.Integer(), nullable=False),
            sa.Column("weight_kg", sa.Float(), nullable=False),
            sa.Column("rest_seconds", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("workout_template_exercises")
    op.drop_table("workout_templates")
