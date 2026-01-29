"""Budget settings schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

from .analytics import BudgetStatus


class BudgetSettingsBase(BaseModel):
    """Base schema for budget settings."""
    overall_monthly_limit: Optional[float] = None
    alert_threshold_warning: float = Field(80.0, ge=0, le=100)
    alert_threshold_danger: float = Field(100.0, ge=0, le=100)
    enable_alerts: bool = True


class BudgetSettingsUpdate(BaseModel):
    """Schema for updating budget settings."""
    overall_monthly_limit: Optional[float] = None
    alert_threshold_warning: Optional[float] = Field(None, ge=0, le=100)
    alert_threshold_danger: Optional[float] = Field(None, ge=0, le=100)
    enable_alerts: Optional[bool] = None


class BudgetSettingsResponse(BudgetSettingsBase):
    """Schema for budget settings response."""
    id: int
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OverallBudgetStatus(BaseModel):
    """Schema for overall budget status."""
    month: str
    overall_limit: Optional[float] = None
    total_spent: float
    remaining: float
    percentage: float
    status: str = Field(..., description="Budget status: ok, warning, over, no_limit")
    alert_message: Optional[str] = None


class CompleteBudgetStatus(BaseModel):
    """Schema for complete budget status including overall and categories."""
    overall: OverallBudgetStatus
    categories: List[BudgetStatus]
    settings: BudgetSettingsResponse


class BudgetAlert(BaseModel):
    """Schema for budget alert notification."""
    type: str = Field(..., description="Alert type: overall or category")
    severity: str = Field(..., description="Alert severity: warning or over")
    message: str
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class BudgetAlertsResponse(BaseModel):
    """Schema for budget alerts response."""
    alerts: List[BudgetAlert]
