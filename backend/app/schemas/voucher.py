"""Voucher schemas for request/response validation."""

from pydantic import BaseModel, ConfigDict
from typing import Optional


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
