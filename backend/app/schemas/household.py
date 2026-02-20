"""Household schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


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
    id: int
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
