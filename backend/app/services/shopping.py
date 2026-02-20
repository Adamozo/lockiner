"""Shopping Lists module service layer."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from ..models.shopping import ShoppingList, ShoppingListItem
from ..models.household import HouseholdMember
from ..models import utc_now
from ..schemas.shopping import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingItemStatusUpdate,
    ShoppingListSummaryResponse,
)
from ..repositories.shopping import ShoppingListRepository, ShoppingListItemRepository


# ============================================================
# Custom exceptions
# ============================================================

class ShoppingListNotFoundError(Exception):
    def __init__(self, list_id):
        super().__init__(f"Shopping list {list_id} not found")


class ShoppingItemNotFoundError(Exception):
    def __init__(self, item_id):
        super().__init__(f"Shopping list item {item_id} not found")


class ShoppingAccessDeniedError(Exception):
    def __init__(self, list_id):
        super().__init__(f"Access denied to shopping list {list_id}")


class ShoppingInvalidHouseholdError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


# ============================================================
# Service
# ============================================================

class ShoppingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.list_repo = ShoppingListRepository(db)
        self.item_repo = ShoppingListItemRepository(db)

    # ----------------------------------------------------------
    # Access control helpers
    # ----------------------------------------------------------

    async def _check_access(self, shopping_list: ShoppingList, user_id: int) -> None:
        """Read/write access: owner for private lists, any active household member for household lists."""
        if shopping_list.visibility == "private":
            if shopping_list.owner_id != user_id:
                raise ShoppingAccessDeniedError(shopping_list.id)
        elif shopping_list.visibility == "household":
            if not await self._is_household_member(shopping_list.household_id, user_id):
                raise ShoppingAccessDeniedError(shopping_list.id)

    async def _check_owner(self, shopping_list: ShoppingList, user_id: int) -> None:
        """Owner-only actions: delete list, change visibility/household."""
        if shopping_list.owner_id != user_id:
            raise ShoppingAccessDeniedError(shopping_list.id)

    async def _is_household_member(self, household_id: Optional[int], user_id: int) -> bool:
        if household_id is None:
            return False
        result = await self.db.execute(
            select(HouseholdMember).where(
                HouseholdMember.household_id == household_id,
                HouseholdMember.user_id == user_id,
                HouseholdMember.status == "active",
            )
        )
        return result.scalar_one_or_none() is not None

    # ----------------------------------------------------------
    # Lists
    # ----------------------------------------------------------

    async def get_lists(self, user_id: int, status: Optional[str] = None) -> List[ShoppingListSummaryResponse]:
        lists = await self.list_repo.get_accessible_by_user(user_id, status)
        return [self._to_summary(lst) for lst in lists]

    async def get_list(self, list_id: int, user_id: int) -> ShoppingList:
        shopping_list = await self.list_repo.get_by_id(list_id)
        if shopping_list is None:
            raise ShoppingListNotFoundError(list_id)
        await self._check_access(shopping_list, user_id)
        return shopping_list

    async def create_list(self, data: ShoppingListCreate, user_id: int) -> ShoppingList:
        if data.visibility == "household":
            if data.household_id is None:
                raise ShoppingInvalidHouseholdError("household_id is required when visibility is 'household'")
            if not await self._is_household_member(data.household_id, user_id):
                raise ShoppingInvalidHouseholdError("User is not an active member of the specified household")

        shopping_list = ShoppingList(
            owner_id=user_id,
            household_id=data.household_id,
            visibility=data.visibility,
            name=data.name,
            store_name=data.store_name,
            planned_date=data.planned_date,
            notes=data.notes,
        )
        return await self.list_repo.create(shopping_list)

    async def update_list(self, list_id: int, data: ShoppingListUpdate, user_id: int) -> ShoppingList:
        shopping_list = await self.list_repo.get_by_id(list_id)
        if shopping_list is None:
            raise ShoppingListNotFoundError(list_id)
        await self._check_access(shopping_list, user_id)

        # Changing visibility or household requires owner
        if data.visibility is not None or data.household_id is not None:
            await self._check_owner(shopping_list, user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(shopping_list, field, value)
        shopping_list.updated_at = utc_now().isoformat()
        return await self.list_repo.update(shopping_list)

    async def delete_list(self, list_id: int, user_id: int) -> None:
        shopping_list = await self.list_repo.get_by_id(list_id)
        if shopping_list is None:
            raise ShoppingListNotFoundError(list_id)
        await self._check_owner(shopping_list, user_id)
        await self.list_repo.delete(shopping_list)

    async def complete_list(self, list_id: int, user_id: int) -> ShoppingList:
        shopping_list = await self.list_repo.get_by_id(list_id)
        if shopping_list is None:
            raise ShoppingListNotFoundError(list_id)
        await self._check_access(shopping_list, user_id)
        shopping_list.status = "completed"
        shopping_list.updated_at = utc_now().isoformat()
        return await self.list_repo.update(shopping_list)

    # ----------------------------------------------------------
    # Items
    # ----------------------------------------------------------

    async def add_item(self, list_id: int, data: ShoppingListItemCreate, user_id: int) -> ShoppingListItem:
        shopping_list = await self.list_repo.get_by_id(list_id)
        if shopping_list is None:
            raise ShoppingListNotFoundError(list_id)
        await self._check_access(shopping_list, user_id)

        auto_position = data.position
        if auto_position == 0 and shopping_list.items:
            auto_position = max(i.position for i in shopping_list.items) + 1

        item = ShoppingListItem(
            list_id=list_id,
            added_by=user_id,
            food_product_id=data.food_product_id,
            name=data.name,
            quantity=data.quantity,
            unit=data.unit,
            category=data.category,
            notes=data.notes,
            position=auto_position,
            is_recurring=data.is_recurring,
        )
        return await self.item_repo.create(item)

    async def update_item(self, item_id: int, data: ShoppingListItemUpdate, user_id: int) -> ShoppingListItem:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise ShoppingItemNotFoundError(item_id)
        shopping_list = await self.list_repo.get_by_id(item.list_id)
        await self._check_access(shopping_list, user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        item.updated_at = utc_now().isoformat()
        return await self.item_repo.update(item)

    async def update_item_status(self, item_id: int, data: ShoppingItemStatusUpdate, user_id: int) -> ShoppingListItem:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise ShoppingItemNotFoundError(item_id)
        shopping_list = await self.list_repo.get_by_id(item.list_id)
        await self._check_access(shopping_list, user_id)
        item.status = data.status
        item.updated_at = utc_now().isoformat()
        return await self.item_repo.update(item)

    async def delete_item(self, item_id: int, user_id: int) -> None:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise ShoppingItemNotFoundError(item_id)
        shopping_list = await self.list_repo.get_by_id(item.list_id)
        await self._check_access(shopping_list, user_id)
        await self.item_repo.delete(item)

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    @staticmethod
    def _to_summary(lst: ShoppingList) -> ShoppingListSummaryResponse:
        items = lst.items or []
        return ShoppingListSummaryResponse(
            id=lst.id,
            owner_id=lst.owner_id,
            household_id=lst.household_id,
            visibility=lst.visibility,
            name=lst.name,
            store_name=lst.store_name,
            planned_date=lst.planned_date,
            status=lst.status,
            total_items=len(items),
            pending_items=sum(1 for i in items if i.status == "pending"),
            in_cart_items=sum(1 for i in items if i.status == "in_cart"),
            purchased_items=sum(1 for i in items if i.status == "purchased"),
            created_at=lst.created_at,
        )
