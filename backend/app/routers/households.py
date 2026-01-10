from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..schemas import (
    HouseholdCreate,
    HouseholdUpdate,
    HouseholdResponse,
    HouseholdDetailResponse,
    HouseholdMemberResponse,
    HouseholdMemberUpdate,
    InvitationCreate,
    InvitationResponse,
    HouseholdMonthlySummary,
    HouseholdSpendingByMember,
    HouseholdSpendingByCategory,
)
from ..services.household import (
    HouseholdService,
    HouseholdNotFoundError,
    HouseholdAccessDeniedError,
    MemberNotFoundError,
    NotManagerError,
    CannotRemoveLastManagerError,
    InvalidRoleError,
    InvalidStatusError,
)
from ..services.invitation import (
    InvitationService,
    InvitationNotFoundError,
)
from ..services.analytics import (
    AnalyticsService,
    InvalidMonthFormatError,
)
from ..dependencies import (
    get_current_user,
    require_household_member,
    require_household_manager,
    HouseholdContext,
)
from ..models import User

# ---------------------------------------

router = APIRouter(prefix="/api/v1/households", tags=["households"])

# ---------------------------------------


async def get_household_service(db: AsyncSession = Depends(get_db)) -> HouseholdService:
    return HouseholdService(db)


async def get_invitation_service(db: AsyncSession = Depends(get_db)) -> InvitationService:
    return InvitationService(db)


async def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

# ---------------------------------------


@router.get("/", response_model=List[HouseholdResponse])
async def list_households(
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """List all households the current user is a member of."""
    return await service.list_user_households(current_user.id)


@router.post("/", response_model=HouseholdResponse, status_code=status.HTTP_201_CREATED)
async def create_household(
    data: HouseholdCreate,
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """Create a new household. The creator becomes the first manager."""
    return await service.create_household(data, current_user.id)


@router.get("/{uid}", response_model=HouseholdDetailResponse)
async def get_household(
    uid: str,
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """Get household details including members."""
    try:
        return await service.get_household(uid, current_user.id)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/{uid}", response_model=HouseholdResponse)
async def update_household(
    uid: str,
    data: HouseholdUpdate,
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """Update household details (manager only)."""
    try:
        return await service.update_household(uid, data, current_user.id)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_household(
    uid: str,
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """Delete a household (manager only)."""
    try:
        await service.delete_household(uid, current_user.id)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# Member management endpoints

@router.get("/{uid}/members", response_model=List[HouseholdMemberResponse])
async def get_household_members(
    uid: str,
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """Get all members of a household."""
    try:
        return await service.get_household_members(uid, current_user.id)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/{uid}/members/{user_id}", response_model=HouseholdMemberResponse)
async def update_household_member(
    uid: str,
    user_id: int,
    data: HouseholdMemberUpdate,
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """Update a member's role or status (manager only)."""
    try:
        return await service.update_member(uid, user_id, data, current_user.id)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except CannotRemoveLastManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except (InvalidRoleError, InvalidStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{uid}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_household_member(
    uid: str,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: HouseholdService = Depends(get_household_service),
):
    """Remove a member from household (manager only, or self-removal)."""
    try:
        await service.remove_member(uid, user_id, current_user.id)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except CannotRemoveLastManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Invitation management endpoints

@router.post("/{uid}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    uid: str,
    data: InvitationCreate,
    current_user: User = Depends(get_current_user),
    household_service: HouseholdService = Depends(get_household_service),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """Create a new invitation for a household (manager only)."""
    try:
        # Get household and verify manager access
        household = await household_service.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if current user is a manager
        member = await household_service.repository.get_member(household.id, current_user.id)
        if member is None:
            raise HouseholdAccessDeniedError()

        if member.role != "manager":
            raise NotManagerError()

        return await invitation_service.create_invitation(household, current_user.id, data)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/{uid}/invitations", response_model=List[InvitationResponse])
async def list_invitations(
    uid: str,
    current_user: User = Depends(get_current_user),
    household_service: HouseholdService = Depends(get_household_service),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """List all active invitations for a household (manager only)."""
    try:
        # Get household and verify manager access
        household = await household_service.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if current user is a manager
        member = await household_service.repository.get_member(household.id, current_user.id)
        if member is None:
            raise HouseholdAccessDeniedError()

        if member.role != "manager":
            raise NotManagerError()

        return await invitation_service.list_household_invitations(household)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/{uid}/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invitation(
    uid: str,
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    household_service: HouseholdService = Depends(get_household_service),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    """Revoke an invitation (manager only)."""
    try:
        # Get household and verify manager access
        household = await household_service.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if current user is a manager
        member = await household_service.repository.get_member(household.id, current_user.id)
        if member is None:
            raise HouseholdAccessDeniedError()

        if member.role != "manager":
            raise NotManagerError()

        await invitation_service.revoke_invitation(invitation_id, household)

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except HouseholdAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except InvitationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Household Analytics Endpoints
# ============================================================================

@router.get("/{uid}/analytics/summary", response_model=HouseholdMonthlySummary)
async def get_household_analytics_summary(
    month: str = Query(..., description="Month in YYYY-MM format"),
    context: HouseholdContext = Depends(require_household_member),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Get monthly summary analytics for a household."""
    try:
        return await analytics_service.get_household_monthly_summary(context.household_id, month)

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{uid}/analytics/by-member", response_model=HouseholdSpendingByMember)
async def get_household_spending_by_member(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (all time if not specified)"),
    context: HouseholdContext = Depends(require_household_member),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Get spending breakdown by household member."""
    try:
        return await analytics_service.get_household_spending_by_member(context.household_id, month)

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{uid}/analytics/by-category", response_model=HouseholdSpendingByCategory)
async def get_household_spending_by_category(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (all time if not specified)"),
    context: HouseholdContext = Depends(require_household_member),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """Get spending breakdown by category with member contributions."""
    try:
        return await analytics_service.get_household_spending_by_category(context.household_id, month)

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
