"""Initial schema baseline.

This migration represents the initial database schema.
All tables are created with proper relationships and constraints.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table already exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Create all tables if they don't exist (baseline migration)."""

    # =========================================================================
    # CORE TABLES
    # =========================================================================

    if not table_exists('users'):
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('email_hash', sa.String(), unique=True, nullable=False, index=True),
            sa.Column('password_hash', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    if not table_exists('vouchers'):
        op.create_table(
            'vouchers',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('code', sa.String(), unique=True, nullable=False, index=True),
            sa.Column('used_by_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('used_at', sa.String(), nullable=True),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('user_api_keys'):
        op.create_table(
            'user_api_keys',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('provider', sa.String(50), nullable=False),
            sa.Column('encrypted_key', sa.Text(), nullable=False),
            sa.Column('is_active', sa.Boolean(), default=False),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    if not table_exists('categories'):
        op.create_table(
            'categories',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('name', sa.String(), unique=True, nullable=False, index=True),
            sa.Column('budget_limit', sa.Float(), nullable=True),
            sa.Column('icon', sa.String()),
            sa.Column('color', sa.String()),
        )

    if not table_exists('receipts'):
        op.create_table(
            'receipts',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('image_path', sa.String(), nullable=False),
            sa.Column('scan_date', sa.String(), nullable=False, index=True),
            sa.Column('merchant', sa.String(), index=True),
            sa.Column('total', sa.Float()),
            sa.Column('payment_method', sa.String(), nullable=True),
            sa.Column('items_json', sa.Text()),
            sa.Column('raw_ocr_response', sa.Text()),
            sa.Column('verified', sa.Boolean(), default=False),
            sa.Column('category', sa.String(), sa.ForeignKey('categories.name', ondelete='SET NULL'), nullable=True, index=True),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('transactions'):
        op.create_table(
            'transactions',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('date', sa.String(), nullable=False, index=True),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('category', sa.String(), default='Inne', index=True),
            sa.Column('payment_method', sa.String(), nullable=True),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('receipts.id', ondelete='SET NULL'), nullable=True),
            sa.Column('notes', sa.Text()),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('monthly_imports'):
        op.create_table(
            'monthly_imports',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('month', sa.String(), nullable=False, index=True),
            sa.Column('filename', sa.String()),
            sa.Column('transactions_count', sa.Integer()),
            sa.Column('imported_at', sa.String()),
        )

    if not table_exists('budget_settings'):
        op.create_table(
            'budget_settings',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('overall_monthly_limit', sa.Float(), nullable=True),
            sa.Column('alert_threshold_warning', sa.Float(), default=80.0),
            sa.Column('alert_threshold_danger', sa.Float(), default=100.0),
            sa.Column('enable_alerts', sa.Boolean(), default=True),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    # =========================================================================
    # HOUSEHOLD TABLES
    # =========================================================================

    if not table_exists('households'):
        op.create_table(
            'households',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('uid', sa.String(), unique=True, nullable=False, index=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('icon', sa.String(), nullable=True),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    if not table_exists('household_members'):
        op.create_table(
            'household_members',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('role', sa.String(), nullable=False, default='member'),
            sa.Column('status', sa.String(), nullable=False, default='active'),
            sa.Column('joined_at', sa.String()),
        )

    if not table_exists('household_invitations'):
        op.create_table(
            'household_invitations',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=False),
            sa.Column('token', sa.String(), unique=True, nullable=False, index=True),
            sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('expires_at', sa.String(), nullable=True),
            sa.Column('max_uses', sa.Integer(), nullable=True),
            sa.Column('uses_count', sa.Integer(), default=0),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('created_at', sa.String()),
        )

    # =========================================================================
    # OWNERSHIP JUNCTION TABLES
    # =========================================================================

    if not table_exists('user_transactions'):
        op.create_table(
            'user_transactions',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('transaction_id', sa.Integer(), sa.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('household_transactions'):
        op.create_table(
            'household_transactions',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=False),
            sa.Column('transaction_id', sa.Integer(), sa.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False),
            sa.Column('added_by_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('user_receipts'):
        op.create_table(
            'user_receipts',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('receipts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('household_receipts'):
        op.create_table(
            'household_receipts',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=False),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('receipts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('added_by_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('user_categories'):
        op.create_table(
            'user_categories',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('household_categories'):
        op.create_table(
            'household_categories',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=False),
            sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('user_budget_settings'):
        op.create_table(
            'user_budget_settings',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('budget_settings_id', sa.Integer(), sa.ForeignKey('budget_settings.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('household_budget_settings'):
        op.create_table(
            'household_budget_settings',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=False),
            sa.Column('budget_settings_id', sa.Integer(), sa.ForeignKey('budget_settings.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String()),
        )

    # =========================================================================
    # FOOD MODULE TABLES
    # =========================================================================

    if not table_exists('food_categories'):
        op.create_table(
            'food_categories',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('name', sa.String(), unique=True, nullable=False, index=True),
            sa.Column('icon', sa.String(), nullable=True),
            sa.Column('color', sa.String(), nullable=True),
            sa.Column('default_expiry_days', sa.Integer(), nullable=True),
            sa.Column('storage_tips', sa.Text(), nullable=True),
        )

    if not table_exists('food_products'):
        op.create_table(
            'food_products',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('name_normalized', sa.String(), nullable=False, index=True),
            sa.Column('barcode', sa.String(), nullable=True, index=True),
            sa.Column('barcode_type', sa.String(), nullable=True),
            sa.Column('food_category_id', sa.Integer(), sa.ForeignKey('food_categories.id', ondelete='SET NULL'), nullable=True),
            sa.Column('calories', sa.Float(), nullable=True),
            sa.Column('protein', sa.Float(), nullable=True),
            sa.Column('carbohydrates', sa.Float(), nullable=True),
            sa.Column('fat', sa.Float(), nullable=True),
            sa.Column('fiber', sa.Float(), nullable=True),
            sa.Column('sugar', sa.Float(), nullable=True),
            sa.Column('sodium', sa.Float(), nullable=True),
            sa.Column('default_unit', sa.String(), default='szt'),
            sa.Column('is_verified', sa.Boolean(), default=False),
            sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    if not table_exists('food_product_aliases'):
        op.create_table(
            'food_product_aliases',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('food_products.id', ondelete='CASCADE'), nullable=False),
            sa.Column('alias', sa.String(), nullable=False),
            sa.Column('alias_normalized', sa.String(), nullable=False, index=True),
            sa.Column('source', sa.String(), default='manual'),
            sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('food_pending_imports'):
        op.create_table(
            'food_pending_imports',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('receipts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=True),
            sa.Column('status', sa.String(), default='pending'),
            sa.Column('created_at', sa.String()),
            sa.Column('processed_at', sa.String(), nullable=True),
        )

    if not table_exists('food_pending_import_items'):
        op.create_table(
            'food_pending_import_items',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('pending_import_id', sa.Integer(), sa.ForeignKey('food_pending_imports.id', ondelete='CASCADE'), nullable=False),
            sa.Column('original_name', sa.String(), nullable=False),
            sa.Column('original_name_normalized', sa.String(), nullable=False),
            sa.Column('quantity', sa.Float(), default=1),
            sa.Column('unit_price', sa.Float(), nullable=True),
            sa.Column('total_price', sa.Float(), nullable=True),
            sa.Column('matched_product_id', sa.Integer(), sa.ForeignKey('food_products.id', ondelete='SET NULL'), nullable=True),
            sa.Column('match_method', sa.String(), nullable=True),
            sa.Column('match_confidence', sa.Float(), nullable=True),
            sa.Column('ai_suggested_name', sa.String(), nullable=True),
            sa.Column('ai_suggested_category_id', sa.Integer(), sa.ForeignKey('food_categories.id', ondelete='SET NULL'), nullable=True),
            sa.Column('ai_suggested_expiry_days', sa.Integer(), nullable=True),
            sa.Column('suggested_expiry_date', sa.String(), nullable=True),
            sa.Column('status', sa.String(), default='pending'),
            sa.Column('final_product_id', sa.Integer(), sa.ForeignKey('food_products.id', ondelete='SET NULL'), nullable=True),
            sa.Column('final_expiry_date', sa.String(), nullable=True),
            sa.Column('final_quantity', sa.Float(), nullable=True),
            sa.Column('final_unit', sa.String(), nullable=True),
            sa.Column('created_new_product', sa.Boolean(), default=False),
            sa.Column('processed_at', sa.String(), nullable=True),
        )

    if not table_exists('food_inventory'):
        op.create_table(
            'food_inventory',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('household_id', sa.Integer(), sa.ForeignKey('households.id', ondelete='CASCADE'), nullable=True),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('food_products.id', ondelete='CASCADE'), nullable=False),
            sa.Column('quantity', sa.Float(), default=1),
            sa.Column('unit', sa.String(), default='szt'),
            sa.Column('purchase_date', sa.String(), nullable=True),
            sa.Column('expiry_date', sa.String(), nullable=True),
            sa.Column('opened_date', sa.String(), nullable=True),
            sa.Column('receipt_id', sa.Integer(), sa.ForeignKey('receipts.id', ondelete='SET NULL'), nullable=True),
            sa.Column('pending_import_item_id', sa.Integer(), sa.ForeignKey('food_pending_import_items.id', ondelete='SET NULL'), nullable=True),
            sa.Column('added_manually', sa.Boolean(), default=False),
            sa.Column('status', sa.String(), default='available'),
            sa.Column('location', sa.String(), default='pantry'),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    if not table_exists('food_expiry_reminders'):
        op.create_table(
            'food_expiry_reminders',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('inventory_item_id', sa.Integer(), sa.ForeignKey('food_inventory.id', ondelete='CASCADE'), nullable=False),
            sa.Column('remind_at', sa.String(), nullable=False),
            sa.Column('days_before_expiry', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(), default='pending'),
            sa.Column('sent_at', sa.String(), nullable=True),
            sa.Column('created_at', sa.String()),
        )

    if not table_exists('food_reminder_settings'):
        op.create_table(
            'food_reminder_settings',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
            sa.Column('enabled', sa.Boolean(), default=True),
            sa.Column('default_days_before', sa.Integer(), default=3),
            sa.Column('dairy_days_before', sa.Integer(), default=2),
            sa.Column('meat_days_before', sa.Integer(), default=1),
            sa.Column('vegetables_days_before', sa.Integer(), default=2),
            sa.Column('fruits_days_before', sa.Integer(), default=2),
            sa.Column('bread_days_before', sa.Integer(), default=1),
            sa.Column('frozen_days_before', sa.Integer(), default=7),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    if not table_exists('food_consumption_log'):
        op.create_table(
            'food_consumption_log',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('food_products.id', ondelete='SET NULL'), nullable=True),
            sa.Column('inventory_item_id', sa.Integer(), sa.ForeignKey('food_inventory.id', ondelete='SET NULL'), nullable=True),
            sa.Column('quantity', sa.Float(), default=1),
            sa.Column('unit', sa.String(), default='szt'),
            sa.Column('calories', sa.Float(), nullable=True),
            sa.Column('protein', sa.Float(), nullable=True),
            sa.Column('carbohydrates', sa.Float(), nullable=True),
            sa.Column('fat', sa.Float(), nullable=True),
            sa.Column('consumed_at', sa.String(), nullable=False),
            sa.Column('meal_type', sa.String(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.String()),
        )

    # =========================================================================
    # FITNESS MODULE TABLES
    # =========================================================================

    if not table_exists('workouts'):
        op.create_table(
            'workouts',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('date', sa.String(), nullable=False, index=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('duration_minutes', sa.Integer(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('completed', sa.Boolean(), default=True),
            sa.Column('created_at', sa.String()),
            sa.Column('updated_at', sa.String(), nullable=True),
        )

    if not table_exists('exercises'):
        op.create_table(
            'exercises',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('workout_id', sa.Integer(), sa.ForeignKey('workouts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('sets', sa.Integer(), nullable=False),
            sa.Column('reps', sa.Integer(), nullable=False),
            sa.Column('weight_kg', sa.Float(), nullable=False),
            sa.Column('rest_seconds', sa.Integer(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
        )

    if not table_exists('weight_entries'):
        op.create_table(
            'weight_entries',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('date', sa.String(), nullable=False, index=True),
            sa.Column('weight_kg', sa.Float(), nullable=False),
            sa.Column('body_fat_percentage', sa.Float(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.String()),
        )


def downgrade() -> None:
    """Drop all tables in reverse order."""
    # Fitness
    op.drop_table('weight_entries')
    op.drop_table('exercises')
    op.drop_table('workouts')

    # Food
    op.drop_table('food_consumption_log')
    op.drop_table('food_reminder_settings')
    op.drop_table('food_expiry_reminders')
    op.drop_table('food_inventory')
    op.drop_table('food_pending_import_items')
    op.drop_table('food_pending_imports')
    op.drop_table('food_product_aliases')
    op.drop_table('food_products')
    op.drop_table('food_categories')

    # Ownership
    op.drop_table('household_budget_settings')
    op.drop_table('user_budget_settings')
    op.drop_table('household_categories')
    op.drop_table('user_categories')
    op.drop_table('household_receipts')
    op.drop_table('user_receipts')
    op.drop_table('household_transactions')
    op.drop_table('user_transactions')

    # Household
    op.drop_table('household_invitations')
    op.drop_table('household_members')
    op.drop_table('households')

    # Core
    op.drop_table('budget_settings')
    op.drop_table('monthly_imports')
    op.drop_table('transactions')
    op.drop_table('receipts')
    op.drop_table('categories')
    op.drop_table('user_api_keys')
    op.drop_table('vouchers')
    op.drop_table('users')
