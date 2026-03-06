"""add oauth tables

Revision ID: fbc51d6de763
Revises: 017_user_language
Create Date: 2026-03-02 16:12:07.820713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbc51d6de763'
down_revision: Union[str, None] = '017_user_language'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # OAuth clients
    if not conn.execute(sa.text("SELECT 1 FROM information_schema.tables WHERE table_name='oauth_clients'")).scalar():
        op.create_table('oauth_clients',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('client_id', sa.String(length=100), nullable=False),
            sa.Column('client_name', sa.String(length=100), nullable=False),
            sa.Column('redirect_uris', sa.Text(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_clients_client_id ON oauth_clients (client_id)"))
        conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_oauth_clients_client_id ON oauth_clients (client_id)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_oauth_clients_id ON oauth_clients (id)"))

    # OAuth access tokens
    if not conn.execute(sa.text("SELECT 1 FROM information_schema.tables WHERE table_name='oauth_access_tokens'")).scalar():
        op.create_table('oauth_access_tokens',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('access_token', sa.String(length=256), nullable=False),
            sa.Column('refresh_token', sa.String(length=256), nullable=True),
            sa.Column('client_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('expires_at', sa.String(), nullable=False),
            sa.Column('refresh_token_expires_at', sa.String(), nullable=True),
            sa.Column('revoked', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.String(), nullable=True),
            sa.ForeignKeyConstraint(['client_id'], ['oauth_clients.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_tokens_access ON oauth_access_tokens (access_token)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_tokens_refresh ON oauth_access_tokens (refresh_token)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_tokens_user ON oauth_access_tokens (user_id)"))
        conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_oauth_access_tokens_access_token ON oauth_access_tokens (access_token)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_oauth_access_tokens_id ON oauth_access_tokens (id)"))
        conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_oauth_access_tokens_refresh_token ON oauth_access_tokens (refresh_token)"))

    # OAuth authorization codes
    if not conn.execute(sa.text("SELECT 1 FROM information_schema.tables WHERE table_name='oauth_authorization_codes'")).scalar():
        op.create_table('oauth_authorization_codes',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('code', sa.String(length=128), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('code_challenge', sa.String(length=128), nullable=False),
            sa.Column('code_challenge_method', sa.String(length=10), nullable=False),
            sa.Column('redirect_uri', sa.String(length=500), nullable=False),
            sa.Column('expires_at', sa.String(), nullable=False),
            sa.Column('used', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.String(), nullable=True),
            sa.ForeignKeyConstraint(['client_id'], ['oauth_clients.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_codes_client ON oauth_authorization_codes (client_id)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_oauth_codes_code ON oauth_authorization_codes (code)"))
        conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_oauth_authorization_codes_code ON oauth_authorization_codes (code)"))
        conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_oauth_authorization_codes_id ON oauth_authorization_codes (id)"))


def downgrade() -> None:
    op.drop_table('oauth_authorization_codes')
    op.drop_table('oauth_access_tokens')
    op.drop_table('oauth_clients')
