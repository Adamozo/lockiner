"""
Pydantic schemas for request/response validation.

This module defines Pydantic models for API request validation
and response serialization. Follows Pydantic V2 syntax.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionBase(BaseModel):
    """Base schema for transaction data."""
    date: str = Field(..., description="Date in ISO 8601 format (YYYY-MM-DD)")
    amount: float = Field(..., description="Transaction amount (negative = expense)")
    description: Optional[str] = Field(None, description="Description from bank statement")
    category: str = Field(default="Inne", description="Expense category")
    payment_method: Optional[str] = Field(None, description="Payment method: card, cash, blik, other")
    receipt_id: Optional[int] = Field(None, description="Linked receipt ID")
    notes: Optional[str] = Field(None, description="User notes")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction (all fields optional)."""
    date: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    receipt_id: Optional[int] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Receipt Schemas
# ============================================================================

class ReceiptItem(BaseModel):
    """Individual item from receipt OCR."""
    name: str
    price: float
    quantity: Optional[int] = 1


class ReceiptBase(BaseModel):
    """Base schema for receipt data."""
    image_path: str
    scan_date: str = Field(..., description="Date in ISO 8601 format")
    merchant: Optional[str] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None
    items_json: Optional[str] = Field(None, description="JSON array of items")
    raw_ocr_response: Optional[str] = None
    verified: bool = False
    category: str = "Inne"


class ReceiptCreate(ReceiptBase):
    """Schema for creating a new receipt."""
    pass


class ReceiptUpdate(BaseModel):
    """Schema for updating a receipt."""
    merchant: Optional[str] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None
    items_json: Optional[str] = None
    verified: Optional[bool] = None
    category: Optional[str] = None


class ReceiptResponse(ReceiptBase):
    """Schema for receipt response."""
    id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class ReceiptItemDetailed(BaseModel):
    """Detailed receipt item with quantity and prices."""
    name: str
    quantity: int = 1
    unit_price: float
    total_price: float
    category: Optional[str] = None  # Item-level category (defaults to receipt category if not set)


class ReceiptOCRResponse(BaseModel):
    """Schema for OCR processing response."""
    merchant: str
    date: str
    total: float
    items: List[ReceiptItemDetailed]
    payment_method: Optional[str] = None
    tax_amount: Optional[float] = 0.0
    currency: str = "PLN"


class ReceiptUploadResponse(BaseModel):
    """Schema for receipt upload with OCR response."""
    receipt_id: int
    image_path: str
    ocr_data: Optional[ReceiptOCRResponse] = None
    error: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Category Schemas
# ============================================================================

class CategoryBase(BaseModel):
    """Base schema for category data."""
    name: str
    budget_limit: Optional[float] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = None
    budget_limit: Optional[float] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Monthly Import Schemas
# ============================================================================

class MonthlyImportBase(BaseModel):
    """Base schema for monthly import data."""
    month: str = Field(..., description="Month in YYYY-MM format")
    filename: Optional[str] = None
    transactions_count: Optional[int] = None


class MonthlyImportCreate(MonthlyImportBase):
    """Schema for creating a new import record."""
    pass


class MonthlyImportResponse(MonthlyImportBase):
    """Schema for monthly import response."""
    id: int
    imported_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Analytics Schemas
# ============================================================================

class CategorySpending(BaseModel):
    """Schema for category spending summary."""
    category: str
    total: float
    count: int
    average: float
    percentage: Optional[float] = None


class MonthSummary(BaseModel):
    """Schema for monthly summary statistics."""
    month: str
    total_income: float
    total_expenses: float
    net_amount: float
    transactions_count: int
    by_category: List[CategorySpending]


class SpendingTrend(BaseModel):
    """Schema for spending trends over time."""
    month: str
    amount: float


class YearlySummary(BaseModel):
    """Schema for yearly summary statistics."""
    year: str
    total_income: float
    total_expenses: float
    net_amount: float
    transactions_count: int
    receipts_count: int
    by_category: List[CategorySpending]
    monthly_breakdown: List[MonthSummary]


class MerchantSpending(BaseModel):
    """Schema for merchant/shop spending summary."""
    merchant: str
    total: float
    receipts_count: int
    average: float
    percentage: Optional[float] = None


class BudgetStatus(BaseModel):
    """Schema for category budget status."""
    category: str
    icon: Optional[str] = None
    color: Optional[str] = None
    budget_limit: float
    spent: float
    remaining: float
    percentage: float
    status: str = Field(..., description="Budget status: ok, warning, over")


# ============================================================================
# Budget Settings Schemas
# ============================================================================

class BudgetSettingsBase(BaseModel):
    """Base schema for budget settings."""
    overall_monthly_limit: Optional[float] = None
    alert_threshold_warning: float = Field(80.0, ge=0, le=100)
    alert_threshold_danger: float = Field(100.0, ge=0, le=100)
    enable_alerts: bool = True


class BudgetSettingsUpdate(BaseModel):
    """Schema for updating budget settings."""
    overall_monthly_limit: Optional[float] = None
    alert_threshold_warning: Optional[float] = Field(None, ge=0, le=100)
    alert_threshold_danger: Optional[float] = Field(None, ge=0, le=100)
    enable_alerts: Optional[bool] = None


class BudgetSettingsResponse(BudgetSettingsBase):
    """Schema for budget settings response."""
    id: int
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OverallBudgetStatus(BaseModel):
    """Schema for overall budget status."""
    month: str
    overall_limit: Optional[float] = None
    total_spent: float
    remaining: float
    percentage: float
    status: str = Field(..., description="Budget status: ok, warning, over, no_limit")
    alert_message: Optional[str] = None


class CompleteBudgetStatus(BaseModel):
    """Schema for complete budget status including overall and categories."""
    overall: OverallBudgetStatus
    categories: List[BudgetStatus]
    settings: BudgetSettingsResponse


class BudgetAlert(BaseModel):
    """Schema for budget alert notification."""
    type: str = Field(..., description="Alert type: overall or category")
    severity: str = Field(..., description="Alert severity: warning or over")
    message: str
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class BudgetAlertsResponse(BaseModel):
    """Schema for budget alerts response."""
    alerts: List[BudgetAlert]


# ============================================================================
# CSV Import Schemas
# ============================================================================

class CSVImportRequest(BaseModel):
    """Schema for CSV import request."""
    month: str = Field(..., description="Month in YYYY-MM format")
    filename: str
    transactions: List[TransactionCreate]


class CSVImportResponse(BaseModel):
    """Schema for CSV import response."""
    month: str
    imported_count: int
    skipped_count: int
    errors: List[str] = []


# ============================================================================
# Error Response Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""
    detail: List[dict]


# ============================================================================
# Settings/Configuration Schemas
# ============================================================================

class APIProviderConfigBase(BaseModel):
    """Base schema for API provider configuration."""
    provider: str = Field(..., description="Provider type: gemini, claude, openai")
    api_key: str = Field(..., min_length=1, description="API key for the provider")
    is_active: bool = Field(default=False, description="Whether this provider is currently active")


class APIProviderConfigCreate(APIProviderConfigBase):
    """Schema for creating API provider configuration."""
    pass


class APIProviderConfigResponse(BaseModel):
    """Schema for API provider configuration response (without full API key)."""
    provider: str
    key_preview: str = Field(..., description="First 8 characters of API key")
    is_active: bool
    configured_at: Optional[str] = None


class APIProviderListResponse(BaseModel):
    """Schema for listing all configured API providers."""
    providers: List[APIProviderConfigResponse]
    active_provider: Optional[str] = None


class SetActiveProviderRequest(BaseModel):
    """Schema for setting active provider."""
    provider: str = Field(..., description="Provider type to set as active: gemini, claude, openai")


# ============================================================================
# Voucher Schemas
# ============================================================================

class VoucherResponse(BaseModel):
    """Schema for voucher response."""
    id: int
    code: str
    is_used: bool
    used_at: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class VoucherValidateResponse(BaseModel):
    """Schema for voucher validation response."""
    valid: bool
    message: str


# ============================================================================
# User/Authentication Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base schema for user data."""
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    email: str = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Schema for creating a new user (registration)."""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    voucher_code: str = Field(..., description="Registration voucher code (required)")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserResponse(BaseModel):
    """Schema for user response (public info)."""
    id: int
    name: str
    created_at: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


# ============================================================================
# Household Schemas
# ============================================================================

class HouseholdBase(BaseModel):
    """Base schema for household data."""
    name: str = Field(..., min_length=1, max_length=100, description="Household name")
    description: Optional[str] = Field(None, max_length=500, description="Household description")
    icon: Optional[str] = Field(None, description="Icon identifier or emoji")


class HouseholdCreate(HouseholdBase):
    """Schema for creating a new household."""
    pass


class HouseholdUpdate(BaseModel):
    """Schema for updating a household."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = None


class HouseholdMemberResponse(BaseModel):
    """Schema for household member info."""
    user_id: int
    user_name: str
    role: str = Field(..., description="Role: manager or member")
    status: str = Field(..., description="Status: active or blocked")
    joined_at: str


class HouseholdResponse(HouseholdBase):
    """Schema for household response."""
    uid: str
    created_at: str
    updated_at: Optional[str] = None
    member_count: int = 0
    current_user_role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HouseholdDetailResponse(HouseholdResponse):
    """Schema for detailed household response with members."""
    members: List[HouseholdMemberResponse] = []


class HouseholdMemberUpdate(BaseModel):
    """Schema for updating a household member."""
    role: Optional[str] = Field(None, description="Role: manager or member")
    status: Optional[str] = Field(None, description="Status: active or blocked")


# ============================================================================
# Invitation Schemas
# ============================================================================

class InvitationCreate(BaseModel):
    """Schema for creating a household invitation."""
    expires_in_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Number of days until invitation expires (null = never)"
    )
    max_uses: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of times the invitation can be used (null = unlimited)"
    )


class InvitationResponse(BaseModel):
    """Schema for invitation response."""
    id: int
    token: str
    household_uid: Optional[str] = None
    household_name: Optional[str] = None
    created_by_name: str
    expires_at: Optional[str] = None
    max_uses: Optional[int] = None
    uses_count: int = 0
    is_active: bool = True
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class InvitationJoinResponse(BaseModel):
    """Schema for successful invitation join."""
    success: bool = True
    household_uid: str
    household_name: str
    message: str


# ============================================================================
# Household Analytics Schemas
# ============================================================================

class MemberSpending(BaseModel):
    """Schema for individual member spending summary."""
    user_id: int
    user_name: str
    total: float
    count: int
    average: float
    percentage: float


class HouseholdMonthlySummary(BaseModel):
    """Schema for household monthly summary statistics."""
    month: str
    total_income: float
    total_expenses: float
    net_amount: float
    transactions_count: int
    by_category: List[CategorySpending]
    by_member: List[MemberSpending]


class HouseholdCategorySummary(BaseModel):
    """Schema for household category spending summary."""
    category: str
    total: float
    count: int
    average: float
    percentage: float
    by_member: List[MemberSpending]


class HouseholdSpendingByMember(BaseModel):
    """Schema for wrapped household spending by member response."""
    month: Optional[str] = None  # null = all-time
    members: List[MemberSpending]
    total: float


class HouseholdSpendingByCategory(BaseModel):
    """Schema for wrapped household spending by category response."""
    month: Optional[str] = None  # null = all-time
    categories: List[HouseholdCategorySummary]
    total: float


# ============================================================================
# Food Module Schemas
# ============================================================================

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
