"""Add oauth_device_codes table for Device Authorization Grant (RFC 8628).

Revision ID: 019_oauth_device_codes
Revises: 018_receipt_multi_images
Create Date: 2026-03-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '019_oauth_device_codes'
down_revision: Union[str, None] = '018_receipt_multi_images'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    if not conn.execute(sa.text("SELECT 1 FROM information_schema.tables WHERE table_name='oauth_device_codes'")).scalar():
        op.create_table(
            'oauth_device_codes',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('device_code', sa.String(length=256), nullable=False),
            sa.Column('user_code', sa.String(length=20), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
            sa.Column('expires_at', sa.String(), nullable=False),
            sa.Column('created_at', sa.String(), nullable=True),
            sa.ForeignKeyConstraint(['client_id'], ['oauth_clients.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_oauth_device_codes_device_code ON oauth_device_codes (device_code)"))
        conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_oauth_device_codes_user_code ON oauth_device_codes (user_code)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_device_codes_device ON oauth_device_codes (device_code)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_device_codes_user_code ON oauth_device_codes (user_code)"))


def downgrade() -> None:
    op.drop_table('oauth_device_codes')
