from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from ..models import Receipt, Transaction


class ReceiptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        verified: Optional[bool] = None,
        receipt_ids: Optional[List[int]] = None,
    ) -> list[Receipt]:
        query = select(Receipt)

        # Filter by owned receipt IDs if provided
        if receipt_ids is not None:
            if not receipt_ids:
                return []  # No owned receipts
            query = query.filter(Receipt.id.in_(receipt_ids))

        if verified is not None:
            query = query.filter(Receipt.verified == verified)

        query = query.order_by(Receipt.scan_date.desc(), Receipt.id.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, receipt_id: int) -> Receipt | None:
        result = await self.db.execute(
            select(Receipt).filter(Receipt.id == receipt_id)
        )
        return result.scalar_one_or_none()

    async def create(self, receipt: Receipt) -> Receipt:
        self.db.add(receipt)
        await self.db.commit()
        await self.db.refresh(receipt)
        return receipt

    async def update(self, receipt: Receipt) -> Receipt:
        await self.db.commit()
        await self.db.refresh(receipt)
        return receipt

    async def delete(self, receipt: Receipt) -> None:
        await self.db.delete(receipt)
        await self.db.commit()

    async def get_transaction_by_receipt_id(self, receipt_id: int) -> Transaction | None:
        result = await self.db.execute(
            select(Transaction).filter(Transaction.receipt_id == receipt_id)
        )
        return result.scalar_one_or_none()

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction | None:
        result = await self.db.execute(
            select(Transaction).filter(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def save(self) -> None:
        await self.db.commit()
