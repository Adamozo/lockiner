"""Medicine/Supplement module repositories."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List

from ..models import Medicine, MedicineSchedule, MedicineLog


class MedicineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: int, active_only: bool = False) -> List[Medicine]:
        query = select(Medicine).options(
            selectinload(Medicine.schedules)
        ).filter(Medicine.user_id == user_id)

        if active_only:
            query = query.filter(Medicine.active == True)

        query = query.order_by(Medicine.name.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, medicine_id: int) -> Optional[Medicine]:
        result = await self.db.execute(
            select(Medicine)
            .options(selectinload(Medicine.schedules))
            .filter(Medicine.id == medicine_id)
        )
        return result.scalar_one_or_none()

    async def create(self, medicine: Medicine) -> Medicine:
        self.db.add(medicine)
        await self.db.commit()
        await self.db.refresh(medicine)
        return await self.get_by_id(medicine.id)

    async def update(self, medicine: Medicine) -> Medicine:
        await self.db.commit()
        await self.db.refresh(medicine)
        return await self.get_by_id(medicine.id)

    async def delete(self, medicine: Medicine) -> None:
        await self.db.delete(medicine)
        await self.db.commit()


class MedicineScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, schedule_id: int) -> Optional[MedicineSchedule]:
        result = await self.db.execute(
            select(MedicineSchedule).filter(MedicineSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_medicine(self, medicine_id: int) -> List[MedicineSchedule]:
        result = await self.db.execute(
            select(MedicineSchedule).filter(
                MedicineSchedule.medicine_id == medicine_id,
                MedicineSchedule.active == True,
            ).order_by(MedicineSchedule.time_of_day.asc())
        )
        return list(result.scalars().all())

    async def get_active_with_notifications(self) -> List[MedicineSchedule]:
        """Get all active schedules that have notifications enabled, with medicine loaded."""
        result = await self.db.execute(
            select(MedicineSchedule)
            .options(selectinload(MedicineSchedule.medicine))
            .filter(
                MedicineSchedule.active == True,
                MedicineSchedule.notifications_enabled == True,
            )
        )
        return list(result.scalars().all())

    async def create(self, schedule: MedicineSchedule) -> MedicineSchedule:
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def update(self, schedule: MedicineSchedule) -> MedicineSchedule:
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def delete(self, schedule: MedicineSchedule) -> None:
        await self.db.delete(schedule)
        await self.db.commit()


class MedicineLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, log_id: int) -> Optional[MedicineLog]:
        result = await self.db.execute(
            select(MedicineLog).filter(MedicineLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_for_date(
        self, medicine_id: int, schedule_id: int, scheduled_date: str, scheduled_time: str
    ) -> MedicineLog:
        """Get existing log or create a new one for a given schedule+date."""
        result = await self.db.execute(
            select(MedicineLog).filter(
                MedicineLog.schedule_id == schedule_id,
                MedicineLog.scheduled_date == scheduled_date,
            )
        )
        log = result.scalar_one_or_none()

        if log is None:
            log = MedicineLog(
                medicine_id=medicine_id,
                schedule_id=schedule_id,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
            )
            self.db.add(log)
            await self.db.commit()
            await self.db.refresh(log)

        return log

    async def get_logs_for_date(self, medicine_ids: List[int], date: str) -> List[MedicineLog]:
        if not medicine_ids:
            return []
        result = await self.db.execute(
            select(MedicineLog).filter(
                MedicineLog.medicine_id.in_(medicine_ids),
                MedicineLog.scheduled_date == date,
            ).order_by(MedicineLog.scheduled_time.asc())
        )
        return list(result.scalars().all())

    async def get_logs_for_date_range(
        self, medicine_ids: List[int], start_date: str, end_date: str
    ) -> List[MedicineLog]:
        if not medicine_ids:
            return []
        result = await self.db.execute(
            select(MedicineLog).filter(
                MedicineLog.medicine_id.in_(medicine_ids),
                MedicineLog.scheduled_date >= start_date,
                MedicineLog.scheduled_date <= end_date,
            )
        )
        return list(result.scalars().all())

    async def get_logs_by_medicine(
        self, medicine_id: int, skip: int = 0, limit: int = 50
    ) -> List[MedicineLog]:
        result = await self.db.execute(
            select(MedicineLog)
            .filter(MedicineLog.medicine_id == medicine_id)
            .order_by(MedicineLog.scheduled_date.desc(), MedicineLog.scheduled_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, log: MedicineLog) -> MedicineLog:
        await self.db.commit()
        await self.db.refresh(log)
        return log
