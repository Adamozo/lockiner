"""Add shopping lists module tables.

Revision ID: 013_shopping
Revises: 012_todo
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '013_shopping'
down_revision: Union[str, None] = '012_todo'
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
    if not table_exists("shopping_lists"):
        op.create_table(
            "shopping_lists",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("household_id", sa.Integer, sa.ForeignKey("households.id", ondelete="SET NULL"), nullable=True),
            sa.Column("visibility", sa.String, nullable=False, server_default="private"),  # private | household
            sa.Column("name", sa.String, nullable=False),
            sa.Column("store_name", sa.String, nullable=True),
            sa.Column("planned_date", sa.String, nullable=True),  # ISO 8601: YYYY-MM-DD
            sa.Column("status", sa.String, nullable=False, server_default="active"),  # active | completed | archived
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_shopping_lists_owner", "shopping_lists", ["owner_id"])
        op.create_index("idx_shopping_lists_household", "shopping_lists", ["household_id"])
        op.create_index("idx_shopping_lists_status", "shopping_lists", ["status"])

    if not table_exists("shopping_list_items"):
        op.create_table(
            "shopping_list_items",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("list_id", sa.Integer, sa.ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False),
            sa.Column("added_by", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("food_product_id", sa.Integer, sa.ForeignKey("food_products.id", ondelete="SET NULL"), nullable=True),
            sa.Column("name", sa.String, nullable=False),
            sa.Column("quantity", sa.Float, nullable=True),
            sa.Column("unit", sa.String, nullable=True),
            sa.Column("category", sa.String, nullable=True),  # free text
            sa.Column("status", sa.String, nullable=False, server_default="pending"),  # pending | in_cart | purchased
            sa.Column("is_recurring", sa.Boolean, nullable=False, server_default="false"),
            sa.Column("notes", sa.String, nullable=True),
            sa.Column("position", sa.Integer, nullable=False, server_default="0"),
            sa.Column("created_at", sa.String, nullable=False),
            sa.Column("updated_at", sa.String, nullable=True),
        )
        op.create_index("idx_shopping_list_items_list", "shopping_list_items", ["list_id"])
        op.create_index("idx_shopping_list_items_added_by", "shopping_list_items", ["added_by"])
        op.create_index("idx_shopping_list_items_status", "shopping_list_items", ["status"])


def downgrade() -> None:
    op.drop_table("shopping_list_items")
    op.drop_table("shopping_lists")
