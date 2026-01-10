from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    Text,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(String, nullable=False, index=True)  # ISO 8601: YYYY-MM-DD
    amount = Column(Float, nullable=False)
    description = Column(Text)
    category = Column(String, default="Inne", index=True)
    payment_method = Column(String, nullable=True) 
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    receipt = relationship("Receipt", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount}, category={self.category})>"


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_path = Column(String, nullable=False)
    scan_date = Column(String, nullable=False, index=True)  # ISO 8601: YYYY-MM-DD
    merchant = Column(String, index=True)
    total = Column(Float)
    payment_method = Column(String, nullable=True)  
    items_json = Column(Text) 
    raw_ocr_response = Column(Text) 
    verified = Column(Boolean, default=False)
    category = Column(String, ForeignKey("categories.name"), default="Inne", index=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    transactions = relationship("Transaction", back_populates="receipt")
    category_rel = relationship("Category", foreign_keys=[category])

    def __repr__(self):
        return f"<Receipt(id={self.id}, merchant={self.merchant}, total={self.total}, verified={self.verified})>"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    budget_limit = Column(Float, nullable=True)
    icon = Column(String)  
    color = Column(String)  

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, icon={self.icon})>"


class MonthlyImport(Base):
    __tablename__ = "monthly_imports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    month = Column(String, nullable=False, index=True)  # YYYY-MM format
    filename = Column(String)
    transactions_count = Column(Integer)
    imported_at = Column(String, default=lambda: utc_now().isoformat())

    def __repr__(self):
        return f"<MonthlyImport(id={self.id}, month={self.month}, count={self.transactions_count})>"


class BudgetSettings(Base):
    __tablename__ = "budget_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    overall_monthly_limit = Column(Float, nullable=True)  
    alert_threshold_warning = Column(Float, default=80.0) 
    alert_threshold_danger = Column(Float, default=100.0)  
    enable_alerts = Column(Boolean, default=True) 
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    def __repr__(self):
        return f"<BudgetSettings(id={self.id}, overall_limit={self.overall_monthly_limit}, alerts={self.enable_alerts})>"


class Voucher(Base):
    """Registration voucher - required for account creation."""
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)  # UUID string
    used_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    used_at = Column(String, nullable=True)  # ISO 8601 datetime
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    used_by = relationship("User", back_populates="voucher")

    def __repr__(self):
        return f"<Voucher(id={self.id}, code={self.code[:8]}..., used={self.used_by_user_id is not None})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email_hash = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    household_memberships = relationship("HouseholdMember", back_populates="user")
    api_keys = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    voucher = relationship("Voucher", back_populates="used_by", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class UserAPIKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<UserAPIKey(id={self.id}, user_id={self.user_id}, provider={self.provider})>"


class Household(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uid = Column(String, unique=True, nullable=False, index=True)  # UUID string
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    members = relationship("HouseholdMember", back_populates="household", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Household(id={self.id}, uid={self.uid}, name={self.name})>"


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default="member")  # manager, member
    status = Column(String, nullable=False, default="active")  # active, blocked
    joined_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household", back_populates="members")
    user = relationship("User", back_populates="household_memberships")

    def __repr__(self):
        return f"<HouseholdMember(id={self.id}, household_id={self.household_id}, user_id={self.user_id}, role={self.role})>"


class HouseholdInvitation(Base):
    __tablename__ = "household_invitations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)  # UUID string
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(String, nullable=True)  # ISO 8601 datetime, null = never expires
    max_uses = Column(Integer, nullable=True)  # null = unlimited
    uses_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household", backref="invitations")
    creator = relationship("User")

    def __repr__(self):
        return f"<HouseholdInvitation(id={self.id}, household_id={self.household_id}, token={self.token[:8]}...)>"


# ============================================================================
# Ownership Junction Tables
# ============================================================================

class UserTransaction(Base):
    __tablename__ = "user_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    transaction = relationship("Transaction")

    def __repr__(self):
        return f"<UserTransaction(user_id={self.user_id}, transaction_id={self.transaction_id})>"


class HouseholdTransaction(Base):
    __tablename__ = "household_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    added_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    transaction = relationship("Transaction")
    added_by = relationship("User")

    def __repr__(self):
        return f"<HouseholdTransaction(household_id={self.household_id}, transaction_id={self.transaction_id})>"


class UserReceipt(Base):
    __tablename__ = "user_receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    receipt = relationship("Receipt")

    def __repr__(self):
        return f"<UserReceipt(user_id={self.user_id}, receipt_id={self.receipt_id})>"


class HouseholdReceipt(Base):
    __tablename__ = "household_receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    added_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    receipt = relationship("Receipt")
    added_by = relationship("User")

    def __repr__(self):
        return f"<HouseholdReceipt(household_id={self.household_id}, receipt_id={self.receipt_id})>"


class UserCategory(Base):
    __tablename__ = "user_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    category = relationship("Category")

    def __repr__(self):
        return f"<UserCategory(user_id={self.user_id}, category_id={self.category_id})>"


class HouseholdCategory(Base):
    __tablename__ = "household_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    category = relationship("Category")

    def __repr__(self):
        return f"<HouseholdCategory(household_id={self.household_id}, category_id={self.category_id})>"


class UserBudgetSettings(Base):
    __tablename__ = "user_budget_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    budget_settings_id = Column(Integer, ForeignKey("budget_settings.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    budget_settings = relationship("BudgetSettings")

    def __repr__(self):
        return f"<UserBudgetSettings(user_id={self.user_id}, budget_settings_id={self.budget_settings_id})>"


class HouseholdBudgetSettings(Base):
    __tablename__ = "household_budget_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    budget_settings_id = Column(Integer, ForeignKey("budget_settings.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    budget_settings = relationship("BudgetSettings")

    def __repr__(self):
        return f"<HouseholdBudgetSettings(household_id={self.household_id}, budget_settings_id={self.budget_settings_id})>"


# ============================================================================
# Food Module Models
# ============================================================================

class FoodCategory(Base):
    """Food categories for organizing products (e.g., Dairy, Meat, Vegetables)."""
    __tablename__ = "food_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    default_expiry_days = Column(Integer, nullable=True)
    storage_tips = Column(Text, nullable=True)

    # Relationships
    products = relationship("FoodProduct", back_populates="food_category")

    def __repr__(self):
        return f"<FoodCategory(id={self.id}, name={self.name})>"


class FoodProduct(Base):
    """Global product catalog for food items."""
    __tablename__ = "food_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    name_normalized = Column(String, nullable=False, index=True)
    barcode = Column(String, nullable=True, index=True)
    barcode_type = Column(String, nullable=True)  # EAN-13, UPC-A, etc.
    food_category_id = Column(Integer, ForeignKey("food_categories.id", ondelete="SET NULL"), nullable=True)

    # Nutritional information (per 100g)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)

    default_unit = Column(String, default="szt")  # szt, kg, g, l, ml
    is_verified = Column(Boolean, default=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    food_category = relationship("FoodCategory", back_populates="products")
    created_by = relationship("User")
    aliases = relationship("FoodProductAlias", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FoodProduct(id={self.id}, name={self.name})>"


class FoodProductAlias(Base):
    """Aliases for food products (OCR name mappings)."""
    __tablename__ = "food_product_aliases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("food_products.id", ondelete="CASCADE"), nullable=False)
    alias = Column(String, nullable=False)
    alias_normalized = Column(String, nullable=False, index=True)
    source = Column(String, default="manual")  # manual, ocr, user_correction
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    product = relationship("FoodProduct", back_populates="aliases")
    created_by = relationship("User")

    def __repr__(self):
        return f"<FoodProductAlias(id={self.id}, alias={self.alias})>"


class FoodPendingImport(Base):
    """Pending food imports from receipts."""
    __tablename__ = "food_pending_imports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=True)
    status = Column(String, default="pending")  # pending, partially_accepted, accepted, rejected
    created_at = Column(String, default=lambda: utc_now().isoformat())
    processed_at = Column(String, nullable=True)

    # Relationships
    receipt = relationship("Receipt")
    user = relationship("User")
    household = relationship("Household")
    items = relationship("FoodPendingImportItem", back_populates="pending_import", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FoodPendingImport(id={self.id}, receipt_id={self.receipt_id}, status={self.status})>"


class FoodPendingImportItem(Base):
    """Individual items in a pending food import."""
    __tablename__ = "food_pending_import_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pending_import_id = Column(Integer, ForeignKey("food_pending_imports.id", ondelete="CASCADE"), nullable=False)
    original_name = Column(String, nullable=False)
    original_name_normalized = Column(String, nullable=False)
    quantity = Column(Float, default=1)
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)

    # Matching info
    matched_product_id = Column(Integer, ForeignKey("food_products.id", ondelete="SET NULL"), nullable=True)
    match_method = Column(String, nullable=True)  # exact_name, alias, barcode, ai_suggestion
    match_confidence = Column(Float, nullable=True)  # 0.0 - 1.0

    # AI suggestions
    ai_suggested_name = Column(String, nullable=True)
    ai_suggested_category_id = Column(Integer, ForeignKey("food_categories.id", ondelete="SET NULL"), nullable=True)
    ai_suggested_expiry_days = Column(Integer, nullable=True)
    suggested_expiry_date = Column(String, nullable=True)

    # Final values after user decision
    status = Column(String, default="pending")  # pending, accepted, rejected, skipped
    final_product_id = Column(Integer, ForeignKey("food_products.id", ondelete="SET NULL"), nullable=True)
    final_expiry_date = Column(String, nullable=True)
    final_quantity = Column(Float, nullable=True)
    final_unit = Column(String, nullable=True)
    created_new_product = Column(Boolean, default=False)
    processed_at = Column(String, nullable=True)

    # Relationships
    pending_import = relationship("FoodPendingImport", back_populates="items")
    matched_product = relationship("FoodProduct", foreign_keys=[matched_product_id])
    final_product = relationship("FoodProduct", foreign_keys=[final_product_id])
    ai_suggested_category = relationship("FoodCategory")

    def __repr__(self):
        return f"<FoodPendingImportItem(id={self.id}, original_name={self.original_name}, status={self.status})>"


class FoodInventory(Base):
    """User/household food inventory (fridge, pantry, freezer)."""
    __tablename__ = "food_inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=True)
    product_id = Column(Integer, ForeignKey("food_products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Float, default=1)
    unit = Column(String, default="szt")

    purchase_date = Column(String, nullable=True)
    expiry_date = Column(String, nullable=True)
    opened_date = Column(String, nullable=True)

    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="SET NULL"), nullable=True)
    pending_import_item_id = Column(Integer, ForeignKey("food_pending_import_items.id", ondelete="SET NULL"), nullable=True)
    added_manually = Column(Boolean, default=False)

    status = Column(String, default="available")  # available, opened, consumed, expired, thrown_away
    location = Column(String, default="pantry")  # fridge, freezer, pantry
    notes = Column(Text, nullable=True)

    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")
    household = relationship("Household")
    product = relationship("FoodProduct")
    receipt = relationship("Receipt")
    pending_import_item = relationship("FoodPendingImportItem")
    reminders = relationship("FoodExpiryReminder", back_populates="inventory_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FoodInventory(id={self.id}, product_id={self.product_id}, status={self.status})>"


class FoodExpiryReminder(Base):
    """Reminders for expiring food items."""
    __tablename__ = "food_expiry_reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("food_inventory.id", ondelete="CASCADE"), nullable=False)
    remind_at = Column(String, nullable=False)
    days_before_expiry = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, sent, dismissed
    sent_at = Column(String, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    inventory_item = relationship("FoodInventory", back_populates="reminders")

    def __repr__(self):
        return f"<FoodExpiryReminder(id={self.id}, inventory_item_id={self.inventory_item_id}, status={self.status})>"


class FoodReminderSettings(Base):
    """User settings for food expiry reminders."""
    __tablename__ = "food_reminder_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    enabled = Column(Boolean, default=True)
    default_days_before = Column(Integer, default=3)
    dairy_days_before = Column(Integer, default=2)
    meat_days_before = Column(Integer, default=1)
    vegetables_days_before = Column(Integer, default=2)
    fruits_days_before = Column(Integer, default=2)
    bread_days_before = Column(Integer, default=1)
    frozen_days_before = Column(Integer, default=7)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<FoodReminderSettings(id={self.id}, user_id={self.user_id}, enabled={self.enabled})>"


class FoodConsumptionLog(Base):
    """Log of consumed food items (for fitness/nutrition tracking)."""
    __tablename__ = "food_consumption_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("food_products.id", ondelete="SET NULL"), nullable=True)
    inventory_item_id = Column(Integer, ForeignKey("food_inventory.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Float, default=1)
    unit = Column(String, default="szt")

    # Nutritional info at time of consumption
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)

    consumed_at = Column(String, nullable=False)
    meal_type = Column(String, nullable=True)  # breakfast, lunch, dinner, snack
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    product = relationship("FoodProduct")
    inventory_item = relationship("FoodInventory")

    def __repr__(self):
        return f"<FoodConsumptionLog(id={self.id}, user_id={self.user_id}, consumed_at={self.consumed_at})>"


# ============================================================================
# Indexes
# ============================================================================

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
