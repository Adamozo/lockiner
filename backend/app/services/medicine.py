"""Medicine/Supplement module service layer."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timezone, timedelta, date

from ..models import Medicine, MedicineSchedule, MedicineLog, utc_now
from ..schemas.medicine import (
    MedicineCreate,
    MedicineUpdate,
    MedicineScheduleCreate,
    MedicineScheduleUpdate,
    MedicineLogMarkTaken,
    TodayDoseResponse,
    MedicineStatsResponse,
)
from ..repositories.medicine import (
    MedicineRepository,
    MedicineScheduleRepository,
    MedicineLogRepository,
)

# ---------------------------------------


class MedicineNotFoundError(Exception):
    def __init__(self, medicine_id: int):
        self.medicine_id = medicine_id
        super().__init__(f"Medicine {medicine_id} not found")


class MedicineScheduleNotFoundError(Exception):
    def __init__(self, schedule_id: int):
        self.schedule_id = schedule_id
        super().__init__(f"Medicine schedule {schedule_id} not found")


class MedicineLogNotFoundError(Exception):
    def __init__(self, log_id: int):
        self.log_id = log_id
        super().__init__(f"Medicine log {log_id} not found")


class MedicineAccessDeniedError(Exception):
    def __init__(self, resource_type: str, resource_id: int):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"Access denied to {resource_type} {resource_id}")


# ---------------------------------------


class MedicineService:
    def __init__(self, db: AsyncSession):
        self.medicine_repo = MedicineRepository(db)
        self.schedule_repo = MedicineScheduleRepository(db)
        self.log_repo = MedicineLogRepository(db)
        self.db = db

    # --- Medicines ---

    async def list_medicines(self, user_id: int) -> List[Medicine]:
        return await self.medicine_repo.get_all(user_id=user_id)

    async def get_medicine(self, medicine_id: int, user_id: int) -> Medicine:
        medicine = await self.medicine_repo.get_by_id(medicine_id)
        if medicine is None:
            raise MedicineNotFoundError(medicine_id)
        if medicine.user_id != user_id:
            raise MedicineAccessDeniedError("medicine", medicine_id)
        return medicine

    async def create_medicine(self, data: MedicineCreate, user_id: int) -> Medicine:
        medicine = Medicine(
            user_id=user_id,
            name=data.name,
            description=data.description,
            dosage=data.dosage,
            unit=data.unit,
            color=data.color,
            icon=data.icon,
        )

        if data.schedules:
            for sched_data in data.schedules:
                schedule = MedicineSchedule(
                    frequency_type=sched_data.frequency_type,
                    frequency_value=sched_data.frequency_value,
                    time_of_day=sched_data.time_of_day,
                    days_of_week=sched_data.days_of_week,
                    day_of_month=sched_data.day_of_month,
                    notifications_enabled=sched_data.notifications_enabled,
                )
                medicine.schedules.append(schedule)

        return await self.medicine_repo.create(medicine)

    async def update_medicine(self, medicine_id: int, data: MedicineUpdate, user_id: int) -> Medicine:
        medicine = await self.medicine_repo.get_by_id(medicine_id)
        if medicine is None:
            raise MedicineNotFoundError(medicine_id)
        if medicine.user_id != user_id:
            raise MedicineAccessDeniedError("medicine", medicine_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(medicine, field, value)

        medicine.updated_at = utc_now().isoformat()
        return await self.medicine_repo.update(medicine)

    async def delete_medicine(self, medicine_id: int, user_id: int) -> None:
        medicine = await self.medicine_repo.get_by_id(medicine_id)
        if medicine is None:
            raise MedicineNotFoundError(medicine_id)
        if medicine.user_id != user_id:
            raise MedicineAccessDeniedError("medicine", medicine_id)
        await self.medicine_repo.delete(medicine)

    # --- Schedules ---

    async def add_schedule(self, medicine_id: int, data: MedicineScheduleCreate, user_id: int) -> MedicineSchedule:
        medicine = await self.medicine_repo.get_by_id(medicine_id)
        if medicine is None:
            raise MedicineNotFoundError(medicine_id)
        if medicine.user_id != user_id:
            raise MedicineAccessDeniedError("medicine", medicine_id)

        schedule = MedicineSchedule(
            medicine_id=medicine_id,
            frequency_type=data.frequency_type,
            frequency_value=data.frequency_value,
            time_of_day=data.time_of_day,
            days_of_week=data.days_of_week,
            day_of_month=data.day_of_month,
            notifications_enabled=data.notifications_enabled,
        )
        return await self.schedule_repo.create(schedule)

    async def update_schedule(self, schedule_id: int, data: MedicineScheduleUpdate, user_id: int) -> MedicineSchedule:
        schedule = await self.schedule_repo.get_by_id(schedule_id)
        if schedule is None:
            raise MedicineScheduleNotFoundError(schedule_id)

        # Verify ownership via medicine
        medicine = await self.medicine_repo.get_by_id(schedule.medicine_id)
        if medicine is None or medicine.user_id != user_id:
            raise MedicineAccessDeniedError("schedule", schedule_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        schedule.updated_at = utc_now().isoformat()
        return await self.schedule_repo.update(schedule)

    async def delete_schedule(self, schedule_id: int, user_id: int) -> None:
        schedule = await self.schedule_repo.get_by_id(schedule_id)
        if schedule is None:
            raise MedicineScheduleNotFoundError(schedule_id)

        medicine = await self.medicine_repo.get_by_id(schedule.medicine_id)
        if medicine is None or medicine.user_id != user_id:
            raise MedicineAccessDeniedError("schedule", schedule_id)

        await self.schedule_repo.delete(schedule)

    # --- Today's Doses ---

    async def get_today_doses(self, user_id: int) -> List[TodayDoseResponse]:
        """Materialize today's doses from active schedules and return flattened list."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_date = date.fromisoformat(today_str)

        medicines = await self.medicine_repo.get_all(user_id=user_id, active_only=True)
        doses: List[TodayDoseResponse] = []

        for medicine in medicines:
            for schedule in medicine.schedules:
                if not schedule.active:
                    continue

                if not self._is_schedule_due_on_date(schedule, today_date):
                    continue

                log = await self.log_repo.get_or_create_for_date(
                    medicine_id=medicine.id,
                    schedule_id=schedule.id,
                    scheduled_date=today_str,
                    scheduled_time=schedule.time_of_day,
                )

                doses.append(TodayDoseResponse(
                    log_id=log.id,
                    medicine_id=medicine.id,
                    medicine_name=medicine.name,
                    medicine_color=medicine.color,
                    medicine_icon=medicine.icon,
                    dosage=medicine.dosage,
                    unit=medicine.unit,
                    scheduled_time=schedule.time_of_day,
                    taken=log.taken,
                    taken_at=log.taken_at,
                ))

        doses.sort(key=lambda d: d.scheduled_time)
        return doses

    # --- Mark Dose ---

    async def mark_dose(self, log_id: int, data: MedicineLogMarkTaken, user_id: int) -> MedicineLog:
        log = await self.log_repo.get_by_id(log_id)
        if log is None:
            raise MedicineLogNotFoundError(log_id)

        # Verify ownership via medicine
        medicine = await self.medicine_repo.get_by_id(log.medicine_id)
        if medicine is None or medicine.user_id != user_id:
            raise MedicineAccessDeniedError("log", log_id)

        log.taken = data.taken
        log.taken_at = utc_now().isoformat() if data.taken else None
        return await self.log_repo.update(log)

    # --- Stats ---

    async def get_medicine_stats(self, user_id: int) -> MedicineStatsResponse:
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        today_date = date.fromisoformat(today_str)

        medicines = await self.medicine_repo.get_all(user_id=user_id, active_only=True)
        medicine_ids = [m.id for m in medicines]

        # Today's counts — single query, then match in memory
        today_total = 0
        today_taken = 0
        today_logs = await self.log_repo.get_logs_for_date(medicine_ids, today_str)
        today_log_map = {log.schedule_id: log for log in today_logs}

        for medicine in medicines:
            for schedule in medicine.schedules:
                if not schedule.active:
                    continue
                if self._is_schedule_due_on_date(schedule, today_date):
                    today_total += 1
                    log = today_log_map.get(schedule.id)
                    if log and log.taken:
                        today_taken += 1

        # Weekly adherence
        week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        week_logs = await self.log_repo.get_logs_for_date_range(medicine_ids, week_start, today_str)
        week_total = len(week_logs)
        week_taken = sum(1 for log in week_logs if log.taken)
        weekly_adherence_pct = (week_taken / week_total * 100) if week_total > 0 else 100.0

        # Streak: fetch last 30 days in one query, then walk backwards
        current_streak = 0
        streak_start = (today_date - timedelta(days=30)).isoformat()
        yesterday_str = (today_date - timedelta(days=1)).isoformat()
        streak_logs = await self.log_repo.get_logs_for_date_range(medicine_ids, streak_start, yesterday_str)

        # Group logs by date
        logs_by_date: dict[str, list] = {}
        for log in streak_logs:
            logs_by_date.setdefault(log.scheduled_date, []).append(log)

        check_date = today_date - timedelta(days=1)
        for _ in range(30):
            check_str = check_date.isoformat()
            day_logs = logs_by_date.get(check_str, [])

            if not day_logs:
                break

            if not all(log.taken for log in day_logs):
                break

            current_streak += 1
            check_date -= timedelta(days=1)

        return MedicineStatsResponse(
            today_total=today_total,
            today_taken=today_taken,
            weekly_adherence_pct=round(weekly_adherence_pct, 1),
            current_streak_days=current_streak,
        )

    # --- Helpers ---

    @staticmethod
    def _is_schedule_due_on_date(schedule: MedicineSchedule, check_date: date) -> bool:
        """Determine whether a schedule fires on the given date."""
        freq = schedule.frequency_type

        if freq == "daily":
            return True

        if freq == "every_n_days":
            if not schedule.frequency_value or not schedule.created_at:
                return False
            created = date.fromisoformat(schedule.created_at[:10])
            delta_days = (check_date - created).days
            return delta_days >= 0 and delta_days % schedule.frequency_value == 0

        if freq == "weekly":
            if not schedule.days_of_week:
                return False
            days = [int(d) for d in schedule.days_of_week.split(",")]
            return check_date.weekday() in days

        if freq == "monthly":
            if schedule.day_of_month is None:
                return False
            return check_date.day == schedule.day_of_month

        return False
