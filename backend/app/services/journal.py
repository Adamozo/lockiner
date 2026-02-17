import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from ..models.journal import JournalEntry, JournalItem, JournalReport
from ..models.base import utc_now
from ..schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    ReportGenerateRequest,
    JournalStatsResponse,
    ReportData,
    CategoryReportData,
    JOURNAL_CATEGORIES,
)
from ..repositories.journal import (
    JournalEntryRepository,
    JournalItemRepository,
    JournalReportRepository,
)


# --- Exceptions ---

class JournalEntryNotFoundError(Exception):
    def __init__(self, entry_id: int):
        self.entry_id = entry_id
        super().__init__(f"Journal entry {entry_id} not found")


class JournalEntryDateNotFoundError(Exception):
    def __init__(self, date: str):
        self.date = date
        super().__init__(f"No journal entry for date {date}")


class JournalEntryConflictError(Exception):
    def __init__(self, date: str):
        self.date = date
        super().__init__(f"Journal entry already exists for date {date}")


class JournalAccessDeniedError(Exception):
    def __init__(self, resource_type: str, resource_id: int):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"Access denied to {resource_type} {resource_id}")


class JournalReportNotFoundError(Exception):
    def __init__(self, report_type: str, period: str):
        self.report_type = report_type
        self.period = period
        super().__init__(f"Report not found: {report_type}/{period}")


# --- Service ---

class JournalService:
    def __init__(self, db: AsyncSession):
        self.entry_repo = JournalEntryRepository(db)
        self.item_repo = JournalItemRepository(db)
        self.report_repo = JournalReportRepository(db)
        self.db = db

    # --- Entries ---

    async def list_entries(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[JournalEntry]:
        return await self.entry_repo.get_all(
            user_id=user_id, skip=skip, limit=limit,
            start_date=start_date, end_date=end_date,
        )

    async def get_entry(self, entry_id: int, user_id: int) -> JournalEntry:
        entry = await self.entry_repo.get_by_id(entry_id)
        if entry is None:
            raise JournalEntryNotFoundError(entry_id)
        if entry.user_id != user_id:
            raise JournalAccessDeniedError("journal_entry", entry_id)
        return entry

    async def get_entry_by_date(self, date: str, user_id: int) -> JournalEntry:
        entry = await self.entry_repo.get_by_user_and_date(user_id, date)
        if entry is None:
            raise JournalEntryDateNotFoundError(date)
        return entry

    async def create_entry(self, data: JournalEntryCreate, user_id: int) -> JournalEntry:
        existing = await self.entry_repo.get_by_user_and_date(user_id, data.date)
        if existing:
            raise JournalEntryConflictError(data.date)

        entry = JournalEntry(
            user_id=user_id,
            date=data.date,
            mood_score=data.mood_score,
            notes=data.notes,
        )

        for item_data in data.items:
            entry.items.append(JournalItem(
                category=item_data.category,
                position=item_data.position,
                content=item_data.content,
            ))

        return await self.entry_repo.create(entry)

    async def update_entry(
        self, entry_id: int, data: JournalEntryUpdate, user_id: int
    ) -> JournalEntry:
        entry = await self.entry_repo.get_by_id(entry_id)
        if entry is None:
            raise JournalEntryNotFoundError(entry_id)
        if entry.user_id != user_id:
            raise JournalAccessDeniedError("journal_entry", entry_id)

        update_data = data.model_dump(exclude_unset=True, exclude={"items"})
        for field, value in update_data.items():
            setattr(entry, field, value)

        entry.updated_at = utc_now().isoformat()

        if data.items is not None:
            await self.item_repo.delete_by_entry_id(entry_id)
            entry.items = []
            for item_data in data.items:
                item = JournalItem(
                    entry_id=entry_id,
                    category=item_data.category,
                    position=item_data.position,
                    content=item_data.content,
                )
                entry.items.append(item)

        return await self.entry_repo.update(entry)

    async def delete_entry(self, entry_id: int, user_id: int) -> None:
        entry = await self.entry_repo.get_by_id(entry_id)
        if entry is None:
            raise JournalEntryNotFoundError(entry_id)
        if entry.user_id != user_id:
            raise JournalAccessDeniedError("journal_entry", entry_id)
        await self.entry_repo.delete(entry)

    # --- Stats ---

    async def get_stats(self, user_id: int) -> JournalStatsResponse:
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        month_start = now.strftime("%Y-%m-01")

        total = await self.entry_repo.count_by_user(user_id)
        this_week = await self.entry_repo.count_by_user_and_date_range(user_id, week_start, today)
        this_month = await self.entry_repo.count_by_user_and_date_range(user_id, month_start, today)

        dates = await self.entry_repo.get_all_dates(user_id)
        current_streak, longest_streak = self._calculate_streaks(dates, today)

        avg_mood = await self.entry_repo.get_avg_mood(user_id)

        return JournalStatsResponse(
            total_entries=total,
            entries_this_week=this_week,
            entries_this_month=this_month,
            current_streak=current_streak,
            longest_streak=longest_streak,
            avg_mood=avg_mood,
        )

    # --- Reports ---

    async def generate_report(
        self, request: ReportGenerateRequest, user_id: int
    ) -> JournalReport:
        if request.report_type == "monthly":
            start_date = f"{request.period}-01"
            # Calculate end of month
            year, month = map(int, request.period.split("-"))
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"
            # Subtract one day for inclusive end
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)
            end_date = end_dt.strftime("%Y-%m-%d")
        else:  # yearly
            start_date = f"{request.period}-01-01"
            end_date = f"{request.period}-12-31"

        # Get items in range
        items = await self.item_repo.get_items_in_date_range(user_id, start_date, end_date)
        entry_count = await self.entry_repo.count_by_user_and_date_range(user_id, start_date, end_date)
        avg_mood = await self.entry_repo.get_avg_mood_in_range(user_id, start_date, end_date)

        # Get dates for streak calculation
        all_dates = await self.entry_repo.get_all_dates(user_id)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        current_streak, longest_streak = self._calculate_streaks(all_dates, today)

        # Build category data
        categories = {}
        for cat in JOURNAL_CATEGORIES:
            cat_items = [i.content for i in items if i.category == cat]
            categories[cat] = CategoryReportData(count=len(cat_items), items=cat_items)

        report_data = ReportData(
            categories=categories,
            avg_mood=avg_mood,
            entry_count=entry_count,
            current_streak=current_streak,
            longest_streak=longest_streak,
        )

        # Upsert report
        existing = await self.report_repo.get_by_user_type_period(
            user_id, request.report_type, request.period
        )

        if existing:
            existing.data = report_data.model_dump_json()
            existing.entry_count = entry_count
            existing.updated_at = utc_now().isoformat()
            return await self.report_repo.update(existing)
        else:
            report = JournalReport(
                user_id=user_id,
                report_type=request.report_type,
                period=request.period,
                data=report_data.model_dump_json(),
                entry_count=entry_count,
            )
            return await self.report_repo.upsert(report)

    async def get_report(
        self, user_id: int, report_type: str, period: str
    ) -> JournalReport:
        report = await self.report_repo.get_by_user_type_period(user_id, report_type, period)
        if report is None:
            raise JournalReportNotFoundError(report_type, period)
        return report

    async def list_reports(
        self, user_id: int, report_type: str
    ) -> List[JournalReport]:
        return await self.report_repo.get_all_by_type(user_id, report_type)

    # --- Helpers ---

    @staticmethod
    def _calculate_streaks(dates: List[str], today: str) -> tuple[int, int]:
        """Calculate current and longest streaks from sorted date list."""
        if not dates:
            return 0, 0

        date_set = set(dates)
        longest = 0
        current = 0

        # Calculate longest streak
        streak = 1
        sorted_dates = sorted(dates)
        for i in range(1, len(sorted_dates)):
            prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
            curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
            if (curr - prev).days == 1:
                streak += 1
            else:
                longest = max(longest, streak)
                streak = 1
        longest = max(longest, streak)

        # Calculate current streak (counting back from today)
        current_date = datetime.strptime(today, "%Y-%m-%d")
        # Start from today or yesterday
        if today in date_set:
            current = 1
            check = current_date - timedelta(days=1)
        elif (current_date - timedelta(days=1)).strftime("%Y-%m-%d") in date_set:
            current = 1
            check = current_date - timedelta(days=2)
        else:
            return 0, longest

        while check.strftime("%Y-%m-%d") in date_set:
            current += 1
            check -= timedelta(days=1)

        return current, longest
