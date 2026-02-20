"""Shopping Lists module schemas (Pydantic V2)."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# ============================================================
# ShoppingListItem schemas
# ============================================================

class ShoppingListItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    position: int = Field(0, ge=0)
    food_product_id: Optional[int] = None
    is_recurring: bool = False


class ShoppingListItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    position: Optional[int] = Field(None, ge=0)
    is_recurring: Optional[bool] = None


class ShoppingItemStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|in_cart|purchased)$")


class ShoppingListItemResponse(BaseModel):
    id: int
    list_id: int
    added_by: int
    food_product_id: Optional[int]
    name: str
    quantity: Optional[float]
    unit: Optional[str]
    category: Optional[str]
    status: str
    is_recurring: bool
    notes: Optional[str]
    position: int
    created_at: str
    updated_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ShoppingList schemas
# ============================================================

class ShoppingListCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    store_name: Optional[str] = Field(None, max_length=255)
    planned_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    visibility: str = Field("private", pattern="^(private|household)$")
    household_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=2000)


class ShoppingListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    store_name: Optional[str] = Field(None, max_length=255)
    planned_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    visibility: Optional[str] = Field(None, pattern="^(private|household)$")
    household_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, pattern="^(active|completed|archived)$")


class ShoppingListResponse(BaseModel):
    id: int
    owner_id: int
    household_id: Optional[int]
    visibility: str
    name: str
    store_name: Optional[str]
    planned_date: Optional[str]
    status: str
    notes: Optional[str]
    items: List[ShoppingListItemResponse] = []
    created_at: str
    updated_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ShoppingListSummaryResponse(BaseModel):
    """Lightweight response without items — for listing multiple lists."""

    id: int
    owner_id: int
    household_id: Optional[int]
    visibility: str
    name: str
    store_name: Optional[str]
    planned_date: Optional[str]
    status: str
    total_items: int
    pending_items: int
    in_cart_items: int
    purchased_items: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)
