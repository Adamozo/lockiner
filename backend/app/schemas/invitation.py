"""Invitation schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


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
