"""Analytics schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List


class CategorySpending(BaseModel):
    """Schema for category spending summary."""
    category: str
    total: float
    count: int
    average: float
    percentage: Optional[float] = None


class MonthSummary(BaseModel):
    """Schema for monthly summary statistics."""
    month: str
    total_income: float
    total_expenses: float
    net_amount: float
    transactions_count: int
    by_category: List[CategorySpending]


class SpendingTrend(BaseModel):
    """Schema for spending trends over time."""
    month: str
    amount: float


class YearlySummary(BaseModel):
    """Schema for yearly summary statistics."""
    year: str
    total_income: float
    total_expenses: float
    net_amount: float
    transactions_count: int
    receipts_count: int
    by_category: List[CategorySpending]
    monthly_breakdown: List[MonthSummary]


class MerchantSpending(BaseModel):
    """Schema for merchant/shop spending summary."""
    merchant: str
    total: float
    receipts_count: int
    average: float
    percentage: Optional[float] = None


class BudgetStatus(BaseModel):
    """Schema for category budget status."""
    category: str
    icon: Optional[str] = None
    color: Optional[str] = None
    budget_limit: float
    spent: float
    remaining: float
    percentage: float
    status: str = Field(..., description="Budget status: ok, warning, over")
