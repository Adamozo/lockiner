"""Household analytics schemas for request/response validation."""

from pydantic import BaseModel
from typing import Optional, List

from .analytics import CategorySpending


class MemberSpending(BaseModel):
    """Schema for individual member spending summary."""
    user_id: int
    user_name: str
    total: float
    count: int
    average: float
    percentage: float


class HouseholdMonthlySummary(BaseModel):
    """Schema for household monthly summary statistics."""
    month: str
    total_income: float
    total_expenses: float
    net_amount: float
    transactions_count: int
    by_category: List[CategorySpending]
    by_member: List[MemberSpending]


class HouseholdCategorySummary(BaseModel):
    """Schema for household category spending summary."""
    category: str
    total: float
    count: int
    average: float
    percentage: float
    by_member: List[MemberSpending]


class HouseholdSpendingByMember(BaseModel):
    """Schema for wrapped household spending by member response."""
    month: Optional[str] = None  # null = all-time
    members: List[MemberSpending]
    total: float


class HouseholdSpendingByCategory(BaseModel):
    """Schema for wrapped household spending by category response."""
    month: Optional[str] = None  # null = all-time
    categories: List[HouseholdCategorySummary]
    total: float
