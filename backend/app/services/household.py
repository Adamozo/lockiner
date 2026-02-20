from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from ..models import Household, HouseholdMember, User
from ..schemas import (
    HouseholdCreate,
    HouseholdUpdate,
    HouseholdResponse,
    HouseholdDetailResponse,
    HouseholdMemberResponse,
    HouseholdMemberUpdate,
)
from ..repositories.household import HouseholdRepository

# ---------------------------------------


class HouseholdNotFoundError(Exception):
    def __init__(self, uid: str):
        self.uid = uid
        super().__init__(f"Household {uid} not found")


class HouseholdAccessDeniedError(Exception):
    def __init__(self, message: str = "Access denied to this household"):
        super().__init__(message)


class MemberNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Member with user_id {user_id} not found in household")


class NotManagerError(Exception):
    def __init__(self):
        super().__init__("Only managers can perform this action")


class CannotRemoveLastManagerError(Exception):
    def __init__(self):
        super().__init__("Cannot remove or demote the last manager of the household")


class UserAlreadyMemberError(Exception):
    def __init__(self):
        super().__init__("User is already a member of this household")


class InvalidRoleError(Exception):
    def __init__(self):
        super().__init__("Invalid role. Must be 'manager' or 'member'")


class InvalidStatusError(Exception):
    def __init__(self):
        super().__init__("Invalid status. Must be 'active' or 'blocked'")


# ---------------------------------------


class HouseholdService:
    def __init__(self, db: AsyncSession):
        self.repository = HouseholdRepository(db)
        self.db = db

    def _household_to_response(
        self,
        household: Household,
        current_user_id: int,
        include_members: bool = False,
    ) -> HouseholdResponse | HouseholdDetailResponse:
        """Convert Household model to response schema."""
        member_count = len(household.members) if household.members else 0
        current_user_role = None

        members_response = []
        for member in (household.members or []):
            if member.user_id == current_user_id:
                current_user_role = member.role

            if include_members:
                members_response.append(
                    HouseholdMemberResponse(
                        user_id=member.user_id,
                        user_name=member.user.name if member.user else "Unknown",
                        role=member.role,
                        status=member.status,
                        joined_at=member.joined_at,
                    )
                )

        base_data = {
            "id": household.id,
            "uid": household.uid,
            "name": household.name,
            "description": household.description,
            "icon": household.icon,
            "created_at": household.created_at,
            "updated_at": household.updated_at,
            "member_count": member_count,
            "current_user_role": current_user_role,
        }

        if include_members:
            return HouseholdDetailResponse(**base_data, members=members_response)

        return HouseholdResponse(**base_data)

    async def list_user_households(self, user_id: int) -> list[HouseholdResponse]:
        """List all households for a user."""
        households = await self.repository.get_user_households(user_id)

        result = []
        for household in households:
            # Get member count
            member_count = await self.repository.count_members(household.id)

            # Get user's role in this household
            member = await self.repository.get_member(household.id, user_id)

            result.append(
                HouseholdResponse(
                    id=household.id,
                    uid=household.uid,
                    name=household.name,
                    description=household.description,
                    icon=household.icon,
                    created_at=household.created_at,
                    updated_at=household.updated_at,
                    member_count=member_count,
                    current_user_role=member.role if member else None,
                )
            )

        return result

    async def get_household(self, uid: str, current_user_id: int) -> HouseholdDetailResponse:
        """Get household details with members."""
        household = await self.repository.get_by_uid_with_members(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if user is a member
        member = await self.repository.get_member(household.id, current_user_id)
        if member is None:
            raise HouseholdAccessDeniedError()

        if member.status == "blocked":
            raise HouseholdAccessDeniedError("Your access to this household is blocked")

        return self._household_to_response(household, current_user_id, include_members=True)

    async def create_household(self, data: HouseholdCreate, creator_id: int) -> HouseholdResponse:
        """Create a new household and add creator as manager."""
        household = Household(
            uid=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            icon=data.icon,
        )

        household = await self.repository.create(household)

        # Add creator as manager
        member = HouseholdMember(
            household_id=household.id,
            user_id=creator_id,
            role="manager",
            status="active",
        )
        await self.repository.add_member(member)

        return HouseholdResponse(
            id=household.id,
            uid=household.uid,
            name=household.name,
            description=household.description,
            icon=household.icon,
            created_at=household.created_at,
            updated_at=household.updated_at,
            member_count=1,
            current_user_role="manager",
        )

    async def update_household(
        self,
        uid: str,
        data: HouseholdUpdate,
        current_user_id: int,
    ) -> HouseholdResponse:
        """Update household details (manager only)."""
        household = await self.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if user is a manager
        member = await self.repository.get_member(household.id, current_user_id)
        if member is None:
            raise HouseholdAccessDeniedError()

        if member.role != "manager":
            raise NotManagerError()

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(household, field, value)

        household = await self.repository.update(household)
        member_count = await self.repository.count_members(household.id)

        return HouseholdResponse(
            id=household.id,
            uid=household.uid,
            name=household.name,
            description=household.description,
            icon=household.icon,
            created_at=household.created_at,
            updated_at=household.updated_at,
            member_count=member_count,
            current_user_role=member.role,
        )

    async def delete_household(self, uid: str, current_user_id: int) -> None:
        """Delete a household (manager only)."""
        household = await self.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if user is a manager
        member = await self.repository.get_member(household.id, current_user_id)
        if member is None:
            raise HouseholdAccessDeniedError()

        if member.role != "manager":
            raise NotManagerError()

        await self.repository.delete(household)

    async def get_household_members(self, uid: str, current_user_id: int) -> list[HouseholdMemberResponse]:
        """Get all members of a household."""
        household = await self.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if user is a member
        member = await self.repository.get_member(household.id, current_user_id)
        if member is None:
            raise HouseholdAccessDeniedError()

        members = await self.repository.get_household_members(household.id)

        return [
            HouseholdMemberResponse(
                user_id=m.user_id,
                user_name=m.user.name if m.user else "Unknown",
                role=m.role,
                status=m.status,
                joined_at=m.joined_at,
            )
            for m in members
        ]

    async def update_member(
        self,
        uid: str,
        target_user_id: int,
        data: HouseholdMemberUpdate,
        current_user_id: int,
    ) -> HouseholdMemberResponse:
        """Update a household member's role or status (manager only)."""
        household = await self.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Check if current user is a manager
        current_member = await self.repository.get_member(household.id, current_user_id)
        if current_member is None:
            raise HouseholdAccessDeniedError()

        if current_member.role != "manager":
            raise NotManagerError()

        # Get target member
        target_member = await self.repository.get_member(household.id, target_user_id)
        if target_member is None:
            raise MemberNotFoundError(target_user_id)

        # Validate role and status
        if data.role is not None and data.role not in ("manager", "member"):
            raise InvalidRoleError()

        if data.status is not None and data.status not in ("active", "blocked"):
            raise InvalidStatusError()

        # Check if demoting last manager
        if data.role == "member" and target_member.role == "manager":
            manager_count = await self.repository.count_managers(household.id)
            if manager_count <= 1:
                raise CannotRemoveLastManagerError()

        if data.role is not None:
            target_member.role = data.role

        if data.status is not None:
            target_member.status = data.status

        target_member = await self.repository.update_member(target_member)

        # Reload to get user info
        await self.db.refresh(target_member, ["user"])

        return HouseholdMemberResponse(
            user_id=target_member.user_id,
            user_name=target_member.user.name if target_member.user else "Unknown",
            role=target_member.role,
            status=target_member.status,
            joined_at=target_member.joined_at,
        )

    async def remove_member(
        self,
        uid: str,
        target_user_id: int,
        current_user_id: int,
    ) -> None:
        """Remove a member from household (manager only, or self-removal)."""
        household = await self.repository.get_by_uid(uid)

        if household is None:
            raise HouseholdNotFoundError(uid)

        # Get current user's membership
        current_member = await self.repository.get_member(household.id, current_user_id)
        if current_member is None:
            raise HouseholdAccessDeniedError()

        # Self-removal is always allowed
        if target_user_id == current_user_id:
            # But managers can't leave if they're the only one
            if current_member.role == "manager":
                manager_count = await self.repository.count_managers(household.id)
                if manager_count <= 1:
                    raise CannotRemoveLastManagerError()

            await self.repository.remove_member(current_member)
            return

        # For removing others, must be a manager
        if current_member.role != "manager":
            raise NotManagerError()

        # Get target member
        target_member = await self.repository.get_member(household.id, target_user_id)
        if target_member is None:
            raise MemberNotFoundError(target_user_id)

        # Check if removing last manager
        if target_member.role == "manager":
            manager_count = await self.repository.count_managers(household.id)
            if manager_count <= 1:
                raise CannotRemoveLastManagerError()

        await self.repository.remove_member(target_member)

    async def add_member_by_user_id(
        self,
        household_id: int,
        user_id: int,
        role: str = "member",
    ) -> HouseholdMember:
        """Add a user as a member to a household (used by invitation system)."""
        # Check if already a member
        existing = await self.repository.get_member(household_id, user_id)
        if existing is not None:
            raise UserAlreadyMemberError()

        member = HouseholdMember(
            household_id=household_id,
            user_id=user_id,
            role=role,
            status="active",
        )

        return await self.repository.add_member(member)
