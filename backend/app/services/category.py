from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from ..models import Category
from ..schemas import CategoryCreate, CategoryUpdate
from ..repositories.category import CategoryRepository
from ..repositories.household import HouseholdRepository
from .ownership import OwnershipService

# ---------------------------------------

class CategoryNotFoundError(Exception):
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"Category {category_id} not found")


class CategoryNameExistsError(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Category '{name}' already exists")


class CategoryInUseError(Exception):
    def __init__(self, name: str, transaction_count: int):
        self.name = name
        self.transaction_count = transaction_count
        super().__init__(
            f"Cannot delete category '{name}' - it is used by {transaction_count} transaction(s)"
        )


class CategoryAccessDeniedError(Exception):
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"Access denied to category {category_id}")


# ---------------------------------------


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repository: CategoryRepository = CategoryRepository(db)
        self.household_repository: HouseholdRepository = HouseholdRepository(db)
        self.ownership_service: OwnershipService = OwnershipService(db)
        self.db = db

    async def _resolve_household_id(self, household_uid: Optional[str]) -> Optional[int]:
        """Convert household UID (string) to household ID (int)."""
        if not household_uid:
            return None
        household = await self.household_repository.get_by_uid(household_uid)
        return household.id if household else None

    async def _get_accessible_category_ids(
        self,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> List[int]:
        """Get IDs of categories accessible to user (personal + optional household)."""
        user_ids = await self.ownership_service.get_user_entity_ids("category", user_id)

        if household_id:
            household_ids = await self.ownership_service.get_household_entity_ids(
                "category", household_id
            )
            return list(set(user_ids + household_ids))

        return user_ids

    async def _check_access(
        self,
        category_id: int,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> bool:
        """Check if user has access to a category (owns it or it's a default category)."""
        if await self.ownership_service.user_owns_entity("category", category_id, user_id):
            return True

        if household_id:
            if await self.ownership_service.household_owns_entity(
                "category", category_id, household_id
            ):
                return True

        # Check if it's a default category (not owned by anyone)
        # A category is default if it has no ownership record
        from sqlalchemy import select, exists
        from ..models import UserCategory, HouseholdCategory

        has_user_owner = await self.db.execute(
            select(exists().where(UserCategory.category_id == category_id))
        )
        has_household_owner = await self.db.execute(
            select(exists().where(HouseholdCategory.category_id == category_id))
        )

        if not has_user_owner.scalar() and not has_household_owner.scalar():
            # Default category - accessible to everyone
            return True

        return False

    async def list_categories(
        self,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> list[Category]:
        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        accessible_ids = await self._get_accessible_category_ids(user_id, household_id)
        return await self.repository.get_all(
            category_ids=accessible_ids,
            include_default=True,
        )

    async def get_category(
        self,
        category_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        if not await self._check_access(category_id, user_id, household_id):
            raise CategoryAccessDeniedError(category_id)

        return category

    async def create_category(
        self,
        data: CategoryCreate,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Category:
        if await self.repository.exists_by_name(data.name):
            raise CategoryNameExistsError(data.name)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        try:
            category = Category(**data.model_dump())
            created = await self.repository.create(category)

            # Create ownership record
            if household_id:
                await self.ownership_service.assign_to_household(
                    "category", created.id, household_id
                )
            else:
                await self.ownership_service.assign_to_user("category", created.id, user_id)

            return created

        except IntegrityError:
            await self.db.rollback()
            raise CategoryNameExistsError(data.name)

    async def update_category(
        self,
        category_id: int,
        data: CategoryUpdate,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        if not await self._check_access(category_id, user_id, household_id):
            raise CategoryAccessDeniedError(category_id)

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data:
            if await self.repository.exists_by_name(update_data["name"], exclude_id=category_id):
                raise CategoryNameExistsError(update_data["name"])

        for field, value in update_data.items():
            setattr(category, field, value)

        try:
            return await self.repository.update(category)

        except IntegrityError:
            await self.db.rollback()
            raise CategoryNameExistsError(update_data.get("name", ""))

    async def delete_category(
        self,
        category_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> None:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        if not await self._check_access(category_id, user_id, household_id):
            raise CategoryAccessDeniedError(category_id)

        transaction_count = await self.repository.count_transactions_by_category_name(category.name)
        if transaction_count > 0:
            raise CategoryInUseError(category.name, transaction_count)

        await self.repository.delete(category)
