"""Food Module Models."""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, utc_now


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


class FoodRecipe(Base):
    """User's recipe collection."""
    __tablename__ = "food_recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    servings = Column(Integer, nullable=True)
    instructions = Column(Text, nullable=True)  # JSON list of steps
    tags = Column(String, nullable=True)  # comma-separated
    rating = Column(Integer, nullable=True)  # 1-5
    source = Column(String, nullable=False, default="manual")  # manual | saved_from_ai
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")
    ingredients = relationship("FoodRecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FoodRecipe(id={self.id}, name={self.name}, user_id={self.user_id})>"


class FoodRecipeIngredient(Base):
    """Ingredient in a recipe, optionally linked to a FoodProduct."""
    __tablename__ = "food_recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("food_recipes.id", ondelete="CASCADE"), nullable=False)
    food_product_id = Column(Integer, ForeignKey("food_products.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)  # always present (AI doesn't know product IDs)
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)

    # Relationships
    recipe = relationship("FoodRecipe", back_populates="ingredients")
    food_product = relationship("FoodProduct")

    def __repr__(self):
        return f"<FoodRecipeIngredient(id={self.id}, name={self.name}, recipe_id={self.recipe_id})>"


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
