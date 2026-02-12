"""Notification schedule service - manages per-user reminder configurations."""

import logging
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.notification_schedule import NotificationScheduleRepository, REMINDER_TYPES
from ..models.notification import NotificationSchedule

logger = logging.getLogger(__name__)


class NotificationScheduleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationScheduleRepository(db)

    async def get_user_schedules(self, user_id: int) -> List[NotificationSchedule]:
        """Get all schedules for a user, auto-creating missing built-in ones."""
        existing = await self.repo.get_user_schedules(user_id)
        existing_types = {s.reminder_type for s in existing}

        for rt in REMINDER_TYPES:
            if rt not in existing_types:
                schedule = await self.repo.create_default_schedule(user_id, rt)
                existing.append(schedule)

        # Sort: built-ins first in defined order, then custom sorted alphabetically
        type_order = {t: i for i, t in enumerate(REMINDER_TYPES)}
        existing.sort(key=lambda s: (
            type_order.get(s.reminder_type, len(REMINDER_TYPES)),
            s.custom_name or s.reminder_type,
        ))
        return existing

    async def update_schedule(
        self,
        user_id: int,
        reminder_type: str,
        enabled: Optional[bool] = None,
        frequency: Optional[str] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
    ) -> NotificationSchedule:
        """Update a single schedule, merging provided fields with existing values."""
        existing = await self.repo.get_user_schedule_by_type(user_id, reminder_type)
        if existing is None:
            existing = await self.repo.create_default_schedule(user_id, reminder_type)

        final_enabled = enabled if enabled is not None else existing.enabled
        final_frequency = frequency if frequency is not None else existing.frequency
        final_hour = hour if hour is not None else existing.hour
        final_minute = minute if minute is not None else existing.minute
        final_day_of_week = day_of_week if day_of_week is not None else existing.day_of_week
        final_day_of_month = day_of_month if day_of_month is not None else existing.day_of_month

        # Auto-clean based on frequency
        if final_frequency == "daily":
            final_day_of_week = None
            final_day_of_month = None
        elif final_frequency == "weekly":
            final_day_of_month = None
            if final_day_of_week is None:
                final_day_of_week = 0
        elif final_frequency == "monthly":
            final_day_of_week = None
            if final_day_of_month is None:
                final_day_of_month = 1

        return await self.repo.upsert_schedule(
            user_id=user_id,
            reminder_type=reminder_type,
            enabled=final_enabled,
            frequency=final_frequency,
            hour=final_hour,
            minute=final_minute,
            day_of_week=final_day_of_week,
            day_of_month=final_day_of_month,
        )

    async def bulk_update_schedules(
        self, user_id: int, schedules_data: list
    ) -> List[NotificationSchedule]:
        """Bulk update all schedules from a list of schema objects."""
        results = []
        for data in schedules_data:
            kwargs = dict(
                user_id=user_id,
                reminder_type=data.reminder_type,
                enabled=data.enabled,
                frequency=data.frequency,
                hour=data.hour,
                minute=data.minute,
                day_of_week=data.day_of_week,
                day_of_month=data.day_of_month,
            )
            # Pass custom fields if present (for custom reminders)
            if hasattr(data, 'custom_name') and data.custom_name is not None:
                kwargs['custom_name'] = data.custom_name
            if hasattr(data, 'custom_icon') and data.custom_icon is not None:
                kwargs['custom_icon'] = data.custom_icon
            if hasattr(data, 'custom_title') and data.custom_title is not None:
                kwargs['custom_title'] = data.custom_title
            if hasattr(data, 'custom_body') and data.custom_body is not None:
                kwargs['custom_body'] = data.custom_body
            schedule = await self.repo.upsert_schedule(**kwargs)
            results.append(schedule)
        return results

    async def create_custom_reminder(
        self,
        user_id: int,
        custom_name: str,
        custom_icon: str,
        custom_title: str,
        custom_body: str,
        enabled: bool = True,
        frequency: str = "daily",
        hour: int = 9,
        minute: int = 0,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
    ) -> NotificationSchedule:
        """Create a new custom reminder with a unique type key."""
        reminder_type = f"custom_{uuid4().hex[:8]}"
        return await self.repo.upsert_schedule(
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
        )

    async def delete_custom_reminder(self, user_id: int, reminder_type: str) -> bool:
        """Delete a custom reminder. Rejects built-in types."""
        if not reminder_type.startswith("custom_"):
            return False
        return await self.repo.delete_schedule(user_id, reminder_type)
