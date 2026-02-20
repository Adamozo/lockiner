"""Todo List module repositories."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import date as date_type

from ..models.todo import TodoList, TodoItem, TodoPostponeLog, TodoNotificationRule


class TodoListRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, list_id: int) -> Optional[TodoList]:
        result = await self.db.execute(
            select(TodoList)
            .options(selectinload(TodoList.items))
            .filter(TodoList.id == list_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_date(self, user_id: int, date: str) -> Optional[TodoList]:
        result = await self.db.execute(
            select(TodoList)
            .options(selectinload(TodoList.items))
            .filter(TodoList.user_id == user_id, TodoList.date == date)
        )
        return result.scalar_one_or_none()

    async def get_range(self, user_id: int, date_from: str, date_to: str) -> List[TodoList]:
        """Get all lists (with items) in a date range, ordered by date asc."""
        result = await self.db.execute(
            select(TodoList)
            .options(selectinload(TodoList.items))
            .filter(
                TodoList.user_id == user_id,
                TodoList.date >= date_from,
                TodoList.date <= date_to,
            )
            .order_by(TodoList.date.asc())
        )
        return list(result.scalars().all())

    async def create(self, todo_list: TodoList) -> TodoList:
        self.db.add(todo_list)
        await self.db.commit()
        await self.db.refresh(todo_list)
        return await self.get_by_id(todo_list.id)

    async def update(self, todo_list: TodoList) -> TodoList:
        await self.db.commit()
        await self.db.refresh(todo_list)
        return await self.get_by_id(todo_list.id)

    async def delete(self, todo_list: TodoList) -> None:
        await self.db.delete(todo_list)
        await self.db.commit()

    async def get_all_with_enabled_rules(self) -> List[TodoList]:
        """Used by scheduler: get today's lists for users who have notification rules."""
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        result = await self.db.execute(
            select(TodoList)
            .options(selectinload(TodoList.items))
            .filter(TodoList.date == today)
        )
        return list(result.scalars().all())


class TodoItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, item_id: int) -> Optional[TodoItem]:
        result = await self.db.execute(
            select(TodoItem).filter(TodoItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create(self, item: TodoItem) -> TodoItem:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update(self, item: TodoItem) -> TodoItem:
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, item: TodoItem) -> None:
        await self.db.delete(item)
        await self.db.commit()

    async def get_items_with_reminders_at(self, time_str: str, date_str: str) -> List[TodoItem]:
        """Return active items with reminder at the given time today."""
        result = await self.db.execute(
            select(TodoItem)
            .join(TodoList, TodoItem.list_id == TodoList.id)
            .filter(
                TodoItem.item_reminder_enabled == True,
                TodoItem.item_reminder_time == time_str,
                TodoItem.completed == False,
                TodoList.date == date_str,
            )
        )
        return list(result.scalars().all())


class TodoPostponeLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log: TodoPostponeLog) -> TodoPostponeLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_by_user(self, user_id: int, days: int = 30) -> List[TodoPostponeLog]:
        from datetime import datetime, timezone, timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        result = await self.db.execute(
            select(TodoPostponeLog)
            .filter(
                TodoPostponeLog.user_id == user_id,
                TodoPostponeLog.postponed_at >= cutoff,
            )
            .order_by(TodoPostponeLog.postponed_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_item(self, item_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).where(TodoPostponeLog.todo_item_id == item_id)
        )
        return result.scalar_one()


class TodoNotificationRuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, rule_id: int) -> Optional[TodoNotificationRule]:
        result = await self.db.execute(
            select(TodoNotificationRule).filter(TodoNotificationRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> List[TodoNotificationRule]:
        result = await self.db.execute(
            select(TodoNotificationRule)
            .filter(TodoNotificationRule.user_id == user_id)
            .order_by(TodoNotificationRule.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_enabled_all_users(self) -> List[TodoNotificationRule]:
        """Return all enabled rules across all users — used by scheduler."""
        result = await self.db.execute(
            select(TodoNotificationRule)
            .filter(TodoNotificationRule.enabled == True)
        )
        return list(result.scalars().all())

    async def create(self, rule: TodoNotificationRule) -> TodoNotificationRule:
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def update(self, rule: TodoNotificationRule) -> TodoNotificationRule:
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def delete(self, rule: TodoNotificationRule) -> None:
        await self.db.delete(rule)
        await self.db.commit()
