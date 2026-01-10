from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.sql import false as sql_false
from typing import Optional, List, Tuple

from ..models import (
    Transaction,
    Category,
    Receipt,
    BudgetSettings,
    UserBudgetSettings,
    HouseholdBudgetSettings,
    HouseholdTransaction,
    User,
)


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_transactions_by_month(
        self,
        month: str,
        transaction_ids: Optional[List[int]] = None,
    ) -> list[Transaction]:
        query = select(Transaction).filter(Transaction.date.like(f"{month}%"))

        if transaction_ids is not None:
            if not transaction_ids:
                return []
            query = query.filter(Transaction.id.in_(transaction_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_transactions_by_year(
        self,
        year: str,
        transaction_ids: Optional[List[int]] = None,
    ) -> list[Transaction]:
        query = select(Transaction).filter(Transaction.date.like(f"{year}%"))

        if transaction_ids is not None:
            if not transaction_ids:
                return []
            query = query.filter(Transaction.id.in_(transaction_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_expenses_by_month(
        self,
        month: Optional[str] = None,
        transaction_ids: Optional[List[int]] = None,
    ) -> list[Transaction]:
        query = select(Transaction).filter(Transaction.amount < 0)

        if month:
            query = query.filter(Transaction.date.like(f"{month}%"))

        if transaction_ids is not None:
            if not transaction_ids:
                return []
            query = query.filter(Transaction.id.in_(transaction_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_expenses(
        self,
        category: Optional[str] = None,
        transaction_ids: Optional[List[int]] = None,
    ) -> list[Transaction]:
        query = select(Transaction).filter(Transaction.amount < 0)

        if category:
            query = query.filter(Transaction.category == category)

        if transaction_ids is not None:
            if not transaction_ids:
                return []
            query = query.filter(Transaction.id.in_(transaction_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_top_transactions(
        self,
        limit: int,
        month: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: str = "expenses",
        transaction_ids: Optional[List[int]] = None,
    ) -> list[Transaction]:
        query = select(Transaction)

        if month:
            query = query.filter(Transaction.date.like(f"{month}%"))

        if category:
            query = query.filter(Transaction.category == category)

        if transaction_ids is not None:
            if not transaction_ids:
                return []
            query = query.filter(Transaction.id.in_(transaction_ids))

        if transaction_type == "expenses":
            query = query.filter(Transaction.amount < 0)
            query = query.order_by(Transaction.amount.asc())
        else:
            query = query.filter(Transaction.amount > 0)
            query = query.order_by(Transaction.amount.desc())

        query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_categories_with_budget(self) -> list[Category]:
        result = await self.db.execute(
            select(Category).filter(Category.budget_limit.isnot(None))
        )
        return list(result.scalars().all())

    async def get_category_transactions(
        self,
        category_name: str,
        month: str,
        transaction_ids: Optional[List[int]] = None,
    ) -> list[Transaction]:
        query = select(Transaction).filter(
            and_(
                Transaction.category == category_name,
                Transaction.date.like(f"{month}%"),
                Transaction.amount < 0,
            )
        )

        if transaction_ids is not None:
            if not transaction_ids:
                return []
            query = query.filter(Transaction.id.in_(transaction_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_receipts_by_year(
        self,
        year: str,
        receipt_ids: Optional[List[int]] = None,
    ) -> list[Receipt]:
        query = select(Receipt).filter(Receipt.scan_date.like(f"{year}%"))

        if receipt_ids is not None:
            if not receipt_ids:
                return []
            query = query.filter(Receipt.id.in_(receipt_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_receipts_by_month(
        self,
        month: Optional[str] = None,
        receipt_ids: Optional[List[int]] = None,
    ) -> list[Receipt]:
        query = select(Receipt).filter(
            and_(
                Receipt.merchant.isnot(None),
                Receipt.total.isnot(None),
                Receipt.total > 0,
            )
        )

        if month:
            query = query.filter(Receipt.scan_date.like(f"{month}%"))

        if receipt_ids is not None:
            if not receipt_ids:
                return []
            query = query.filter(Receipt.id.in_(receipt_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_budget_settings(self, budget_settings_id: Optional[int] = None) -> BudgetSettings | None:
        if budget_settings_id:
            result = await self.db.execute(
                select(BudgetSettings).filter(BudgetSettings.id == budget_settings_id)
            )
        else:
            # Fallback to first settings (legacy behavior)
            result = await self.db.execute(select(BudgetSettings))
        return result.scalar_one_or_none()

    async def get_user_budget_settings(self, user_id: int) -> BudgetSettings | None:
        """Get budget settings owned by a user."""
        result = await self.db.execute(
            select(BudgetSettings).join(
                UserBudgetSettings,
                UserBudgetSettings.budget_settings_id == BudgetSettings.id
            ).filter(UserBudgetSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_household_budget_settings(self, household_id: int) -> BudgetSettings | None:
        """Get budget settings owned by a household."""
        result = await self.db.execute(
            select(BudgetSettings).join(
                HouseholdBudgetSettings,
                HouseholdBudgetSettings.budget_settings_id == BudgetSettings.id
            ).filter(HouseholdBudgetSettings.household_id == household_id)
        )
        return result.scalar_one_or_none()

    async def create_budget_settings(self, settings: BudgetSettings) -> BudgetSettings:
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def update_budget_settings(self, settings: BudgetSettings) -> BudgetSettings:
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    # ============================================================================
    # Household Analytics Methods
    # ============================================================================

    async def get_household_transactions(
        self,
        household_id: int,
        month: Optional[str] = None,
    ) -> List[Tuple[Transaction, Optional[User]]]:
        """Get household transactions with the user who added them."""
        query = (
            select(Transaction, User)
            .join(
                HouseholdTransaction,
                HouseholdTransaction.transaction_id == Transaction.id,
            )
            .outerjoin(User, HouseholdTransaction.added_by_user_id == User.id)
            .filter(HouseholdTransaction.household_id == household_id)
        )

        if month:
            query = query.filter(Transaction.date.like(f"{month}%"))

        result = await self.db.execute(query)
        return list(result.all())

    async def get_household_expenses(
        self,
        household_id: int,
        month: Optional[str] = None,
    ) -> List[Tuple[Transaction, Optional[User]]]:
        """Get household expenses with the user who added them."""
        query = (
            select(Transaction, User)
            .join(
                HouseholdTransaction,
                HouseholdTransaction.transaction_id == Transaction.id,
            )
            .outerjoin(User, HouseholdTransaction.added_by_user_id == User.id)
            .filter(HouseholdTransaction.household_id == household_id)
            .filter(Transaction.amount < 0)
        )

        if month:
            query = query.filter(Transaction.date.like(f"{month}%"))

        result = await self.db.execute(query)
        return list(result.all())
