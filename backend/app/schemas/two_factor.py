"""Two-factor authentication schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TwoFactorSetupResponse(BaseModel):
    """Response when initiating 2FA setup."""
    secret: str
    uri: str


class TwoFactorVerifySetupRequest(BaseModel):
    """Request to verify initial 2FA setup with first TOTP code."""
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')


class TwoFactorVerifySetupResponse(BaseModel):
    """Response after verifying 2FA setup - contains recovery codes."""
    recovery_codes: list[str]


class TwoFactorDisableRequest(BaseModel):
    """Request to disable 2FA."""
    code: str = Field(..., min_length=6, max_length=10)


class TwoFactorStatusResponse(BaseModel):
    """2FA status for current user."""
    enabled: bool
    recovery_codes_remaining: int


class TwoFactorVerifyLoginRequest(BaseModel):
    """Request to complete login with 2FA code."""
    two_factor_token: str
    code: str = Field(..., min_length=6, max_length=10)


class TwoFactorRegenerateRequest(BaseModel):
    """Request to regenerate recovery codes (requires TOTP code)."""
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')


class TwoFactorRegenerateResponse(BaseModel):
    """Response with new recovery codes."""
    recovery_codes: list[str]


class LoginResponse(BaseModel):
    """Extended login response that supports 2FA flow."""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    requires_2fa: bool = False
    two_factor_token: Optional[str] = None
