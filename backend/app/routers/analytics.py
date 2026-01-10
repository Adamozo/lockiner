from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import (
    CategorySpending,
    MonthSummary,
    SpendingTrend,
    YearlySummary,
    MerchantSpending,
    BudgetSettingsResponse,
    BudgetSettingsUpdate,
    BudgetAlertsResponse,
)
from ..services.analytics import (
    AnalyticsService,
    InvalidMonthFormatError,
    InvalidYearFormatError,
    InvalidTransactionTypeError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# ---------------------------------------


async def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

# ---------------------------------------


@router.get("/summary", response_model=MonthSummary)
async def get_monthly_summary(
    month: str = Query(..., description="Month in YYYY-MM format"),
    household_id: Optional[str] = Query(None, description="Filter by household UUID"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.get_monthly_summary(
            month,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/by-category", response_model=List[CategorySpending])
async def get_spending_by_category(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (all time if not specified)"),
    household_id: Optional[str] = Query(None, description="Filter by household UUID"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.get_spending_by_category(
            month,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/top")
async def get_top_transactions(
    limit: int = Query(10, ge=1, le=100, description="Number of top transactions to return"),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    category: Optional[str] = Query(None, description="Filter by category"),
    type: str = Query("expenses", description="Transaction type: 'expenses' or 'income'"),
    household_id: Optional[str] = Query(None, description="Filter by household UUID"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.get_top_transactions(
            limit=limit,
            month=month,
            category=category,
            transaction_type=type,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except InvalidTransactionTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/trends", response_model=List[SpendingTrend])
async def get_spending_trends(
    months: int = Query(6, ge=1, le=24, description="Number of months to include"),
    category: Optional[str] = Query(None, description="Filter by category"),
    household_id: Optional[str] = Query(None, description="Filter by household UUID"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_spending_trends(
        months=months,
        category=category,
        user_id=current_user.id,
        household_uid=household_id,
    )


@router.get("/budget-status")
async def get_budget_status(
    month: str = Query(..., description="Month in YYYY-MM format"),
    household_id: Optional[str] = Query(None, description="Filter by household UUID"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.get_budget_status(
            month,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/yearly-summary", response_model=YearlySummary)
async def get_yearly_summary(
    year: str = Query(..., description="Year in YYYY format"),
    household_id: Optional[str] = Query(None, description="Filter by household UUID"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.get_yearly_summary(
            year,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidYearFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/by-merchant", response_model=List[MerchantSpending])
async def get_spending_by_merchant(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (all time if not specified)"),
    household_id: Optional[str] = Query(None, description="Filter by household UUID"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.get_spending_by_merchant(
            month,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/budget-settings", response_model=BudgetSettingsResponse)
async def get_budget_settings(
    household_id: Optional[str] = Query(None, description="Get household budget settings (UUID)"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_budget_settings(
        user_id=current_user.id,
        household_uid=household_id,
    )


@router.put("/budget-settings", response_model=BudgetSettingsResponse)
async def update_budget_settings(
    settings_update: BudgetSettingsUpdate,
    household_id: Optional[str] = Query(None, description="Update household budget settings (UUID)"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.update_budget_settings(
            settings_update,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update budget settings: {str(e)}",
        )


@router.get("/budget-status-complete")
async def get_complete_budget_status(
    month: str = Query(..., description="Month in YYYY-MM format"),
    household_id: Optional[str] = Query(None, description="Get household budget status (UUID)"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.get_complete_budget_status(
            month,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/budget-alerts", response_model=BudgetAlertsResponse)
async def check_budget_alerts(
    month: str = Query(..., description="Month in YYYY-MM format"),
    household_id: Optional[str] = Query(None, description="Check household budget alerts (UUID)"),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return await service.check_budget_alerts(
            month,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
