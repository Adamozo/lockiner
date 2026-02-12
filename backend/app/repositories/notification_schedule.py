"""Repository for notification schedule database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete as sa_delete
from typing import List, Optional

from ..models.notification import NotificationSchedule
from ..models.base import utc_now


REMINDER_TYPES = ["workout", "weight", "receipt", "finance"]


class NotificationScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_schedules(self, user_id: int) -> List[NotificationSchedule]:
        """Get all notification schedules for a user."""
        result = await self.db.execute(
            select(NotificationSchedule)
            .filter(NotificationSchedule.user_id == user_id)
            .order_by(NotificationSchedule.reminder_type)
        )
        return list(result.scalars().all())

    async def get_user_schedule_by_type(
        self, user_id: int, reminder_type: str
    ) -> Optional[NotificationSchedule]:
        """Get a specific schedule by user and reminder type."""
        result = await self.db.execute(
            select(NotificationSchedule).filter(
                NotificationSchedule.user_id == user_id,
                NotificationSchedule.reminder_type == reminder_type,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_schedule(
        self,
        user_id: int,
        reminder_type: str,
        enabled: bool,
        frequency: str,
        hour: int,
        minute: int,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
        custom_name: Optional[str] = None,
        custom_icon: Optional[str] = None,
        custom_title: Optional[str] = None,
        custom_body: Optional[str] = None,
    ) -> NotificationSchedule:
        """Create or update a notification schedule."""
        existing = await self.get_user_schedule_by_type(user_id, reminder_type)
        now = utc_now().isoformat()

        if existing:
            existing.enabled = enabled
            existing.frequency = frequency
            existing.hour = hour
            existing.minute = minute
            existing.day_of_week = day_of_week
            existing.day_of_month = day_of_month
            if custom_name is not None:
                existing.custom_name = custom_name
            if custom_icon is not None:
                existing.custom_icon = custom_icon
            if custom_title is not None:
                existing.custom_title = custom_title
            if custom_body is not None:
                existing.custom_body = custom_body
            existing.updated_at = now
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        schedule = NotificationSchedule(
            user_id=user_id,
            reminder_type=reminder_type,
            enabled=enabled,
            frequency=frequency,
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            custom_name=custom_name,
            custom_icon=custom_icon,
            custom_title=custom_title,
            custom_body=custom_body,
            created_at=now,
        )
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def create_default_schedule(
        self, user_id: int, reminder_type: str
    ) -> NotificationSchedule:
        """Create a disabled default schedule for a reminder type."""
        now = utc_now().isoformat()
        schedule = NotificationSchedule(
            user_id=user_id,
            reminder_type=reminder_type,
            enabled=False,
            frequency="daily",
            hour=9,
            minute=0,
            created_at=now,
        )
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def delete_schedule(self, user_id: int, reminder_type: str) -> bool:
        """Delete a schedule by user_id and reminder_type. Returns True if deleted."""
        result = await self.db.execute(
            sa_delete(NotificationSchedule).where(
                and_(
                    NotificationSchedule.user_id == user_id,
                    NotificationSchedule.reminder_type == reminder_type,
                )
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_due_schedules(
        self, frequency: str, hour: int, minute: int,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
    ) -> List[NotificationSchedule]:
        """Get all enabled schedules that are due right now."""
        conditions = [
            NotificationSchedule.enabled == True,
            NotificationSchedule.frequency == frequency,
            NotificationSchedule.hour == hour,
            NotificationSchedule.minute == minute,
        ]
        if frequency == "weekly" and day_of_week is not None:
            conditions.append(NotificationSchedule.day_of_week == day_of_week)
        elif frequency == "monthly" and day_of_month is not None:
            conditions.append(NotificationSchedule.day_of_month == day_of_month)

        result = await self.db.execute(
            select(NotificationSchedule).filter(and_(*conditions))
        )
        return list(result.scalars().all())
