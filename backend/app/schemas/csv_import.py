"""CSV import schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import List

from .transaction import TransactionCreate


class CSVImportRequest(BaseModel):
    """Schema for CSV import request."""
    month: str = Field(..., description="Month in YYYY-MM format")
    filename: str
    transactions: List[TransactionCreate]


class CSVImportResponse(BaseModel):
    """Schema for CSV import response."""
    month: str
    imported_count: int
    skipped_count: int
    errors: List[str] = []
