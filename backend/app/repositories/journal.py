from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List

from ..models.journal import JournalEntry, JournalItem, JournalReport


class JournalEntryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[JournalEntry]:
        query = select(JournalEntry).options(
            selectinload(JournalEntry.items)
        ).filter(JournalEntry.user_id == user_id)

        if start_date:
            query = query.filter(JournalEntry.date >= start_date)
        if end_date:
            query = query.filter(JournalEntry.date <= end_date)

        query = query.order_by(JournalEntry.date.desc(), JournalEntry.id.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entry_id: int) -> Optional[JournalEntry]:
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.items))
            .filter(JournalEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_date(self, user_id: int, date: str) -> Optional[JournalEntry]:
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.items))
            .filter(JournalEntry.user_id == user_id, JournalEntry.date == date)
        )
        return result.scalar_one_or_none()

    async def create(self, entry: JournalEntry) -> JournalEntry:
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return await self.get_by_id(entry.id)

    async def update(self, entry: JournalEntry) -> JournalEntry:
        await self.db.commit()
        await self.db.refresh(entry)
        return await self.get_by_id(entry.id)

    async def delete(self, entry: JournalEntry) -> None:
        await self.db.delete(entry)
        await self.db.commit()

    async def count_by_user(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(JournalEntry.id)).filter(JournalEntry.user_id == user_id)
        )
        return result.scalar() or 0

    async def count_by_user_and_date_range(
        self, user_id: int, start_date: str, end_date: str
    ) -> int:
        result = await self.db.execute(
            select(func.count(JournalEntry.id)).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date,
            )
        )
        return result.scalar() or 0

    async def get_all_dates(self, user_id: int) -> List[str]:
        """Get all entry dates for a user, ordered ascending."""
        result = await self.db.execute(
            select(JournalEntry.date)
            .filter(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.date.asc())
        )
        return [row[0] for row in result.all()]

    async def get_avg_mood(self, user_id: int) -> Optional[float]:
        result = await self.db.execute(
            select(func.avg(JournalEntry.mood_score)).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.mood_score.isnot(None),
            )
        )
        val = result.scalar()
        return round(float(val), 1) if val is not None else None

    async def get_avg_mood_in_range(
        self, user_id: int, start_date: str, end_date: str
    ) -> Optional[float]:
        result = await self.db.execute(
            select(func.avg(JournalEntry.mood_score)).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.mood_score.isnot(None),
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date,
            )
        )
        val = result.scalar()
        return round(float(val), 1) if val is not None else None


class JournalItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_entry_id(self, entry_id: int) -> List[JournalItem]:
        result = await self.db.execute(
            select(JournalItem).filter(JournalItem.entry_id == entry_id)
        )
        return list(result.scalars().all())

    async def delete_by_entry_id(self, entry_id: int) -> None:
        items = await self.get_by_entry_id(entry_id)
        for item in items:
            await self.db.delete(item)
        await self.db.commit()

    async def get_items_in_date_range(
        self, user_id: int, start_date: str, end_date: str
    ) -> List[JournalItem]:
        """Get all journal items for entries in a date range."""
        result = await self.db.execute(
            select(JournalItem)
            .join(JournalEntry, JournalItem.entry_id == JournalEntry.id)
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.date >= start_date,
                JournalEntry.date <= end_date,
            )
            .order_by(JournalItem.category, JournalItem.position)
        )
        return list(result.scalars().all())


class JournalReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_type_period(
        self, user_id: int, report_type: str, period: str
    ) -> Optional[JournalReport]:
        result = await self.db.execute(
            select(JournalReport).filter(
                JournalReport.user_id == user_id,
                JournalReport.report_type == report_type,
                JournalReport.period == period,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_type(
        self, user_id: int, report_type: str
    ) -> List[JournalReport]:
        result = await self.db.execute(
            select(JournalReport)
            .filter(
                JournalReport.user_id == user_id,
                JournalReport.report_type == report_type,
            )
            .order_by(JournalReport.period.desc())
        )
        return list(result.scalars().all())

    async def upsert(self, report: JournalReport) -> JournalReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def update(self, report: JournalReport) -> JournalReport:
        await self.db.commit()
        await self.db.refresh(report)
        return report
