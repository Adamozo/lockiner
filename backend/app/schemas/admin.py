"""Admin panel schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# ============================================================================
# Voucher Admin Schemas
# ============================================================================

class VoucherAdminResponse(BaseModel):
    """Admin view of a voucher."""
    id: int
    code: str
    status: str  # available | used | blocked
    used_by_user_id: Optional[int] = None
    used_by_name: Optional[str] = None
    used_at: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class VoucherGenerateRequest(BaseModel):
    """Request to generate vouchers."""
    count: int = Field(..., ge=1, le=100, description="Number of vouchers to generate")


class VoucherGenerateResponse(BaseModel):
    """Response after generating vouchers."""
    vouchers: List[VoucherAdminResponse]
    count: int


# ============================================================================
# User Admin Schemas
# ============================================================================

class UserAdminResponse(BaseModel):
    """Admin view of a user."""
    id: int
    name: str
    role: str  # user | admin
    is_active: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class SetRoleRequest(BaseModel):
    """Request to change user role."""
    role: str = Field(..., pattern="^(user|admin)$", description="New role: user or admin")
