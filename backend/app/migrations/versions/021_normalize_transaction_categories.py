"""Normalize transaction category names to match DB categories table.

Revision ID: 021_norm_tx_categories
Revises: 020_missing_categories
Create Date: 2026-03-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '021_norm_tx_categories'
down_revision: Union[str, None] = '020_missing_categories'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RENAMES = [
    ('Jedzenie', 'Spożywcze'),
    ('Odzież', 'Ubrania'),
    ('Zakupy', 'Inne'),
    ('Czynsz', 'Dom'),
    ('Opłaty bankowe', 'Rachunki'),
    ('Gotówka', 'Inne'),
]


def upgrade() -> None:
    connection = op.get_bind()
    for old_name, new_name in RENAMES:
        connection.execute(
            sa.text("UPDATE transactions SET category = :new WHERE category = :old"),
            {'new': new_name, 'old': old_name}
        )


def downgrade() -> None:
    connection = op.get_bind()
    for old_name, new_name in RENAMES:
        connection.execute(
            sa.text("UPDATE transactions SET category = :old WHERE category = :new"),
            {'old': old_name, 'new': new_name}
        )
