"""
SQLAlchemy Models Package

This package contains all database models split into logical modules:
- base: Base class and utilities
- transaction: Transaction model
- receipt: Receipt model
- category: Category model
- monthly_import: MonthlyImport model
- budget: BudgetSettings model
- user: User, UserAPIKey, Voucher models
- household: Household, HouseholdMember, HouseholdInvitation models
- ownership: Junction tables for multi-tenant ownership
- food: Food module models
- fitness: Fitness module models
"""

from sqlalchemy import Index

# Base and utilities
from .base import Base, utc_now

# Core models
from .transaction import Transaction
from .receipt import Receipt
from .category import Category
from .monthly_import import MonthlyImport
from .budget import BudgetSettings

# User models
from .user import User, UserAPIKey, Voucher

# Household models
from .household import Household, HouseholdMember, HouseholdInvitation

# Ownership junction tables
from .ownership import (
    UserTransaction,
    HouseholdTransaction,
    UserReceipt,
    HouseholdReceipt,
    UserCategory,
    HouseholdCategory,
    UserBudgetSettings,
    HouseholdBudgetSettings,
)

# Food module models
from .food import (
    FoodCategory,
    FoodProduct,
    FoodProductAlias,
    FoodPendingImport,
    FoodPendingImportItem,
    FoodInventory,
    FoodExpiryReminder,
    FoodReminderSettings,
    FoodConsumptionLog,
)

# Notification models
from .notification import Notification, UserNotification, PushSubscription, NotificationSchedule

# Fitness module models
from .fitness import Workout, Exercise, ExerciseSet, WeightEntry


# ============================================================================
# Indexes
# ============================================================================

# Core model indexes
Index("idx_transactions_date", Transaction.date)
Index("idx_transactions_category", Transaction.category)
Index("idx_receipts_scan_date", Receipt.scan_date)
Index("idx_receipts_merchant", Receipt.merchant)
Index("idx_receipts_category", Receipt.category)
Index("idx_categories_name", Category.name)
Index("idx_monthly_imports_month", MonthlyImport.month)
Index("idx_users_email_hash", User.email_hash)
Index("idx_vouchers_code", Voucher.code)
Index("idx_vouchers_used_by", Voucher.used_by_user_id)
Index("idx_households_uid", Household.uid)
Index("idx_household_members_household", HouseholdMember.household_id)
Index("idx_household_members_user", HouseholdMember.user_id)
Index("idx_household_invitations_token", HouseholdInvitation.token)
Index("idx_household_invitations_household", HouseholdInvitation.household_id)

# Ownership junction table indexes
Index("idx_user_transactions_user", UserTransaction.user_id)
Index("idx_user_transactions_transaction", UserTransaction.transaction_id)
Index("idx_household_transactions_household", HouseholdTransaction.household_id)
Index("idx_household_transactions_transaction", HouseholdTransaction.transaction_id)
Index("idx_user_receipts_user", UserReceipt.user_id)
Index("idx_user_receipts_receipt", UserReceipt.receipt_id)
Index("idx_household_receipts_household", HouseholdReceipt.household_id)
Index("idx_household_receipts_receipt", HouseholdReceipt.receipt_id)
Index("idx_user_categories_user", UserCategory.user_id)
Index("idx_user_categories_category", UserCategory.category_id)
Index("idx_household_categories_household", HouseholdCategory.household_id)
Index("idx_household_categories_category", HouseholdCategory.category_id)
Index("idx_user_budget_settings_user", UserBudgetSettings.user_id)
Index("idx_user_budget_settings_budget", UserBudgetSettings.budget_settings_id)
Index("idx_household_budget_settings_household", HouseholdBudgetSettings.household_id)
Index("idx_household_budget_settings_budget", HouseholdBudgetSettings.budget_settings_id)
Index("idx_user_api_keys_user", UserAPIKey.user_id)
Index("idx_user_api_keys_user_provider", UserAPIKey.user_id, UserAPIKey.provider, unique=True)

# Food module indexes
Index("idx_food_categories_name", FoodCategory.name)
Index("idx_food_products_name_normalized", FoodProduct.name_normalized)
Index("idx_food_products_barcode", FoodProduct.barcode)
Index("idx_food_products_category", FoodProduct.food_category_id)
Index("idx_food_product_aliases_normalized", FoodProductAlias.alias_normalized)
Index("idx_food_product_aliases_product", FoodProductAlias.product_id)
Index("idx_food_pending_imports_user", FoodPendingImport.user_id)
Index("idx_food_pending_imports_household", FoodPendingImport.household_id)
Index("idx_food_pending_imports_receipt", FoodPendingImport.receipt_id)
Index("idx_food_pending_imports_status", FoodPendingImport.status)
Index("idx_food_pending_import_items_import", FoodPendingImportItem.pending_import_id)
Index("idx_food_pending_import_items_status", FoodPendingImportItem.status)
Index("idx_food_inventory_user", FoodInventory.user_id)
Index("idx_food_inventory_household", FoodInventory.household_id)
Index("idx_food_inventory_product", FoodInventory.product_id)
Index("idx_food_inventory_expiry", FoodInventory.expiry_date)
Index("idx_food_inventory_status", FoodInventory.status)
Index("idx_food_inventory_location", FoodInventory.location)
Index("idx_food_expiry_reminders_user", FoodExpiryReminder.user_id)
Index("idx_food_expiry_reminders_inventory", FoodExpiryReminder.inventory_item_id)
Index("idx_food_expiry_reminders_status", FoodExpiryReminder.status)
Index("idx_food_consumption_log_user", FoodConsumptionLog.user_id)
Index("idx_food_consumption_log_consumed_at", FoodConsumptionLog.consumed_at)

# Notification module indexes
Index("idx_user_notifications_user", UserNotification.user_id)
Index("idx_user_notifications_notification", UserNotification.notification_id)
Index("idx_push_subscriptions_user", PushSubscription.user_id)
Index("idx_notifications_created_by", Notification.created_by_user_id)
Index("idx_notification_schedules_user", NotificationSchedule.user_id)
Index("idx_notification_schedules_enabled", NotificationSchedule.enabled)

# Fitness module indexes
Index("idx_workouts_user", Workout.user_id)
Index("idx_workouts_date", Workout.date)
Index("idx_exercises_workout", Exercise.workout_id)
Index("idx_exercise_sets_exercise", ExerciseSet.exercise_id)
Index("idx_weight_entries_user", WeightEntry.user_id)
Index("idx_weight_entries_date", WeightEntry.date)


# Export all models
__all__ = [
    # Base
    "Base",
    "utc_now",
    # Core
    "Transaction",
    "Receipt",
    "Category",
    "MonthlyImport",
    "BudgetSettings",
    # User
    "User",
    "UserAPIKey",
    "Voucher",
    # Household
    "Household",
    "HouseholdMember",
    "HouseholdInvitation",
    # Ownership
    "UserTransaction",
    "HouseholdTransaction",
    "UserReceipt",
    "HouseholdReceipt",
    "UserCategory",
    "HouseholdCategory",
    "UserBudgetSettings",
    "HouseholdBudgetSettings",
    # Food
    "FoodCategory",
    "FoodProduct",
    "FoodProductAlias",
    "FoodPendingImport",
    "FoodPendingImportItem",
    "FoodInventory",
    "FoodExpiryReminder",
    "FoodReminderSettings",
    "FoodConsumptionLog",
    # Notification
    "Notification",
    "UserNotification",
    "PushSubscription",
    "NotificationSchedule",
    # Fitness
    "Workout",
    "Exercise",
    "ExerciseSet",
    "WeightEntry",
]
