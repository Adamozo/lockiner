from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import MonthlyImport


class ImportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[MonthlyImport]:
        result = await self.db.execute(
            select(MonthlyImport)
            .order_by(MonthlyImport.month.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, import_id: int) -> MonthlyImport | None:
        result = await self.db.execute(
            select(MonthlyImport).filter(MonthlyImport.id == import_id)
        )
        return result.scalar_one_or_none()

    async def get_by_month(self, month: str) -> MonthlyImport | None:
        result = await self.db.execute(
            select(MonthlyImport).filter(MonthlyImport.month == month)
        )
        return result.scalar_one_or_none()

    async def create(self, import_record: MonthlyImport) -> MonthlyImport:
        self.db.add(import_record)
        await self.db.commit()
        await self.db.refresh(import_record)
        return import_record

    async def delete(self, import_record: MonthlyImport) -> None:
        await self.db.delete(import_record)
        await self.db.commit()
