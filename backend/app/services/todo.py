"""Todo List module service layer."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timezone, timedelta, date

from ..models.todo import TodoList, TodoItem, TodoPostponeLog, TodoNotificationRule
from ..models import utc_now
from ..schemas.todo import (
    TodoListCreate,
    TodoListUpdate,
    TodoItemCreate,
    TodoItemUpdate,
    TodoPostponeRequest,
    TodoNotificationRuleCreate,
    TodoNotificationRuleUpdate,
    TodoStatsResponse,
    TodoListSummaryResponse,
)
from ..repositories.todo import (
    TodoListRepository,
    TodoItemRepository,
    TodoPostponeLogRepository,
    TodoNotificationRuleRepository,
)


# ============================================================
# Custom exceptions
# ============================================================

class TodoListNotFoundError(Exception):
    def __init__(self, list_id):
        super().__init__(f"Todo list {list_id} not found")


class TodoItemNotFoundError(Exception):
    def __init__(self, item_id):
        super().__init__(f"Todo item {item_id} not found")


class TodoNotificationRuleNotFoundError(Exception):
    def __init__(self, rule_id):
        super().__init__(f"Todo notification rule {rule_id} not found")


class TodoAccessDeniedError(Exception):
    def __init__(self, resource: str, resource_id):
        super().__init__(f"Access denied to {resource} {resource_id}")


class TodoListAlreadyExistsError(Exception):
    def __init__(self, date: str):
        super().__init__(f"Todo list for date {date} already exists")


# ============================================================
# Service
# ============================================================

class TodoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.list_repo = TodoListRepository(db)
        self.item_repo = TodoItemRepository(db)
        self.log_repo = TodoPostponeLogRepository(db)
        self.rule_repo = TodoNotificationRuleRepository(db)

    # ----------------------------------------------------------
    # Lists
    # ----------------------------------------------------------

    async def get_list(self, list_id: int, user_id: int) -> TodoList:
        todo_list = await self.list_repo.get_by_id(list_id)
        if todo_list is None:
            raise TodoListNotFoundError(list_id)
        if todo_list.user_id != user_id:
            raise TodoAccessDeniedError("todo_list", list_id)
        return todo_list

    async def get_list_for_date(self, user_id: int, date: str) -> Optional[TodoList]:
        return await self.list_repo.get_by_user_and_date(user_id, date)

    async def get_lists_range(self, user_id: int, date_from: str, date_to: str) -> List[TodoListSummaryResponse]:
        lists = await self.list_repo.get_range(user_id, date_from, date_to)
        return [self._to_summary(lst) for lst in lists]

    async def create_list(self, data: TodoListCreate, user_id: int) -> TodoList:
        today = datetime.now(timezone.utc).date()
        list_date = date.fromisoformat(data.date)
        advance_days = max(0, (list_date - today).days)

        existing = await self.list_repo.get_by_user_and_date(user_id, data.date)
        if existing is not None:
            raise TodoListAlreadyExistsError(data.date)

        todo_list = TodoList(
            user_id=user_id,
            title=data.title,
            date=data.date,
            created_in_advance_days=advance_days,
        )
        return await self.list_repo.create(todo_list)

    async def get_or_create_list_for_date(self, user_id: int, date_str: str, title: str) -> TodoList:
        """Get or lazily create a list for the given date."""
        existing = await self.list_repo.get_by_user_and_date(user_id, date_str)
        if existing:
            return existing

        today = datetime.now(timezone.utc).date()
        list_date = date.fromisoformat(date_str)
        advance_days = max(0, (list_date - today).days)

        todo_list = TodoList(
            user_id=user_id,
            title=title,
            date=date_str,
            created_in_advance_days=advance_days,
        )
        return await self.list_repo.create(todo_list)

    async def update_list(self, list_id: int, data: TodoListUpdate, user_id: int) -> TodoList:
        todo_list = await self.list_repo.get_by_id(list_id)
        if todo_list is None:
            raise TodoListNotFoundError(list_id)
        if todo_list.user_id != user_id:
            raise TodoAccessDeniedError("todo_list", list_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo_list, field, value)
        todo_list.updated_at = utc_now().isoformat()
        return await self.list_repo.update(todo_list)

    async def delete_list(self, list_id: int, user_id: int) -> None:
        todo_list = await self.list_repo.get_by_id(list_id)
        if todo_list is None:
            raise TodoListNotFoundError(list_id)
        if todo_list.user_id != user_id:
            raise TodoAccessDeniedError("todo_list", list_id)
        await self.list_repo.delete(todo_list)

    # ----------------------------------------------------------
    # Items
    # ----------------------------------------------------------

    async def add_item(self, list_id: int, data: TodoItemCreate, user_id: int) -> TodoItem:
        todo_list = await self.list_repo.get_by_id(list_id)
        if todo_list is None:
            raise TodoListNotFoundError(list_id)
        if todo_list.user_id != user_id:
            raise TodoAccessDeniedError("todo_list", list_id)

        # Auto-assign position at end of list if caller passes 0 (default)
        auto_position = data.position
        if auto_position == 0 and todo_list.items:
            auto_position = max(i.position for i in todo_list.items) + 1

        item = TodoItem(
            list_id=list_id,
            user_id=user_id,
            title=data.title,
            description=data.description,
            estimated_minutes=data.estimated_minutes,
            priority=data.priority,
            position=auto_position,
            item_reminder_enabled=data.item_reminder_enabled,
            item_reminder_time=data.item_reminder_time,
            original_list_id=list_id,
        )
        return await self.item_repo.create(item)

    async def update_item(self, item_id: int, data: TodoItemUpdate, user_id: int) -> TodoItem:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise TodoItemNotFoundError(item_id)
        if item.user_id != user_id:
            raise TodoAccessDeniedError("todo_item", item_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        item.updated_at = utc_now().isoformat()
        return await self.item_repo.update(item)

    async def delete_item(self, item_id: int, user_id: int) -> None:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise TodoItemNotFoundError(item_id)
        if item.user_id != user_id:
            raise TodoAccessDeniedError("todo_item", item_id)
        await self.item_repo.delete(item)

    async def complete_item(self, item_id: int, completed: bool, user_id: int) -> TodoItem:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise TodoItemNotFoundError(item_id)
        if item.user_id != user_id:
            raise TodoAccessDeniedError("todo_item", item_id)

        item.completed = completed
        item.completed_at = utc_now().isoformat() if completed else None
        item.updated_at = utc_now().isoformat()
        return await self.item_repo.update(item)

    async def postpone_item(self, item_id: int, data: TodoPostponeRequest, user_id: int) -> TodoItem:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise TodoItemNotFoundError(item_id)
        if item.user_id != user_id:
            raise TodoAccessDeniedError("todo_item", item_id)

        from_list_id = item.list_id
        to_list_id = None

        if data.to_date:
            title = data.to_list_title or f"List for {data.to_date}"
            target_list = await self.get_or_create_list_for_date(user_id, data.to_date, title)
            to_list_id = target_list.id

            # Calculate position BEFORE mutating item.list_id to avoid session cache issues
            max_pos = max((i.position for i in target_list.items if i.id != item_id), default=-1) + 1

            # Move item to target list
            item.list_id = target_list.id
            item.position = max_pos

        # Update counters
        item.postponed_count += 1
        item.updated_at = utc_now().isoformat()
        await self.item_repo.update(item)

        # Write audit log
        log_entry = TodoPostponeLog(
            todo_item_id=item_id,
            user_id=user_id,
            from_list_id=from_list_id,
            to_list_id=to_list_id,
            excuse=data.excuse,
        )
        await self.log_repo.create(log_entry)

        return item

    # ----------------------------------------------------------
    # Notification rules
    # ----------------------------------------------------------

    async def list_rules(self, user_id: int) -> List[TodoNotificationRule]:
        return await self.rule_repo.get_by_user(user_id)

    async def create_rule(self, data: TodoNotificationRuleCreate, user_id: int) -> TodoNotificationRule:
        rule = TodoNotificationRule(
            user_id=user_id,
            label=data.label,
            trigger_type=data.trigger_type,
            fixed_time=data.fixed_time,
            minutes_before_end=data.minutes_before_end,
            interval_minutes=data.interval_minutes,
            window_start=data.window_start,
            window_end=data.window_end,
            notify_only_if_incomplete=data.notify_only_if_incomplete,
            enabled=data.enabled,
        )
        return await self.rule_repo.create(rule)

    async def update_rule(self, rule_id: int, data: TodoNotificationRuleUpdate, user_id: int) -> TodoNotificationRule:
        rule = await self.rule_repo.get_by_id(rule_id)
        if rule is None:
            raise TodoNotificationRuleNotFoundError(rule_id)
        if rule.user_id != user_id:
            raise TodoAccessDeniedError("todo_notification_rule", rule_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        return await self.rule_repo.update(rule)

    async def delete_rule(self, rule_id: int, user_id: int) -> None:
        rule = await self.rule_repo.get_by_id(rule_id)
        if rule is None:
            raise TodoNotificationRuleNotFoundError(rule_id)
        if rule.user_id != user_id:
            raise TodoAccessDeniedError("todo_notification_rule", rule_id)
        await self.rule_repo.delete(rule)

    # ----------------------------------------------------------
    # Stats
    # ----------------------------------------------------------

    async def get_stats(self, user_id: int, days: int = 30) -> TodoStatsResponse:
        today = datetime.now(timezone.utc).date()
        cutoff = (today - timedelta(days=days)).isoformat()
        today_str = today.isoformat()

        lists = await self.list_repo.get_range(user_id, cutoff, today_str)

        total_created = sum(len(lst.items) for lst in lists)
        total_completed = sum(1 for lst in lists for item in lst.items if item.completed)
        total_postponed = sum(item.postponed_count for lst in lists for item in lst.items)

        completion_rate = (total_completed / total_created * 100) if total_created > 0 else 100.0
        postpone_rate = (total_postponed / total_created * 100) if total_created > 0 else 0.0

        # Streak: consecutive days with 100% completion (walking back from yesterday)
        lists_by_date = {lst.date: lst for lst in lists}
        streak = 0
        check = today - timedelta(days=1)
        for _ in range(days):
            check_str = check.isoformat()
            lst = lists_by_date.get(check_str)
            if lst is None or not lst.items:
                break
            if not all(item.completed for item in lst.items):
                break
            streak += 1
            check -= timedelta(days=1)

        return TodoStatsResponse(
            total_created=total_created,
            total_completed=total_completed,
            total_postponed=total_postponed,
            completion_rate_pct=round(completion_rate, 1),
            postpone_rate_pct=round(postpone_rate, 1),
            current_streak_days=streak,
            days_analyzed=days,
        )

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    @staticmethod
    def _to_summary(lst: TodoList) -> TodoListSummaryResponse:
        items = lst.items or []
        completed = sum(1 for i in items if i.completed)
        est_total = sum(i.estimated_minutes for i in items if i.estimated_minutes) or None
        return TodoListSummaryResponse(
            id=lst.id,
            user_id=lst.user_id,
            title=lst.title,
            date=lst.date,
            created_in_advance_days=lst.created_in_advance_days,
            total_items=len(items),
            completed_items=completed,
            estimated_minutes_total=est_total,
            created_at=lst.created_at,
        )
