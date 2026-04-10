"""Add encrypted_dek and dek_salt columns to users table.

Revision ID: 024_dek
Revises: 023_food_daily_goals
Create Date: 2026-03-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = '024_dek'
down_revision: Union[str, None] = '023_food_daily_goals'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not column_exists("users", "encrypted_dek"):
        op.add_column("users", sa.Column("encrypted_dek", sa.Text(), nullable=True))
    if not column_exists("users", "dek_salt"):
        op.add_column("users", sa.Column("dek_salt", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "encrypted_dek")
    op.drop_column("users", "dek_salt")
