from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Literal, Union

from ..models import (
    Transaction,
    Receipt,
    Category,
    BudgetSettings,
    UserTransaction,
    HouseholdTransaction,
    UserReceipt,
    HouseholdReceipt,
    UserCategory,
    HouseholdCategory,
    UserBudgetSettings,
    HouseholdBudgetSettings,
)
from ..repositories.ownership import UserOwnershipRepository, HouseholdOwnershipRepository

# ---------------------------------------

EntityType = Literal["transaction", "receipt", "category", "budget_settings"]


class InvalidEntityTypeError(Exception):
    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        super().__init__(f"Invalid entity type: {entity_type}")


class OwnershipAlreadyExistsError(Exception):
    def __init__(self, entity_type: str, entity_id: int, owner_type: str, owner_id: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.owner_type = owner_type
        self.owner_id = owner_id
        super().__init__(
            f"Ownership already exists: {entity_type}#{entity_id} -> {owner_type}#{owner_id}"
        )


# ---------------------------------------


class OwnershipService:
    """Service for managing entity ownership across users and households."""

    VALID_ENTITY_TYPES = ("transaction", "receipt", "category", "budget_settings")

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserOwnershipRepository(db)
        self.household_repo = HouseholdOwnershipRepository(db)

    def _validate_entity_type(self, entity_type: str) -> None:
        if entity_type not in self.VALID_ENTITY_TYPES:
            raise InvalidEntityTypeError(entity_type)

    # -----------------------------------------------------------------------
    # User Ownership
    # -----------------------------------------------------------------------

    async def assign_to_user(
        self,
        entity_type: EntityType,
        entity_id: int,
        user_id: int,
    ) -> Union[UserTransaction, UserReceipt, UserCategory, UserBudgetSettings]:
        """Assign an entity to a user."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            # Check if already owned
            existing = await self.user_repo.get_transaction_ownership(user_id, entity_id)
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "user", user_id)
            return await self.user_repo.assign_transaction(user_id, entity_id)

        elif entity_type == "receipt":
            existing = await self.user_repo.get_receipt_ownership(user_id, entity_id)
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "user", user_id)
            return await self.user_repo.assign_receipt(user_id, entity_id)

        elif entity_type == "category":
            existing = await self.user_repo.get_category_ownership(user_id, entity_id)
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "user", user_id)
            return await self.user_repo.assign_category(user_id, entity_id)

        elif entity_type == "budget_settings":
            existing = await self.user_repo.get_budget_settings_ownership(user_id, entity_id)
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "user", user_id)
            return await self.user_repo.assign_budget_settings(user_id, entity_id)

    async def remove_from_user(
        self,
        entity_type: EntityType,
        entity_id: int,
        user_id: int,
    ) -> None:
        """Remove entity ownership from a user."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            await self.user_repo.remove_transaction_ownership(user_id, entity_id)
        elif entity_type == "receipt":
            await self.user_repo.remove_receipt_ownership(user_id, entity_id)
        elif entity_type == "category":
            await self.user_repo.remove_category_ownership(user_id, entity_id)
        elif entity_type == "budget_settings":
            await self.user_repo.remove_budget_settings_ownership(user_id, entity_id)

    async def get_user_entities(
        self,
        entity_type: EntityType,
        user_id: int,
    ) -> List[Union[Transaction, Receipt, Category, BudgetSettings]]:
        """Get all entities of a type owned by a user."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            return await self.user_repo.get_user_transactions(user_id)
        elif entity_type == "receipt":
            return await self.user_repo.get_user_receipts(user_id)
        elif entity_type == "category":
            return await self.user_repo.get_user_categories(user_id)
        elif entity_type == "budget_settings":
            result = await self.user_repo.get_user_budget_settings(user_id)
            return [result] if result else []

    async def get_user_entity_ids(
        self,
        entity_type: EntityType,
        user_id: int,
    ) -> List[int]:
        """Get IDs of all entities of a type owned by a user."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            return await self.user_repo.get_user_transaction_ids(user_id)
        elif entity_type == "receipt":
            return await self.user_repo.get_user_receipt_ids(user_id)
        elif entity_type == "category":
            return await self.user_repo.get_user_category_ids(user_id)
        elif entity_type == "budget_settings":
            result = await self.user_repo.get_user_budget_settings(user_id)
            return [result.id] if result else []

    async def user_owns_entity(
        self,
        entity_type: EntityType,
        entity_id: int,
        user_id: int,
    ) -> bool:
        """Check if a user owns a specific entity."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            ownership = await self.user_repo.get_transaction_ownership(user_id, entity_id)
        elif entity_type == "receipt":
            ownership = await self.user_repo.get_receipt_ownership(user_id, entity_id)
        elif entity_type == "category":
            ownership = await self.user_repo.get_category_ownership(user_id, entity_id)
        elif entity_type == "budget_settings":
            ownership = await self.user_repo.get_budget_settings_ownership(user_id, entity_id)

        return ownership is not None

    # -----------------------------------------------------------------------
    # Household Ownership
    # -----------------------------------------------------------------------

    async def assign_to_household(
        self,
        entity_type: EntityType,
        entity_id: int,
        household_id: int,
        added_by: Optional[int] = None,
    ) -> Union[HouseholdTransaction, HouseholdReceipt, HouseholdCategory, HouseholdBudgetSettings]:
        """Assign an entity to a household."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            existing = await self.household_repo.get_transaction_ownership(household_id, entity_id)
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "household", household_id)
            return await self.household_repo.assign_transaction(household_id, entity_id, added_by)

        elif entity_type == "receipt":
            existing = await self.household_repo.get_receipt_ownership(household_id, entity_id)
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "household", household_id)
            return await self.household_repo.assign_receipt(household_id, entity_id, added_by)

        elif entity_type == "category":
            existing = await self.household_repo.get_category_ownership(household_id, entity_id)
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "household", household_id)
            return await self.household_repo.assign_category(household_id, entity_id)

        elif entity_type == "budget_settings":
            existing = await self.household_repo.get_budget_settings_ownership(
                household_id, entity_id
            )
            if existing:
                raise OwnershipAlreadyExistsError(entity_type, entity_id, "household", household_id)
            return await self.household_repo.assign_budget_settings(household_id, entity_id)

    async def remove_from_household(
        self,
        entity_type: EntityType,
        entity_id: int,
        household_id: int,
    ) -> None:
        """Remove entity ownership from a household."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            await self.household_repo.remove_transaction_ownership(household_id, entity_id)
        elif entity_type == "receipt":
            await self.household_repo.remove_receipt_ownership(household_id, entity_id)
        elif entity_type == "category":
            await self.household_repo.remove_category_ownership(household_id, entity_id)
        elif entity_type == "budget_settings":
            await self.household_repo.remove_budget_settings_ownership(household_id, entity_id)

    async def get_household_entities(
        self,
        entity_type: EntityType,
        household_id: int,
    ) -> List[Union[Transaction, Receipt, Category, BudgetSettings]]:
        """Get all entities of a type owned by a household."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            return await self.household_repo.get_household_transactions(household_id)
        elif entity_type == "receipt":
            return await self.household_repo.get_household_receipts(household_id)
        elif entity_type == "category":
            return await self.household_repo.get_household_categories(household_id)
        elif entity_type == "budget_settings":
            result = await self.household_repo.get_household_budget_settings(household_id)
            return [result] if result else []

    async def get_household_entity_ids(
        self,
        entity_type: EntityType,
        household_id: int,
    ) -> List[int]:
        """Get IDs of all entities of a type owned by a household."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            return await self.household_repo.get_household_transaction_ids(household_id)
        elif entity_type == "receipt":
            return await self.household_repo.get_household_receipt_ids(household_id)
        elif entity_type == "category":
            return await self.household_repo.get_household_category_ids(household_id)
        elif entity_type == "budget_settings":
            result = await self.household_repo.get_household_budget_settings(household_id)
            return [result.id] if result else []

    async def household_owns_entity(
        self,
        entity_type: EntityType,
        entity_id: int,
        household_id: int,
    ) -> bool:
        """Check if a household owns a specific entity."""
        self._validate_entity_type(entity_type)

        if entity_type == "transaction":
            ownership = await self.household_repo.get_transaction_ownership(household_id, entity_id)
        elif entity_type == "receipt":
            ownership = await self.household_repo.get_receipt_ownership(household_id, entity_id)
        elif entity_type == "category":
            ownership = await self.household_repo.get_category_ownership(household_id, entity_id)
        elif entity_type == "budget_settings":
            ownership = await self.household_repo.get_budget_settings_ownership(
                household_id, entity_id
            )

        return ownership is not None
