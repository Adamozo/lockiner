from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import Optional

from ..models import Household, HouseholdMember, User


class HouseholdRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, household_id: int) -> Household | None:
        result = await self.db.execute(
            select(Household).filter(Household.id == household_id)
        )
        return result.scalar_one_or_none()

    async def get_by_uid(self, uid: str) -> Household | None:
        result = await self.db.execute(
            select(Household).filter(Household.uid == uid)
        )
        return result.scalar_one_or_none()

    async def get_by_uid_with_members(self, uid: str) -> Household | None:
        result = await self.db.execute(
            select(Household)
            .options(selectinload(Household.members).selectinload(HouseholdMember.user))
            .filter(Household.uid == uid)
        )
        return result.scalar_one_or_none()

    async def get_user_households(self, user_id: int) -> list[Household]:
        result = await self.db.execute(
            select(Household)
            .join(HouseholdMember)
            .filter(HouseholdMember.user_id == user_id)
            .filter(HouseholdMember.status == "active")
        )
        return list(result.scalars().all())

    async def create(self, household: Household) -> Household:
        self.db.add(household)
        await self.db.commit()
        await self.db.refresh(household)
        return household

    async def update(self, household: Household) -> Household:
        household.updated_at = datetime.now(timezone.utc).isoformat()
        await self.db.commit()
        await self.db.refresh(household)
        return household

    async def delete(self, household: Household) -> None:
        await self.db.delete(household)
        await self.db.commit()

    # Household Member operations
    async def get_member(self, household_id: int, user_id: int) -> HouseholdMember | None:
        result = await self.db.execute(
            select(HouseholdMember).filter(
                HouseholdMember.household_id == household_id,
                HouseholdMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_member_by_household_uid(self, household_uid: str, user_id: int) -> HouseholdMember | None:
        result = await self.db.execute(
            select(HouseholdMember)
            .join(Household)
            .filter(
                Household.uid == household_uid,
                HouseholdMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_household_members(self, household_id: int) -> list[HouseholdMember]:
        result = await self.db.execute(
            select(HouseholdMember)
            .options(selectinload(HouseholdMember.user))
            .filter(HouseholdMember.household_id == household_id)
        )
        return list(result.scalars().all())

    async def count_members(self, household_id: int) -> int:
        result = await self.db.execute(
            select(HouseholdMember).filter(HouseholdMember.household_id == household_id)
        )
        return len(list(result.scalars().all()))

    async def count_managers(self, household_id: int) -> int:
        result = await self.db.execute(
            select(HouseholdMember).filter(
                HouseholdMember.household_id == household_id,
                HouseholdMember.role == "manager",
            )
        )
        return len(list(result.scalars().all()))

    async def add_member(self, member: HouseholdMember) -> HouseholdMember:
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def update_member(self, member: HouseholdMember) -> HouseholdMember:
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def remove_member(self, member: HouseholdMember) -> None:
        await self.db.delete(member)
        await self.db.commit()
