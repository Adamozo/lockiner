"""Add body measurements module tables.

Revision ID: 014_body_measurements
Revises: 013_shopping
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '014_body_measurements'
down_revision: Union[str, None] = '013_shopping'
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
    if not table_exists("user_body_profiles"):
        op.create_table(
            "user_body_profiles",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column("height_cm", sa.Float, nullable=True),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_user_body_profiles_user", "user_body_profiles", ["user_id"])

    if not table_exists("body_measurement_entries"):
        op.create_table(
            "body_measurement_entries",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("date", sa.String, nullable=False, index=True),
            sa.Column("bicep_cm", sa.Float, nullable=True),
            sa.Column("waist_cm", sa.Float, nullable=True),
            sa.Column("thigh_cm", sa.Float, nullable=True),
            sa.Column("calf_cm", sa.Float, nullable=True),
            sa.Column("chest_cm", sa.Float, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.String, nullable=False),
        )
        op.create_index("idx_body_measurement_entries_user", "body_measurement_entries", ["user_id"])
        op.create_index("idx_body_measurement_entries_date", "body_measurement_entries", ["date"])


def downgrade() -> None:
    op.drop_table("body_measurement_entries")
    op.drop_table("user_body_profiles")
