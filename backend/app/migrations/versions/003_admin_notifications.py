"""Add admin role, voucher status, and notification tables.

Safe for production: uses column_exists / table_exists checks.
Does NOT delete any existing data.

Revision ID: 003_admin_notifications
Revises: 002_seed_data
Create Date: 2026-02-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_admin_notifications'
down_revision: Union[str, None] = '002_seed_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column"
        ),
        {"table": table_name, "column": column_name},
    )
    return result.fetchone() is not None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name = :table AND table_schema = 'public'"
        ),
        {"table": table_name},
    )
    return result.fetchone() is not None


def upgrade() -> None:
    # =========================================================================
    # 1. users.role — default "user", existing users get "user"
    # =========================================================================
    if not column_exists("users", "role"):
        op.add_column(
            "users",
            sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        )

    # =========================================================================
    # 2. vouchers.status — default "available"
    # =========================================================================
    if not column_exists("vouchers", "status"):
        op.add_column(
            "vouchers",
            sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        )
        # Sync: already used vouchers → status="used"
        op.execute("UPDATE vouchers SET status = 'used' WHERE used_by_user_id IS NOT NULL")

    # =========================================================================
    # 3. notifications table
    # =========================================================================
    if not table_exists("notifications"):
        op.create_table(
            "notifications",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("notification_type", sa.String(50), nullable=False, server_default="general"),
            sa.Column("created_at", sa.String(), nullable=True),
            sa.Column(
                "created_by_user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.create_index("idx_notifications_created_by", "notifications", ["created_by_user_id"])

    # =========================================================================
    # 4. user_notifications table (M2M junction)
    # =========================================================================
    if not table_exists("user_notifications"):
        op.create_table(
            "user_notifications",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "notification_id",
                sa.Integer(),
                sa.ForeignKey("notifications.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("status", sa.String(20), nullable=False, server_default="unread"),
            sa.Column("read_at", sa.String(), nullable=True),
            sa.Column("created_at", sa.String(), nullable=True),
        )
        op.create_index("idx_user_notifications_user", "user_notifications", ["user_id"])
        op.create_index("idx_user_notifications_notification", "user_notifications", ["notification_id"])

    # =========================================================================
    # 5. push_subscriptions table
    # =========================================================================
    if not table_exists("push_subscriptions"):
        op.create_table(
            "push_subscriptions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("endpoint", sa.Text(), nullable=False),
            sa.Column("p256dh_key", sa.String(), nullable=False),
            sa.Column("auth_key", sa.String(), nullable=False),
            sa.Column("created_at", sa.String(), nullable=True),
        )
        op.create_index("idx_push_subscriptions_user", "push_subscriptions", ["user_id"])


def downgrade() -> None:
    # Drop tables (reverse order)
    if table_exists("push_subscriptions"):
        op.drop_table("push_subscriptions")

    if table_exists("user_notifications"):
        op.drop_table("user_notifications")

    if table_exists("notifications"):
        op.drop_table("notifications")

    # Drop columns
    if column_exists("vouchers", "status"):
        op.drop_column("vouchers", "status")

    if column_exists("users", "role"):
        op.drop_column("users", "role")
