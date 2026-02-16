"""Add two-factor authentication columns to users table.

Revision ID: 007_two_factor_auth
Revises: 006_custom_reminders
Create Date: 2026-02-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_two_factor_auth'
down_revision: Union[str, None] = '006_custom_reminders'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT EXISTS ("
            "SELECT FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column"
            ")"
        ),
        {"table": table_name, "column": column_name},
    )
    return result.scalar()


def upgrade() -> None:
    table = "users"
    if not column_exists(table, "totp_secret_encrypted"):
        op.add_column(table, sa.Column("totp_secret_encrypted", sa.Text, nullable=True))
    if not column_exists(table, "totp_enabled"):
        op.add_column(table, sa.Column("totp_enabled", sa.Boolean, default=False, server_default='false'))
    if not column_exists(table, "recovery_codes_hash"):
        op.add_column(table, sa.Column("recovery_codes_hash", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("users", "recovery_codes_hash")
    op.drop_column("users", "totp_enabled")
    op.drop_column("users", "totp_secret_encrypted")
