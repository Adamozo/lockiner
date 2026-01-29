"""Food module schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# Food Categories
class FoodCategoryBase(BaseModel):
    """Base schema for food category data."""
    name: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = None
    color: Optional[str] = None
    default_expiry_days: Optional[int] = Field(None, ge=1)
    storage_tips: Optional[str] = None


class FoodCategoryCreate(FoodCategoryBase):
    """Schema for creating a food category."""
    pass


class FoodCategoryResponse(FoodCategoryBase):
    """Schema for food category response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# Food Products
class FoodProductBase(BaseModel):
    """Base schema for food product data."""
    name: str = Field(..., min_length=1, max_length=255)
    barcode: Optional[str] = None
    barcode_type: Optional[str] = None
    food_category_id: Optional[int] = None
    calories: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    carbohydrates: Optional[float] = Field(None, ge=0)
    fat: Optional[float] = Field(None, ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sugar: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    default_unit: str = Field(default="szt")


class FoodProductCreate(FoodProductBase):
    """Schema for creating a food product."""
    pass


class FoodProductUpdate(BaseModel):
    """Schema for updating a food product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    barcode: Optional[str] = None
    barcode_type: Optional[str] = None
    food_category_id: Optional[int] = None
    calories: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    carbohydrates: Optional[float] = Field(None, ge=0)
    fat: Optional[float] = Field(None, ge=0)
    fiber: Optional[float] = Field(None, ge=0)
    sugar: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    default_unit: Optional[str] = None


class FoodProductResponse(FoodProductBase):
    """Schema for food product response."""
    id: int
    name_normalized: str
    is_verified: bool
    created_at: str
    updated_at: Optional[str] = None
    food_category: Optional[FoodCategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Product Aliases
class FoodProductAliasCreate(BaseModel):
    """Schema for creating a product alias."""
    product_id: int
    alias: str = Field(..., min_length=1, max_length=255)
    source: str = Field(default="manual")


class FoodProductAliasResponse(BaseModel):
    """Schema for product alias response."""
    id: int
    product_id: int
    alias: str
    alias_normalized: str
    source: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Pending Imports
class FoodPendingImportItemResponse(BaseModel):
    """Schema for pending import item response."""
    id: int
    original_name: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    matched_product_id: Optional[int] = None
    matched_product: Optional[FoodProductResponse] = None
    match_method: Optional[str] = None
    match_confidence: Optional[float] = None
    ai_suggested_name: Optional[str] = None
    ai_suggested_category_id: Optional[int] = None
    ai_suggested_expiry_days: Optional[int] = None
    suggested_expiry_date: Optional[str] = None
    status: str
    final_product_id: Optional[int] = None
    final_expiry_date: Optional[str] = None
    final_quantity: Optional[float] = None
    final_unit: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FoodPendingImportResponse(BaseModel):
    """Schema for pending import response."""
    id: int
    receipt_id: int
    user_id: int
    household_id: Optional[int] = None
    status: str
    created_at: str
    processed_at: Optional[str] = None
    items: List[FoodPendingImportItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class FoodPendingImportItemAccept(BaseModel):
    """Schema for accepting a pending import item."""
    final_product_id: Optional[int] = None  # If None, create new product
    final_expiry_date: Optional[str] = None
    final_quantity: Optional[float] = Field(None, gt=0)
    final_unit: Optional[str] = None
    # For creating new product if final_product_id is None
    new_product_name: Optional[str] = None
    new_product_category_id: Optional[int] = None


class FoodPendingImportItemBulkAccept(BaseModel):
    """Schema for bulk accepting pending import items."""
    item_decisions: List[dict] = Field(
        ...,
        description="List of {item_id, accept: bool, data: FoodPendingImportItemAccept}"
    )


# Inventory
class FoodInventoryCreate(BaseModel):
    """Schema for adding item to inventory."""
    product_id: int
    quantity: float = Field(default=1, gt=0)
    unit: str = Field(default="szt")
    expiry_date: Optional[str] = None
    purchase_date: Optional[str] = None
    location: str = Field(default="pantry")  # fridge, freezer, pantry
    notes: Optional[str] = None


class FoodInventoryUpdate(BaseModel):
    """Schema for updating inventory item."""
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    expiry_date: Optional[str] = None
    opened_date: Optional[str] = None
    status: Optional[str] = None  # available, opened, consumed, expired, thrown_away
    location: Optional[str] = None  # fridge, freezer, pantry
    notes: Optional[str] = None


class FoodInventoryResponse(BaseModel):
    """Schema for inventory item response."""
    id: int
    user_id: int
    household_id: Optional[int] = None
    product_id: int
    product: FoodProductResponse
    quantity: float
    unit: str
    purchase_date: Optional[str] = None
    expiry_date: Optional[str] = None
    opened_date: Optional[str] = None
    status: str
    location: str
    notes: Optional[str] = None
    added_manually: bool
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FoodInventoryConsumeRequest(BaseModel):
    """Schema for consuming inventory item."""
    quantity: Optional[float] = Field(None, gt=0, description="Amount to consume. If None, consume all.")
    meal_type: Optional[str] = None  # breakfast, lunch, dinner, snack
    notes: Optional[str] = None


# Expiry Reminders
class FoodExpiryReminderResponse(BaseModel):
    """Schema for expiry reminder response."""
    id: int
    user_id: int
    inventory_item_id: int
    inventory_item: Optional[FoodInventoryResponse] = None
    remind_at: str
    days_before_expiry: int
    status: str
    sent_at: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Reminder Settings
class FoodReminderSettingsBase(BaseModel):
    """Base schema for reminder settings."""
    enabled: bool = True
    default_days_before: int = Field(default=3, ge=1, le=30)
    dairy_days_before: int = Field(default=2, ge=1, le=30)
    meat_days_before: int = Field(default=1, ge=1, le=30)
    vegetables_days_before: int = Field(default=2, ge=1, le=30)
    fruits_days_before: int = Field(default=2, ge=1, le=30)
    bread_days_before: int = Field(default=1, ge=1, le=30)
    frozen_days_before: int = Field(default=7, ge=1, le=30)


class FoodReminderSettingsUpdate(BaseModel):
    """Schema for updating reminder settings."""
    enabled: Optional[bool] = None
    default_days_before: Optional[int] = Field(None, ge=1, le=30)
    dairy_days_before: Optional[int] = Field(None, ge=1, le=30)
    meat_days_before: Optional[int] = Field(None, ge=1, le=30)
    vegetables_days_before: Optional[int] = Field(None, ge=1, le=30)
    fruits_days_before: Optional[int] = Field(None, ge=1, le=30)
    bread_days_before: Optional[int] = Field(None, ge=1, le=30)
    frozen_days_before: Optional[int] = Field(None, ge=1, le=30)


class FoodReminderSettingsResponse(FoodReminderSettingsBase):
    """Schema for reminder settings response."""
    id: int
    user_id: int
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Consumption Log
class FoodConsumptionLogCreate(BaseModel):
    """Schema for creating consumption log entry."""
    product_id: Optional[int] = None
    inventory_item_id: Optional[int] = None
    quantity: float = Field(default=1, gt=0)
    unit: str = Field(default="szt")
    consumed_at: str
    meal_type: Optional[str] = None  # breakfast, lunch, dinner, snack
    notes: Optional[str] = None


class FoodConsumptionLogResponse(BaseModel):
    """Schema for consumption log response."""
    id: int
    user_id: int
    product_id: Optional[int] = None
    product: Optional[FoodProductResponse] = None
    inventory_item_id: Optional[int] = None
    quantity: float
    unit: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    consumed_at: str
    meal_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Search and filter helpers
class FoodProductSearchParams(BaseModel):
    """Schema for product search parameters."""
    query: Optional[str] = None
    category_id: Optional[int] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class FoodInventoryFilterParams(BaseModel):
    """Schema for inventory filter parameters."""
    status: Optional[str] = None
    location: Optional[str] = None
    category_id: Optional[int] = None
    expiring_within_days: Optional[int] = Field(None, ge=1)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
