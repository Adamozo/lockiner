from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from ..models import Transaction
from ..schemas import TransactionCreate, TransactionUpdate
from ..repositories.transaction import TransactionRepository
from ..repositories.household import HouseholdRepository
from .ownership import OwnershipService

# ---------------------------------------


class TransactionNotFoundError(Exception):
    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id
        super().__init__(f"Transaction {transaction_id} not found")


class TransactionAccessDeniedError(Exception):
    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id
        super().__init__(f"Access denied to transaction {transaction_id}")


class InvalidDateFormatError(Exception):
    def __init__(self, date: str):
        self.date = date
        super().__init__("Invalid date format. Use ISO 8601 format (YYYY-MM-DD)")


# ---------------------------------------


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.repository: TransactionRepository = TransactionRepository(db)
        self.household_repository: HouseholdRepository = HouseholdRepository(db)
        self.ownership_service: OwnershipService = OwnershipService(db)
        self.db = db

    async def _resolve_household_id(self, household_uid: Optional[str]) -> Optional[int]:
        """Convert household UID (string) to household ID (int)."""
        if not household_uid:
            return None
        household = await self.household_repository.get_by_uid(household_uid)
        return household.id if household else None

    async def _get_accessible_transaction_ids(
        self,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> List[int]:
        """Get IDs of transactions accessible to user (personal + optional household)."""
        user_ids = await self.ownership_service.get_user_entity_ids("transaction", user_id)

        if household_id:
            household_ids = await self.ownership_service.get_household_entity_ids(
                "transaction", household_id
            )
            # Combine and dedupe
            return list(set(user_ids + household_ids))

        return user_ids

    async def _check_access(
        self,
        transaction_id: int,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> bool:
        """Check if user has access to a transaction."""
        if await self.ownership_service.user_owns_entity("transaction", transaction_id, user_id):
            return True

        if household_id:
            if await self.ownership_service.household_owns_entity(
                "transaction", transaction_id, household_id
            ):
                return True

        return False

    async def list_transactions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        month: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        household_uid: Optional[str] = None,
    ) -> list[Transaction]:
        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible transaction IDs
        accessible_ids = await self._get_accessible_transaction_ids(user_id, household_id)

        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            month=month,
            category=category,
            search=search,
            min_amount=min_amount,
            max_amount=max_amount,
            transaction_ids=accessible_ids,
        )

    async def get_transaction(
        self,
        transaction_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Transaction:
        transaction = await self.repository.get_by_id(transaction_id)
        if transaction is None:
            raise TransactionNotFoundError(transaction_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Check ownership
        if not await self._check_access(transaction_id, user_id, household_id):
            raise TransactionAccessDeniedError(transaction_id)

        return transaction

    async def create_transaction(
        self,
        data: TransactionCreate,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Transaction:
        if not data.date or len(data.date) < 10:
            raise InvalidDateFormatError(data.date or "")

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        try:
            transaction = Transaction(**data.model_dump())
            created = await self.repository.create(transaction)

            # Create ownership record
            if household_id:
                await self.ownership_service.assign_to_household(
                    "transaction", created.id, household_id, added_by=user_id
                )
            else:
                await self.ownership_service.assign_to_user("transaction", created.id, user_id)

            return created

        except IntegrityError:
            await self.db.rollback()
            raise

    async def update_transaction(
        self,
        transaction_id: int,
        data: TransactionUpdate,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Transaction:
        transaction = await self.repository.get_by_id(transaction_id)
        if transaction is None:
            raise TransactionNotFoundError(transaction_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Check ownership
        if not await self._check_access(transaction_id, user_id, household_id):
            raise TransactionAccessDeniedError(transaction_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)

        try:
            return await self.repository.update(transaction)

        except IntegrityError:
            await self.db.rollback()
            raise

    async def delete_transaction(
        self,
        transaction_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> None:
        transaction = await self.repository.get_by_id(transaction_id)
        if transaction is None:
            raise TransactionNotFoundError(transaction_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Check ownership
        if not await self._check_access(transaction_id, user_id, household_id):
            raise TransactionAccessDeniedError(transaction_id)

        await self.repository.delete(transaction)
