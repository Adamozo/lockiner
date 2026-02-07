"""Seed initial data.

This migration populates the database with default categories
and food categories required for the application to function.

Revision ID: 002_seed_data
Revises: 001_initial_schema
Create Date: 2026-02-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_seed_data'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert seed data for categories and food categories."""

    # =========================================================================
    # TRANSACTION/RECEIPT CATEGORIES
    # =========================================================================

    categories_table = sa.table(
        'categories',
        sa.column('name', sa.String),
        sa.column('icon', sa.String),
        sa.column('color', sa.String),
        sa.column('budget_limit', sa.Float),
    )

    default_categories = [
        {'name': 'Spożywcze', 'icon': 'i-heroicons-shopping-cart', 'color': '#22c55e', 'budget_limit': None},
        {'name': 'Transport', 'icon': 'i-heroicons-truck', 'color': '#3b82f6', 'budget_limit': None},
        {'name': 'Rozrywka', 'icon': 'i-heroicons-film', 'color': '#a855f7', 'budget_limit': None},
        {'name': 'Restauracje', 'icon': 'i-heroicons-cake', 'color': '#f97316', 'budget_limit': None},
        {'name': 'Zdrowie', 'icon': 'i-heroicons-heart', 'color': '#ef4444', 'budget_limit': None},
        {'name': 'Rachunki', 'icon': 'i-heroicons-document-text', 'color': '#eab308', 'budget_limit': None},
        {'name': 'Ubrania', 'icon': 'i-heroicons-shopping-bag', 'color': '#ec4899', 'budget_limit': None},
        {'name': 'Dom', 'icon': 'i-heroicons-home', 'color': '#14b8a6', 'budget_limit': None},
        {'name': 'Edukacja', 'icon': 'i-heroicons-academic-cap', 'color': '#6366f1', 'budget_limit': None},
        {'name': 'Subskrypcje', 'icon': 'i-heroicons-credit-card', 'color': '#8b5cf6', 'budget_limit': None},
        {'name': 'Paliwo', 'icon': 'i-heroicons-fire', 'color': '#f59e0b', 'budget_limit': None},
        {'name': 'Elektronika', 'icon': 'i-heroicons-computer-desktop', 'color': '#06b6d4', 'budget_limit': None},
        {'name': 'Prezenty', 'icon': 'i-heroicons-gift', 'color': '#f43f5e', 'budget_limit': None},
        {'name': 'Oszczędności', 'icon': 'i-heroicons-banknotes', 'color': '#10b981', 'budget_limit': None},
        {'name': 'Inne', 'icon': 'i-heroicons-ellipsis-horizontal-circle', 'color': '#6b7280', 'budget_limit': None},
    ]

    # Use INSERT ... ON CONFLICT DO NOTHING for idempotency
    connection = op.get_bind()
    for category in default_categories:
        # Check if category exists
        result = connection.execute(
            sa.text("SELECT id FROM categories WHERE name = :name"),
            {'name': category['name']}
        ).fetchone()
        if not result:
            op.execute(
                categories_table.insert().values(**category)
            )

    # =========================================================================
    # FOOD CATEGORIES
    # =========================================================================

    food_categories_table = sa.table(
        'food_categories',
        sa.column('name', sa.String),
        sa.column('icon', sa.String),
        sa.column('color', sa.String),
        sa.column('default_expiry_days', sa.Integer),
        sa.column('storage_tips', sa.Text),
    )

    default_food_categories = [
        {
            'name': 'Nabiał',
            'icon': 'i-heroicons-beaker',
            'color': '#fef3c7',
            'default_expiry_days': 7,
            'storage_tips': 'Przechowuj w lodówce w temperaturze 2-6°C'
        },
        {
            'name': 'Mięso',
            'icon': 'i-heroicons-fire',
            'color': '#fecaca',
            'default_expiry_days': 3,
            'storage_tips': 'Przechowuj w lodówce do 3 dni lub zamroź'
        },
        {
            'name': 'Ryby i owoce morza',
            'icon': 'i-heroicons-sparkles',
            'color': '#a5f3fc',
            'default_expiry_days': 2,
            'storage_tips': 'Spożyj jak najszybciej lub zamroź'
        },
        {
            'name': 'Warzywa',
            'icon': 'i-heroicons-leaf',
            'color': '#bbf7d0',
            'default_expiry_days': 7,
            'storage_tips': 'Większość warzyw przechowuj w lodówce'
        },
        {
            'name': 'Owoce',
            'icon': 'i-heroicons-sun',
            'color': '#fed7aa',
            'default_expiry_days': 5,
            'storage_tips': 'Niektóre owoce dojrzewają w temperaturze pokojowej'
        },
        {
            'name': 'Pieczywo',
            'icon': 'i-heroicons-cake',
            'color': '#fde68a',
            'default_expiry_days': 3,
            'storage_tips': 'Przechowuj w temperaturze pokojowej lub zamroź'
        },
        {
            'name': 'Mrożonki',
            'icon': 'i-heroicons-cube',
            'color': '#bfdbfe',
            'default_expiry_days': 90,
            'storage_tips': 'Przechowuj w zamrażarce w temperaturze -18°C'
        },
        {
            'name': 'Konserwy',
            'icon': 'i-heroicons-archive-box',
            'color': '#d1d5db',
            'default_expiry_days': 365,
            'storage_tips': 'Przechowuj w suchym, chłodnym miejscu'
        },
        {
            'name': 'Napoje',
            'icon': 'i-heroicons-beaker',
            'color': '#c7d2fe',
            'default_expiry_days': 30,
            'storage_tips': 'Po otwarciu przechowuj w lodówce'
        },
        {
            'name': 'Przekąski',
            'icon': 'i-heroicons-sparkles',
            'color': '#fbcfe8',
            'default_expiry_days': 30,
            'storage_tips': 'Przechowuj w suchym miejscu'
        },
        {
            'name': 'Przyprawy',
            'icon': 'i-heroicons-fire',
            'color': '#fca5a5',
            'default_expiry_days': 365,
            'storage_tips': 'Przechowuj w suchym, ciemnym miejscu'
        },
        {
            'name': 'Produkty suche',
            'icon': 'i-heroicons-square-3-stack-3d',
            'color': '#e5e7eb',
            'default_expiry_days': 180,
            'storage_tips': 'Przechowuj w szczelnych pojemnikach'
        },
        {
            'name': 'Słodycze',
            'icon': 'i-heroicons-heart',
            'color': '#f9a8d4',
            'default_expiry_days': 60,
            'storage_tips': 'Przechowuj w suchym, chłodnym miejscu'
        },
        {
            'name': 'Gotowe dania',
            'icon': 'i-heroicons-rectangle-stack',
            'color': '#fcd34d',
            'default_expiry_days': 3,
            'storage_tips': 'Przechowuj w lodówce, spożyj szybko'
        },
        {
            'name': 'Inne',
            'icon': 'i-heroicons-ellipsis-horizontal-circle',
            'color': '#9ca3af',
            'default_expiry_days': 14,
            'storage_tips': 'Sprawdź etykietę produktu'
        },
    ]

    for food_category in default_food_categories:
        result = connection.execute(
            sa.text("SELECT id FROM food_categories WHERE name = :name"),
            {'name': food_category['name']}
        ).fetchone()
        if not result:
            op.execute(
                food_categories_table.insert().values(**food_category)
            )


def downgrade() -> None:
    """Remove seed data."""
    # Remove food categories
    op.execute("DELETE FROM food_categories WHERE name IN ('Nabiał', 'Mięso', 'Ryby i owoce morza', 'Warzywa', 'Owoce', 'Pieczywo', 'Mrożonki', 'Konserwy', 'Napoje', 'Przekąski', 'Przyprawy', 'Produkty suche', 'Słodycze', 'Gotowe dania', 'Inne')")

    # Remove transaction categories
    op.execute("DELETE FROM categories WHERE name IN ('Spożywcze', 'Transport', 'Rozrywka', 'Restauracje', 'Zdrowie', 'Rachunki', 'Ubrania', 'Dom', 'Edukacja', 'Subskrypcje', 'Paliwo', 'Elektronika', 'Prezenty', 'Oszczędności', 'Inne')")
