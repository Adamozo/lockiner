"""Transaction schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TransactionBase(BaseModel):
    """Base schema for transaction data."""
    date: str = Field(..., description="Date in ISO 8601 format (YYYY-MM-DD)")
    amount: float = Field(..., description="Transaction amount (negative = expense)")
    description: Optional[str] = Field(None, description="Description from bank statement")
    category: str = Field(default="Inne", description="Expense category")
    payment_method: Optional[str] = Field(None, description="Payment method: card, cash, blik, other")
    receipt_id: Optional[int] = Field(None, description="Linked receipt ID")
    notes: Optional[str] = Field(None, description="User notes")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction (all fields optional)."""
    date: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    receipt_id: Optional[int] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)
