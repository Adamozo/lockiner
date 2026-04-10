"""User/authentication schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    """Base schema for user data."""
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    email: str = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Schema for creating a new user (registration)."""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    voucher_code: str = Field(..., description="Registration voucher code (required)")
    language: str = "en"
    encrypted_dek: Optional[str] = None
    dek_salt: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    language: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (public info)."""
    id: int
    name: str
    role: str = "user"
    created_at: str
    is_active: bool
    totp_enabled: bool = False
    language: str = "en"
    encrypted_dek: Optional[str] = None
    dek_salt: Optional[str] = None

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
    encrypted_dek: Optional[str] = None
    dek_salt: Optional[str] = None


class ResetPasswordWithDekRequest(BaseModel):
    """Schema for password reset using recovery key (re-encrypts DEK client-side)."""
    email: str
    new_password: str = Field(..., min_length=8)
    encrypted_dek: str
    dek_salt: str
