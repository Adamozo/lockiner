"""Todo List module router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.todo import (
    TodoListCreate,
    TodoListUpdate,
    TodoListResponse,
    TodoListSummaryResponse,
    TodoItemCreate,
    TodoItemUpdate,
    TodoItemResponse,
    TodoPostponeRequest,
    TodoNotificationRuleCreate,
    TodoNotificationRuleUpdate,
    TodoNotificationRuleResponse,
    TodoStatsResponse,
)
from ..services.todo import (
    TodoService,
    TodoListNotFoundError,
    TodoItemNotFoundError,
    TodoNotificationRuleNotFoundError,
    TodoAccessDeniedError,
    TodoListAlreadyExistsError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/todo", tags=["todo"])

# ---------------------------------------


async def get_todo_service(db: AsyncSession = Depends(get_db)) -> TodoService:
    return TodoService(db)


# ============================================================
# Static routes MUST come before /{list_id}
# ============================================================


@router.get("/stats", response_model=TodoStatsResponse)
async def get_stats(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Get todo statistics for the last N days."""
    return await service.get_stats(user_id=current_user.id, days=days)


@router.get("/lists", response_model=List[TodoListSummaryResponse])
async def list_todo_lists(
    date_from: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Get summaries of all lists in a date range."""
    return await service.get_lists_range(user_id=current_user.id, date_from=date_from, date_to=date_to)


@router.post("/lists", response_model=TodoListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    data: TodoListCreate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Create a new todo list for a specific date."""
    try:
        return await service.create_list(data, user_id=current_user.id)
    except TodoListAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/lists/date/{date}", response_model=Optional[TodoListResponse])
async def get_list_by_date(
    date: str,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Get the todo list for a specific date (or null if none exists)."""
    return await service.get_list_for_date(user_id=current_user.id, date=date)


# --- Notification rules (static prefix, before /{list_id}) ---


@router.get("/notification-rules", response_model=List[TodoNotificationRuleResponse])
async def list_notification_rules(
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Get all notification rules for the current user."""
    return await service.list_rules(user_id=current_user.id)


@router.post("/notification-rules", response_model=TodoNotificationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_rule(
    data: TodoNotificationRuleCreate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Create a new notification rule."""
    return await service.create_rule(data, user_id=current_user.id)


@router.put("/notification-rules/{rule_id}", response_model=TodoNotificationRuleResponse)
async def update_notification_rule(
    rule_id: int,
    data: TodoNotificationRuleUpdate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Update a notification rule."""
    try:
        return await service.update_rule(rule_id, data, user_id=current_user.id)
    except TodoNotificationRuleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/notification-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Delete a notification rule."""
    try:
        await service.delete_rule(rule_id, user_id=current_user.id)
    except TodoNotificationRuleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# --- Item-level routes (static prefix items/, before /{list_id}) ---


@router.put("/items/{item_id}", response_model=TodoItemResponse)
async def update_item(
    item_id: int,
    data: TodoItemUpdate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Update a todo item."""
    try:
        return await service.update_item(item_id, data, user_id=current_user.id)
    except TodoItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Delete a todo item."""
    try:
        await service.delete_item(item_id, user_id=current_user.id)
    except TodoItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/items/{item_id}/complete", response_model=TodoItemResponse)
async def complete_item(
    item_id: int,
    completed: bool = Query(...),
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Mark a todo item as completed or uncompleted."""
    try:
        return await service.complete_item(item_id, completed, user_id=current_user.id)
    except TodoItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/items/{item_id}/postpone", response_model=TodoItemResponse)
async def postpone_item(
    item_id: int,
    data: TodoPostponeRequest,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Postpone a todo item to another date (or indefinitely)."""
    try:
        return await service.postpone_item(item_id, data, user_id=current_user.id)
    except TodoItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================
# Dynamic /{list_id} routes
# ============================================================


@router.get("/lists/{list_id}", response_model=TodoListResponse)
async def get_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Get a specific todo list with all items."""
    try:
        return await service.get_list(list_id, user_id=current_user.id)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/lists/{list_id}", response_model=TodoListResponse)
async def update_list(
    list_id: int,
    data: TodoListUpdate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Update a todo list (e.g. rename)."""
    try:
        return await service.update_list(list_id, data, user_id=current_user.id)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Delete a todo list and all its items."""
    try:
        await service.delete_list(list_id, user_id=current_user.id)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/lists/{list_id}/items", response_model=TodoItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    list_id: int,
    data: TodoItemCreate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Add a new item to a todo list."""
    try:
        return await service.add_item(list_id, data, user_id=current_user.id)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TodoAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
