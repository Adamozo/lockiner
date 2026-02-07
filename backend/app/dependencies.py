from fastapi import Depends, HTTPException, status, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Callable
from dataclasses import dataclass

from .database import get_db
from .models import User, HouseholdMember
from .services.auth import (
    AuthService,
    InvalidTokenError,
    UserNotFoundError,
    UserInactiveError,
)
from .repositories.household import HouseholdRepository

# ---------------------------------------

security = HTTPBearer()

# ---------------------------------------


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from the JWT token."""
    token = credentials.credentials
    auth_service = AuthService(db)

    try:
        user = await auth_service.get_current_user(token)
        return user

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user (alias for get_current_user with explicit check)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require user to have admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ============================================================================
# Household Permission Dependencies
# ============================================================================

@dataclass
class HouseholdContext:
    """Context object containing household and member info after permission check."""
    household_id: int
    household_uid: str
    member: HouseholdMember
    user: User


class HouseholdPermissionError(Exception):
    """Base exception for household permission errors."""
    pass


class NotHouseholdMemberError(HouseholdPermissionError):
    """User is not a member of the household."""
    def __init__(self):
        super().__init__("You are not a member of this household")


class HouseholdAccessBlockedError(HouseholdPermissionError):
    """User's access to the household is blocked."""
    def __init__(self):
        super().__init__("Your access to this household is blocked")


class NotHouseholdManagerError(HouseholdPermissionError):
    """User is not a manager of the household."""
    def __init__(self):
        super().__init__("Only managers can perform this action")


class HouseholdNotFoundError(HouseholdPermissionError):
    """Household not found."""
    def __init__(self, uid: str):
        super().__init__(f"Household {uid} not found")


async def _get_household_member(
    uid: str,
    user: User,
    db: AsyncSession,
) -> tuple[int, HouseholdMember]:
    """Internal helper to get household and member info."""
    repo = HouseholdRepository(db)

    household = await repo.get_by_uid(uid)
    if household is None:
        raise HouseholdNotFoundError(uid)

    member = await repo.get_member(household.id, user.id)
    if member is None:
        raise NotHouseholdMemberError()

    return household.id, household.uid, member


async def require_household_member(
    uid: str = Path(..., description="Household UID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HouseholdContext:
    """
    Dependency that requires the user to be an active member of the household.

    Use this for endpoints that any active household member can access
    (view transactions, receipts, analytics, etc).

    Raises:
        HTTPException 404: Household not found
        HTTPException 403: User is not a member or is blocked
    """
    try:
        household_id, household_uid, member = await _get_household_member(uid, current_user, db)

        if member.status == "blocked":
            raise HouseholdAccessBlockedError()

        return HouseholdContext(
            household_id=household_id,
            household_uid=household_uid,
            member=member,
            user=current_user,
        )

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except (NotHouseholdMemberError, HouseholdAccessBlockedError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


async def require_household_manager(
    uid: str = Path(..., description="Household UID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HouseholdContext:
    """
    Dependency that requires the user to be a manager of the household.

    Use this for endpoints that only managers can access
    (manage members, invitations, update/delete household, etc).

    Raises:
        HTTPException 404: Household not found
        HTTPException 403: User is not a member, is blocked, or is not a manager
    """
    try:
        household_id, household_uid, member = await _get_household_member(uid, current_user, db)

        if member.status == "blocked":
            raise HouseholdAccessBlockedError()

        if member.role != "manager":
            raise NotHouseholdManagerError()

        return HouseholdContext(
            household_id=household_id,
            household_uid=household_uid,
            member=member,
            user=current_user,
        )

    except HouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except NotHouseholdMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except HouseholdAccessBlockedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except NotHouseholdManagerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
