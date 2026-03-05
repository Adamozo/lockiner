"""Add receipt_images table for multi-photo receipts.

Revision ID: 018_receipt_multi_images
Revises: 017_user_language
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '018_receipt_multi_images'
down_revision: Union[str, None] = 'fbc51d6de763'
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
    if not table_exists("receipt_images"):
        op.create_table(
            "receipt_images",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("receipt_id", sa.Integer(), nullable=False),
            sa.Column("image_path", sa.String(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.String(), nullable=True),
            sa.ForeignKeyConstraint(["receipt_id"], ["receipts.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("idx_receipt_images_receipt_id", "receipt_images", ["receipt_id"])


def downgrade() -> None:
    op.drop_index("idx_receipt_images_receipt_id", table_name="receipt_images")
    op.drop_table("receipt_images")
