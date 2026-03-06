"""Add missing finance categories: Przychody, Zakupy Online, Zwierzęta.

Revision ID: 020_missing_categories
Revises: 019_oauth_device_codes
Create Date: 2026-03-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '020_missing_categories'
down_revision: Union[str, None] = '019_oauth_device_codes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    categories_table = sa.table(
        'categories',
        sa.column('name', sa.String),
        sa.column('icon', sa.String),
        sa.column('color', sa.String),
        sa.column('budget_limit', sa.Float),
    )

    new_categories = [
        {'name': 'Przychody', 'icon': 'i-heroicons-arrow-trending-up', 'color': '#00FF87', 'budget_limit': None},
        {'name': 'Zakupy Online', 'icon': 'i-heroicons-shopping-cart', 'color': '#F97316', 'budget_limit': None},
        {'name': 'Zwierzęta', 'icon': 'i-heroicons-heart', 'color': '#EC4899', 'budget_limit': None},
    ]

    connection = op.get_bind()
    for category in new_categories:
        result = connection.execute(
            sa.text("SELECT id FROM categories WHERE name = :name"),
            {'name': category['name']}
        ).fetchone()
        if not result:
            op.execute(
                categories_table.insert().values(**category)
            )


def downgrade() -> None:
    connection = op.get_bind()
    for name in ('Przychody', 'Zakupy Online', 'Zwierzęta'):
        connection.execute(
            sa.text("DELETE FROM categories WHERE name = :name"),
            {'name': name}
        )
