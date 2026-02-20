"""Todo List Module Models."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class TodoList(Base):
    """A todo list for a specific day."""
    __tablename__ = "todo_lists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)  # ISO 8601: YYYY-MM-DD
    created_in_advance_days = Column(Integer, nullable=False, default=0)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_todo_lists_user_date"),
    )

    # Relationships
    user = relationship("User")
    items = relationship(
        "TodoItem",
        back_populates="todo_list",
        cascade="all, delete-orphan",
        foreign_keys="TodoItem.list_id",
        order_by="TodoItem.position",
    )

    def __repr__(self):
        return f"<TodoList(id={self.id}, date={self.date})>"


class TodoItem(Base):
    """A single task inside a todo list."""
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey("todo_lists.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(String, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    priority = Column(String, default="medium")  # low / medium / high
    position = Column(Integer, nullable=False, default=0)
    postponed_count = Column(Integer, nullable=False, default=0)
    original_list_id = Column(Integer, ForeignKey("todo_lists.id", ondelete="SET NULL"), nullable=True)
    item_reminder_enabled = Column(Boolean, default=False)
    item_reminder_time = Column(String, nullable=True)  # "HH:MM"
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")
    todo_list = relationship("TodoList", back_populates="items", foreign_keys=[list_id])
    original_list = relationship("TodoList", foreign_keys=[original_list_id])
    postpone_logs = relationship("TodoPostponeLog", back_populates="todo_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TodoItem(id={self.id}, title={self.title!r}, completed={self.completed})>"


class TodoPostponeLog(Base):
    """Audit log every time a task is postponed — used for statistics."""
    __tablename__ = "todo_postpone_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    todo_item_id = Column(Integer, ForeignKey("todo_items.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    from_list_id = Column(Integer, ForeignKey("todo_lists.id", ondelete="SET NULL"), nullable=True)
    to_list_id = Column(Integer, ForeignKey("todo_lists.id", ondelete="SET NULL"), nullable=True)
    excuse = Column(String, nullable=False, default="other")  # busy / other
    postponed_at = Column(String, nullable=False, default=lambda: utc_now().isoformat())

    # Relationships
    todo_item = relationship("TodoItem", back_populates="postpone_logs")

    def __repr__(self):
        return f"<TodoPostponeLog(id={self.id}, item={self.todo_item_id}, at={self.postponed_at})>"


class TodoNotificationRule(Base):
    """
    A user-defined notification rule for todo lists.

    trigger_type options:
      - fixed_time:       send at a specific time every day (field: fixed_time "HH:MM")
      - before_end_of_day: send N minutes before end of day (field: minutes_before_end)
      - interval:         send every N minutes within a time window
                          (fields: interval_minutes, window_start "HH:MM", window_end "HH:MM")
    """
    __tablename__ = "todo_notification_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    label = Column(String, nullable=True)
    trigger_type = Column(String, nullable=False)  # fixed_time | before_end_of_day | interval
    fixed_time = Column(String, nullable=True)           # "HH:MM"
    minutes_before_end = Column(Integer, nullable=True)
    interval_minutes = Column(Integer, nullable=True)
    window_start = Column(String, nullable=True)         # "HH:MM"
    window_end = Column(String, nullable=True)           # "HH:MM"
    notify_only_if_incomplete = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    last_sent_at = Column(String, nullable=True)         # ISO datetime, for deduplication
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<TodoNotificationRule(id={self.id}, type={self.trigger_type}, user={self.user_id})>"
