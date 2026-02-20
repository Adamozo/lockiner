"""Shopping Lists module repositories."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List

from ..models.shopping import ShoppingList, ShoppingListItem
from ..models.household import HouseholdMember


class ShoppingListRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, list_id: int) -> Optional[ShoppingList]:
        result = await self.db.execute(
            select(ShoppingList)
            .options(selectinload(ShoppingList.items))
            .filter(ShoppingList.id == list_id)
        )
        return result.scalar_one_or_none()

    async def get_accessible_by_user(self, user_id: int, status: Optional[str] = None) -> List[ShoppingList]:
        """Return all lists owned by user plus household lists where user is an active member."""
        household_subq = (
            select(HouseholdMember.household_id)
            .where(
                HouseholdMember.user_id == user_id,
                HouseholdMember.status == "active",
            )
            .scalar_subquery()
        )
        stmt = (
            select(ShoppingList)
            .options(selectinload(ShoppingList.items))
            .where(
                or_(
                    ShoppingList.owner_id == user_id,
                    and_(
                        ShoppingList.visibility == "household",
                        ShoppingList.household_id.in_(household_subq),
                    ),
                )
            )
            .order_by(ShoppingList.created_at.desc())
        )
        if status:
            stmt = stmt.where(ShoppingList.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, shopping_list: ShoppingList) -> ShoppingList:
        self.db.add(shopping_list)
        await self.db.commit()
        await self.db.refresh(shopping_list)
        return await self.get_by_id(shopping_list.id)

    async def update(self, shopping_list: ShoppingList) -> ShoppingList:
        await self.db.commit()
        await self.db.refresh(shopping_list)
        return await self.get_by_id(shopping_list.id)

    async def delete(self, shopping_list: ShoppingList) -> None:
        await self.db.delete(shopping_list)
        await self.db.commit()


class ShoppingListItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, item_id: int) -> Optional[ShoppingListItem]:
        result = await self.db.execute(
            select(ShoppingListItem).filter(ShoppingListItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create(self, item: ShoppingListItem) -> ShoppingListItem:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update(self, item: ShoppingListItem) -> ShoppingListItem:
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, item: ShoppingListItem) -> None:
        await self.db.delete(item)
        await self.db.commit()
