"""Todo List module schemas (Pydantic V2)."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# ============================================================
# TodoItem schemas
# ============================================================

class TodoItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    estimated_minutes: Optional[int] = Field(None, ge=1, le=1440)
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    position: int = Field(0, ge=0)
    item_reminder_enabled: bool = False
    item_reminder_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")


class TodoItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    estimated_minutes: Optional[int] = Field(None, ge=1, le=1440)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    position: Optional[int] = Field(None, ge=0)
    item_reminder_enabled: Optional[bool] = None
    item_reminder_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")


class TodoItemResponse(BaseModel):
    id: int
    list_id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    completed_at: Optional[str]
    estimated_minutes: Optional[int]
    priority: str
    position: int
    postponed_count: int
    original_list_id: Optional[int]
    item_reminder_enabled: bool
    item_reminder_time: Optional[str]
    created_at: str
    updated_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TodoList schemas
# ============================================================

class TodoListCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


class TodoListUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)


class TodoListResponse(BaseModel):
    id: int
    user_id: int
    title: str
    date: str
    created_in_advance_days: int
    items: List[TodoItemResponse] = []
    created_at: str
    updated_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TodoListSummaryResponse(BaseModel):
    """Lightweight list without items — for listing multiple days."""
    id: int
    user_id: int
    title: str
    date: str
    created_in_advance_days: int
    total_items: int
    completed_items: int
    estimated_minutes_total: Optional[int]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Postpone schemas
# ============================================================

class TodoPostponeRequest(BaseModel):
    to_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    to_list_title: Optional[str] = Field(None, max_length=255)
    excuse: str = Field("other", pattern="^(busy|other)$")


class TodoPostponeLogResponse(BaseModel):
    id: int
    todo_item_id: int
    user_id: int
    from_list_id: Optional[int]
    to_list_id: Optional[int]
    excuse: str
    postponed_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Notification rule schemas
# ============================================================

class TodoNotificationRuleCreate(BaseModel):
    label: Optional[str] = Field(None, max_length=100)
    trigger_type: str = Field(..., pattern="^(fixed_time|before_end_of_day|interval)$")
    fixed_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    minutes_before_end: Optional[int] = Field(None, ge=1, le=1439)
    interval_minutes: Optional[int] = Field(None, ge=5, le=1440)
    window_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    window_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    notify_only_if_incomplete: bool = True
    enabled: bool = True


class TodoNotificationRuleUpdate(BaseModel):
    label: Optional[str] = Field(None, max_length=100)
    trigger_type: Optional[str] = Field(None, pattern="^(fixed_time|before_end_of_day|interval)$")
    fixed_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    minutes_before_end: Optional[int] = Field(None, ge=1, le=1439)
    interval_minutes: Optional[int] = Field(None, ge=5, le=1440)
    window_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    window_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    notify_only_if_incomplete: Optional[bool] = None
    enabled: Optional[bool] = None


class TodoNotificationRuleResponse(BaseModel):
    id: int
    user_id: int
    label: Optional[str]
    trigger_type: str
    fixed_time: Optional[str]
    minutes_before_end: Optional[int]
    interval_minutes: Optional[int]
    window_start: Optional[str]
    window_end: Optional[str]
    notify_only_if_incomplete: bool
    enabled: bool
    last_sent_at: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Stats schema
# ============================================================

class TodoStatsResponse(BaseModel):
    total_created: int
    total_completed: int
    total_postponed: int
    completion_rate_pct: float
    postpone_rate_pct: float
    current_streak_days: int
    days_analyzed: int
