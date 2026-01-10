from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from ..models import HouseholdInvitation, Household
from ..schemas import (
    InvitationCreate,
    InvitationResponse,
    InvitationJoinResponse,
)
from ..repositories.invitation import InvitationRepository
from ..repositories.household import HouseholdRepository
from .household import HouseholdService, UserAlreadyMemberError

# ---------------------------------------


class InvitationNotFoundError(Exception):
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Invitation {identifier} not found")


class InvitationExpiredError(Exception):
    def __init__(self):
        super().__init__("This invitation has expired")


class InvitationMaxUsesReachedError(Exception):
    def __init__(self):
        super().__init__("This invitation has reached its maximum number of uses")


class InvitationInactiveError(Exception):
    def __init__(self):
        super().__init__("This invitation is no longer active")


class InvitationHouseholdNotFoundError(Exception):
    def __init__(self):
        super().__init__("The household for this invitation no longer exists")


# ---------------------------------------


class InvitationService:
    def __init__(self, db: AsyncSession):
        self.repository = InvitationRepository(db)
        self.household_repository = HouseholdRepository(db)
        self.household_service = HouseholdService(db)
        self.db = db

    def _invitation_to_response(self, invitation: HouseholdInvitation) -> InvitationResponse:
        """Convert HouseholdInvitation model to response schema."""
        return InvitationResponse(
            id=invitation.id,
            token=invitation.token,
            household_uid=invitation.household.uid if invitation.household else None,
            household_name=invitation.household.name if invitation.household else None,
            created_by_name=invitation.creator.name if invitation.creator else "Unknown",
            expires_at=invitation.expires_at,
            max_uses=invitation.max_uses,
            uses_count=invitation.uses_count,
            is_active=invitation.is_active,
            created_at=invitation.created_at,
        )

    async def create_invitation(
        self,
        household: Household,
        creator_id: int,
        data: InvitationCreate,
    ) -> InvitationResponse:
        """Create a new invitation for a household."""
        # Calculate expiration time if days provided
        expires_at = None
        if data.expires_in_days is not None:
            expires_at = (
                datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)
            ).isoformat()

        invitation = HouseholdInvitation(
            household_id=household.id,
            token=str(uuid.uuid4()),
            created_by=creator_id,
            expires_at=expires_at,
            max_uses=data.max_uses,
            uses_count=0,
            is_active=True,
        )

        invitation = await self.repository.create(invitation)

        # Reload with relationships
        invitation = await self.repository.get_by_id(invitation.id)

        return self._invitation_to_response(invitation)

    async def list_household_invitations(
        self,
        household: Household,
    ) -> list[InvitationResponse]:
        """List all active invitations for a household."""
        invitations = await self.repository.get_active_by_household(household.id)

        return [self._invitation_to_response(inv) for inv in invitations]

    async def revoke_invitation(
        self,
        invitation_id: int,
        household: Household,
    ) -> None:
        """Revoke (deactivate) an invitation."""
        invitation = await self.repository.get_by_id(invitation_id)

        if invitation is None:
            raise InvitationNotFoundError(str(invitation_id))

        # Verify invitation belongs to the household
        if invitation.household_id != household.id:
            raise InvitationNotFoundError(str(invitation_id))

        await self.repository.deactivate(invitation)

    async def get_invitation_info(self, token: str) -> InvitationResponse:
        """Get invitation information by token (for preview before joining)."""
        invitation = await self.repository.get_by_token(token)

        if invitation is None:
            raise InvitationNotFoundError(token)

        return self._invitation_to_response(invitation)

    async def join_by_invitation(
        self,
        token: str,
        user_id: int,
    ) -> InvitationJoinResponse:
        """Join a household using an invitation token."""
        invitation = await self.repository.get_by_token(token)

        if invitation is None:
            raise InvitationNotFoundError(token)

        # Validate invitation
        if not invitation.is_active:
            raise InvitationInactiveError()

        # Check expiration
        if invitation.expires_at is not None:
            expires_dt = datetime.fromisoformat(invitation.expires_at)
            if datetime.now(timezone.utc) > expires_dt:
                raise InvitationExpiredError()

        # Check max uses
        if invitation.max_uses is not None and invitation.uses_count >= invitation.max_uses:
            raise InvitationMaxUsesReachedError()

        # Check household exists
        household = await self.household_repository.get_by_id(invitation.household_id)
        if household is None:
            raise InvitationHouseholdNotFoundError()

        # Try to add user as member (this will raise if already member)
        try:
            await self.household_service.add_member_by_user_id(
                household_id=household.id,
                user_id=user_id,
                role="member",
            )
        except UserAlreadyMemberError:
            raise

        # Increment uses count
        await self.repository.increment_uses(invitation)

        return InvitationJoinResponse(
            success=True,
            household_uid=household.uid,
            household_name=household.name,
            message=f"Successfully joined household '{household.name}'",
        )
