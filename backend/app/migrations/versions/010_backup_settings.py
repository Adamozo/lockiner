"""Add backup settings tables.

Revision ID: 010_backup_settings
Revises: 009_medicines
Create Date: 2026-02-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010_backup_settings'
down_revision: Union[str, None] = '009_medicines'
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
    if not table_exists("backup_settings"):
        op.create_table(
            "backup_settings",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("encrypted_password", sa.Text, nullable=True),
            sa.Column("auto_backup_enabled", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("frequency", sa.String(20), nullable=False, server_default="weekly"),
            sa.Column("hour", sa.Integer, nullable=False, server_default="3"),
            sa.Column("minute", sa.Integer, nullable=False, server_default="0"),
            sa.Column("day_of_week", sa.Integer, nullable=True),
            sa.Column("day_of_month", sa.Integer, nullable=True),
            sa.Column("google_drive_connected", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("google_drive_folder_id", sa.String, nullable=True),
            sa.Column("last_backup_at", sa.String, nullable=True),
            sa.Column("last_backup_filename", sa.String, nullable=True),
            sa.Column("last_backup_size_bytes", sa.Integer, nullable=True),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_backup_settings_user", "backup_settings", ["user_id"])
        op.create_unique_constraint("uq_backup_settings_user", "backup_settings", ["user_id"])

    if not table_exists("household_backup_settings"):
        op.create_table(
            "household_backup_settings",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("household_id", sa.Integer, sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
            sa.Column("configured_by_user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("encrypted_password", sa.Text, nullable=True),
            sa.Column("auto_backup_enabled", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("frequency", sa.String(20), nullable=False, server_default="weekly"),
            sa.Column("hour", sa.Integer, nullable=False, server_default="3"),
            sa.Column("minute", sa.Integer, nullable=False, server_default="0"),
            sa.Column("day_of_week", sa.Integer, nullable=True),
            sa.Column("day_of_month", sa.Integer, nullable=True),
            sa.Column("google_drive_connected", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("google_drive_folder_id", sa.String, nullable=True),
            sa.Column("last_backup_at", sa.String, nullable=True),
            sa.Column("last_backup_filename", sa.String, nullable=True),
            sa.Column("last_backup_size_bytes", sa.Integer, nullable=True),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_household_backup_settings_household", "household_backup_settings", ["household_id"])
        op.create_unique_constraint("uq_household_backup_settings", "household_backup_settings", ["household_id"])


def downgrade() -> None:
    op.drop_table("household_backup_settings")
    op.drop_table("backup_settings")
