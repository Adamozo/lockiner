from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import (
    InvitationResponse,
    InvitationJoinResponse,
)
from ..services.invitation import (
    InvitationService,
    InvitationNotFoundError,
    InvitationExpiredError,
    InvitationMaxUsesReachedError,
    InvitationInactiveError,
    InvitationHouseholdNotFoundError,
)
from ..services.household import UserAlreadyMemberError
from ..dependencies import get_current_user
from ..models import User

# ---------------------------------------

router = APIRouter(prefix="/api/v1/invitations", tags=["invitations"])

# ---------------------------------------


async def get_invitation_service(db: AsyncSession = Depends(get_db)) -> InvitationService:
    return InvitationService(db)

# ---------------------------------------


@router.get("/{token}", response_model=InvitationResponse)
async def get_invitation_info(
    token: str,
    service: InvitationService = Depends(get_invitation_service),
):
    """Get invitation information by token (no authentication required for preview)."""
    try:
        return await service.get_invitation_info(token)

    except InvitationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{token}/join", response_model=InvitationJoinResponse)
async def join_by_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    service: InvitationService = Depends(get_invitation_service),
):
    """Join a household using an invitation token."""
    try:
        return await service.join_by_invitation(token, current_user.id)

    except InvitationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except InvitationExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(e),
        )

    except InvitationMaxUsesReachedError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(e),
        )

    except InvitationInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(e),
        )

    except InvitationHouseholdNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except UserAlreadyMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
