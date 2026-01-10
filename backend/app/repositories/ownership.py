from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List

from ..models import (
    UserTransaction,
    HouseholdTransaction,
    UserReceipt,
    HouseholdReceipt,
    UserCategory,
    HouseholdCategory,
    UserBudgetSettings,
    HouseholdBudgetSettings,
    Transaction,
    Receipt,
    Category,
    BudgetSettings,
)


class UserOwnershipRepository:
    """Repository for user ownership junction tables."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Transaction ownership
    async def assign_transaction(self, user_id: int, transaction_id: int) -> UserTransaction:
        ownership = UserTransaction(user_id=user_id, transaction_id=transaction_id)
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_transaction_ownership(self, user_id: int, transaction_id: int) -> Optional[UserTransaction]:
        result = await self.db.execute(
            select(UserTransaction).where(
                and_(
                    UserTransaction.user_id == user_id,
                    UserTransaction.transaction_id == transaction_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_transactions(self, user_id: int) -> List[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .join(UserTransaction)
            .where(UserTransaction.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_transaction_ids(self, user_id: int) -> List[int]:
        result = await self.db.execute(
            select(UserTransaction.transaction_id).where(UserTransaction.user_id == user_id)
        )
        return list(result.scalars().all())

    async def remove_transaction_ownership(self, user_id: int, transaction_id: int) -> None:
        ownership = await self.get_transaction_ownership(user_id, transaction_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()

    # Receipt ownership
    async def assign_receipt(self, user_id: int, receipt_id: int) -> UserReceipt:
        ownership = UserReceipt(user_id=user_id, receipt_id=receipt_id)
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_receipt_ownership(self, user_id: int, receipt_id: int) -> Optional[UserReceipt]:
        result = await self.db.execute(
            select(UserReceipt).where(
                and_(
                    UserReceipt.user_id == user_id,
                    UserReceipt.receipt_id == receipt_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_receipts(self, user_id: int) -> List[Receipt]:
        result = await self.db.execute(
            select(Receipt)
            .join(UserReceipt)
            .where(UserReceipt.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_receipt_ids(self, user_id: int) -> List[int]:
        result = await self.db.execute(
            select(UserReceipt.receipt_id).where(UserReceipt.user_id == user_id)
        )
        return list(result.scalars().all())

    async def remove_receipt_ownership(self, user_id: int, receipt_id: int) -> None:
        ownership = await self.get_receipt_ownership(user_id, receipt_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()

    # Category ownership
    async def assign_category(self, user_id: int, category_id: int) -> UserCategory:
        ownership = UserCategory(user_id=user_id, category_id=category_id)
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_category_ownership(self, user_id: int, category_id: int) -> Optional[UserCategory]:
        result = await self.db.execute(
            select(UserCategory).where(
                and_(
                    UserCategory.user_id == user_id,
                    UserCategory.category_id == category_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_categories(self, user_id: int) -> List[Category]:
        result = await self.db.execute(
            select(Category)
            .join(UserCategory)
            .where(UserCategory.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_category_ids(self, user_id: int) -> List[int]:
        result = await self.db.execute(
            select(UserCategory.category_id).where(UserCategory.user_id == user_id)
        )
        return list(result.scalars().all())

    async def remove_category_ownership(self, user_id: int, category_id: int) -> None:
        ownership = await self.get_category_ownership(user_id, category_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()

    # Budget settings ownership
    async def assign_budget_settings(self, user_id: int, budget_settings_id: int) -> UserBudgetSettings:
        ownership = UserBudgetSettings(user_id=user_id, budget_settings_id=budget_settings_id)
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_budget_settings_ownership(self, user_id: int, budget_settings_id: int) -> Optional[UserBudgetSettings]:
        result = await self.db.execute(
            select(UserBudgetSettings).where(
                and_(
                    UserBudgetSettings.user_id == user_id,
                    UserBudgetSettings.budget_settings_id == budget_settings_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_budget_settings(self, user_id: int) -> Optional[BudgetSettings]:
        result = await self.db.execute(
            select(BudgetSettings)
            .join(UserBudgetSettings)
            .where(UserBudgetSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def remove_budget_settings_ownership(self, user_id: int, budget_settings_id: int) -> None:
        ownership = await self.get_budget_settings_ownership(user_id, budget_settings_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()


class HouseholdOwnershipRepository:
    """Repository for household ownership junction tables."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Transaction ownership
    async def assign_transaction(
        self, household_id: int, transaction_id: int, added_by_user_id: Optional[int] = None
    ) -> HouseholdTransaction:
        ownership = HouseholdTransaction(
            household_id=household_id,
            transaction_id=transaction_id,
            added_by_user_id=added_by_user_id,
        )
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_transaction_ownership(
        self, household_id: int, transaction_id: int
    ) -> Optional[HouseholdTransaction]:
        result = await self.db.execute(
            select(HouseholdTransaction).where(
                and_(
                    HouseholdTransaction.household_id == household_id,
                    HouseholdTransaction.transaction_id == transaction_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_household_transactions(self, household_id: int) -> List[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .join(HouseholdTransaction)
            .where(HouseholdTransaction.household_id == household_id)
        )
        return list(result.scalars().all())

    async def get_household_transaction_ids(self, household_id: int) -> List[int]:
        result = await self.db.execute(
            select(HouseholdTransaction.transaction_id).where(
                HouseholdTransaction.household_id == household_id
            )
        )
        return list(result.scalars().all())

    async def remove_transaction_ownership(self, household_id: int, transaction_id: int) -> None:
        ownership = await self.get_transaction_ownership(household_id, transaction_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()

    # Receipt ownership
    async def assign_receipt(
        self, household_id: int, receipt_id: int, added_by_user_id: Optional[int] = None
    ) -> HouseholdReceipt:
        ownership = HouseholdReceipt(
            household_id=household_id,
            receipt_id=receipt_id,
            added_by_user_id=added_by_user_id,
        )
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_receipt_ownership(
        self, household_id: int, receipt_id: int
    ) -> Optional[HouseholdReceipt]:
        result = await self.db.execute(
            select(HouseholdReceipt).where(
                and_(
                    HouseholdReceipt.household_id == household_id,
                    HouseholdReceipt.receipt_id == receipt_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_household_receipts(self, household_id: int) -> List[Receipt]:
        result = await self.db.execute(
            select(Receipt)
            .join(HouseholdReceipt)
            .where(HouseholdReceipt.household_id == household_id)
        )
        return list(result.scalars().all())

    async def get_household_receipt_ids(self, household_id: int) -> List[int]:
        result = await self.db.execute(
            select(HouseholdReceipt.receipt_id).where(
                HouseholdReceipt.household_id == household_id
            )
        )
        return list(result.scalars().all())

    async def remove_receipt_ownership(self, household_id: int, receipt_id: int) -> None:
        ownership = await self.get_receipt_ownership(household_id, receipt_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()

    # Category ownership
    async def assign_category(self, household_id: int, category_id: int) -> HouseholdCategory:
        ownership = HouseholdCategory(household_id=household_id, category_id=category_id)
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_category_ownership(
        self, household_id: int, category_id: int
    ) -> Optional[HouseholdCategory]:
        result = await self.db.execute(
            select(HouseholdCategory).where(
                and_(
                    HouseholdCategory.household_id == household_id,
                    HouseholdCategory.category_id == category_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_household_categories(self, household_id: int) -> List[Category]:
        result = await self.db.execute(
            select(Category)
            .join(HouseholdCategory)
            .where(HouseholdCategory.household_id == household_id)
        )
        return list(result.scalars().all())

    async def get_household_category_ids(self, household_id: int) -> List[int]:
        result = await self.db.execute(
            select(HouseholdCategory.category_id).where(
                HouseholdCategory.household_id == household_id
            )
        )
        return list(result.scalars().all())

    async def remove_category_ownership(self, household_id: int, category_id: int) -> None:
        ownership = await self.get_category_ownership(household_id, category_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()

    # Budget settings ownership
    async def assign_budget_settings(
        self, household_id: int, budget_settings_id: int
    ) -> HouseholdBudgetSettings:
        ownership = HouseholdBudgetSettings(
            household_id=household_id,
            budget_settings_id=budget_settings_id,
        )
        self.db.add(ownership)
        await self.db.commit()
        await self.db.refresh(ownership)
        return ownership

    async def get_budget_settings_ownership(
        self, household_id: int, budget_settings_id: int
    ) -> Optional[HouseholdBudgetSettings]:
        result = await self.db.execute(
            select(HouseholdBudgetSettings).where(
                and_(
                    HouseholdBudgetSettings.household_id == household_id,
                    HouseholdBudgetSettings.budget_settings_id == budget_settings_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_household_budget_settings(self, household_id: int) -> Optional[BudgetSettings]:
        result = await self.db.execute(
            select(BudgetSettings)
            .join(HouseholdBudgetSettings)
            .where(HouseholdBudgetSettings.household_id == household_id)
        )
        return result.scalar_one_or_none()

    async def remove_budget_settings_ownership(self, household_id: int, budget_settings_id: int) -> None:
        ownership = await self.get_budget_settings_ownership(household_id, budget_settings_id)
        if ownership:
            await self.db.delete(ownership)
            await self.db.commit()
