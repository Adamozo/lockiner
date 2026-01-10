from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from ..models import Category, Transaction, UserCategory, HouseholdCategory


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        category_ids: Optional[List[int]] = None,
        include_default: bool = True,
    ) -> list[Category]:
        query = select(Category)

        if category_ids is not None:
            if include_default:
                # Get default categories (not owned by anyone) + owned categories
                owned_category_ids_subquery = (
                    select(UserCategory.category_id).union(
                        select(HouseholdCategory.category_id)
                    )
                )
                query = query.filter(
                    or_(
                        Category.id.in_(category_ids),
                        ~Category.id.in_(owned_category_ids_subquery),
                    )
                )
            else:
                if not category_ids:
                    return []
                query = query.filter(Category.id.in_(category_ids))

        query = query.order_by(Category.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).filter(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.db.execute(
            select(Category).filter(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def exists_by_name(self, name: str, exclude_id: int | None = None) -> bool:
        query = select(Category).filter(Category.name == name)
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_transactions_by_category_name(self, category_name: str) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Transaction).filter(
                Transaction.category == category_name
            )
        )
        return result.scalar() or 0

    async def create(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category: Category) -> Category:
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.commit()
