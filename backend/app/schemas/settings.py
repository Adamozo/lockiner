"""API provider configuration schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List


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
