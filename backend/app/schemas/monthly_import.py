"""Monthly import schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


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
