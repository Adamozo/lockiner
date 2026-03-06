"""Add food_recipes and food_recipe_ingredients tables.

Revision ID: 022_food_recipes
Revises: 021_norm_tx_categories
Create Date: 2026-03-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '022_food_recipes'
down_revision: Union[str, None] = '021_norm_tx_categories'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'food_recipes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prep_time_minutes', sa.Integer(), nullable=True),
        sa.Column('servings', sa.Integer(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True),
    )
    op.create_index('idx_food_recipes_user', 'food_recipes', ['user_id'])

    op.create_table(
        'food_recipe_ingredients',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('recipe_id', sa.Integer(), sa.ForeignKey('food_recipes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('food_product_id', sa.Integer(), sa.ForeignKey('food_products.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
    )
    op.create_index('idx_food_recipe_ingredients_recipe', 'food_recipe_ingredients', ['recipe_id'])
    op.create_index('idx_food_recipe_ingredients_product', 'food_recipe_ingredients', ['food_product_id'])


def downgrade() -> None:
    op.drop_table('food_recipe_ingredients')
    op.drop_table('food_recipes')
