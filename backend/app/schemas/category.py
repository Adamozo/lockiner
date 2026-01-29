"""Category schemas for request/response validation."""

from pydantic import BaseModel, ConfigDict
from typing import Optional


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
