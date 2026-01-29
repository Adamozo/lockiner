"""Error response schemas for request/response validation."""

from pydantic import BaseModel
from typing import Optional, List


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""
    detail: List[dict]
