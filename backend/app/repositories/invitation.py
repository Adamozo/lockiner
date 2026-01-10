from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List

from ..models import HouseholdInvitation


class InvitationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, invitation: HouseholdInvitation) -> HouseholdInvitation:
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def get_by_id(self, invitation_id: int) -> Optional[HouseholdInvitation]:
        result = await self.db.execute(
            select(HouseholdInvitation)
            .options(selectinload(HouseholdInvitation.household))
            .options(selectinload(HouseholdInvitation.creator))
            .where(HouseholdInvitation.id == invitation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Optional[HouseholdInvitation]:
        result = await self.db.execute(
            select(HouseholdInvitation)
            .options(selectinload(HouseholdInvitation.household))
            .options(selectinload(HouseholdInvitation.creator))
            .where(HouseholdInvitation.token == token)
        )
        return result.scalar_one_or_none()

    async def get_active_by_household(self, household_id: int) -> List[HouseholdInvitation]:
        result = await self.db.execute(
            select(HouseholdInvitation)
            .options(selectinload(HouseholdInvitation.creator))
            .where(
                and_(
                    HouseholdInvitation.household_id == household_id,
                    HouseholdInvitation.is_active == True,
                )
            )
            .order_by(HouseholdInvitation.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, invitation: HouseholdInvitation) -> HouseholdInvitation:
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def delete(self, invitation: HouseholdInvitation) -> None:
        await self.db.delete(invitation)
        await self.db.commit()

    async def deactivate(self, invitation: HouseholdInvitation) -> HouseholdInvitation:
        invitation.is_active = False
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def increment_uses(self, invitation: HouseholdInvitation) -> HouseholdInvitation:
        invitation.uses_count += 1
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation
