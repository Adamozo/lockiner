"""Add food_daily_goals table and extend food_consumption_log.

Revision ID: 023_food_daily_goals
Revises: 022_food_recipes
Create Date: 2026-03-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = '023_food_daily_goals'
down_revision: Union[str, None] = '022_food_recipes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table)]
    return column in cols


def table_exists(table: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    return table in insp.get_table_names()


def upgrade() -> None:
    # Create food_daily_goals table
    if not table_exists("food_daily_goals"):
        op.create_table(
            "food_daily_goals",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column("calories", sa.Float(), nullable=True, server_default="2000"),
            sa.Column("protein", sa.Float(), nullable=True),
            sa.Column("carbohydrates", sa.Float(), nullable=True),
            sa.Column("fat", sa.Float(), nullable=True),
            sa.Column("updated_at", sa.String(), nullable=True),
        )

    # Extend food_consumption_log with new columns
    if not column_exists("food_consumption_log", "off_product_code"):
        op.add_column("food_consumption_log", sa.Column("off_product_code", sa.String(), nullable=True))

    if not column_exists("food_consumption_log", "product_name"):
        op.add_column("food_consumption_log", sa.Column("product_name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_table("food_daily_goals")
    op.drop_column("food_consumption_log", "off_product_code")
    op.drop_column("food_consumption_log", "product_name")
