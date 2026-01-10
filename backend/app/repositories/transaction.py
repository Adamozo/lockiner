from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, List

from ..models import Transaction


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        month: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        transaction_ids: Optional[List[int]] = None,
    ) -> list[Transaction]:
        query = select(Transaction)

        # Filter by owned transaction IDs if provided
        if transaction_ids is not None:
            if not transaction_ids:
                return []  # No owned transactions
            query = query.filter(Transaction.id.in_(transaction_ids))

        if month:
            query = query.filter(Transaction.date.like(f"{month}%"))

        if category:
            query = query.filter(Transaction.category == category)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.description.ilike(search_term),
                    Transaction.notes.ilike(search_term),
                )
            )

        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)

        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)

        query = query.order_by(Transaction.date.desc(), Transaction.id.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        result = await self.db.execute(
            select(Transaction).filter(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def update(self, transaction: Transaction) -> Transaction:
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def delete(self, transaction: Transaction) -> None:
        await self.db.delete(transaction)
        await self.db.commit()
