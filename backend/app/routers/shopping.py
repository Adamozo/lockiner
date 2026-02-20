"""Shopping Lists module router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.shopping import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListResponse,
    ShoppingListSummaryResponse,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingItemStatusUpdate,
    ShoppingListItemResponse,
)
from ..services.shopping import (
    ShoppingService,
    ShoppingListNotFoundError,
    ShoppingItemNotFoundError,
    ShoppingAccessDeniedError,
    ShoppingInvalidHouseholdError,
)

router = APIRouter(prefix="/api/v1/shopping", tags=["shopping"])


async def get_shopping_service(db: AsyncSession = Depends(get_db)) -> ShoppingService:
    return ShoppingService(db)


# ============================================================
# Lists
# ============================================================

@router.get("/lists", response_model=List[ShoppingListSummaryResponse])
async def get_lists(
    status: Optional[str] = Query(None, pattern="^(active|completed|archived)$"),
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    """Get all shopping lists accessible to the current user."""
    return await service.get_lists(user_id=current_user.id, status=status)


@router.post("/lists", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    data: ShoppingListCreate,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        return await service.create_list(data, user_id=current_user.id)
    except ShoppingInvalidHouseholdError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/lists/{list_id}", response_model=ShoppingListResponse)
async def get_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        return await service.get_list(list_id, user_id=current_user.id)
    except ShoppingListNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.put("/lists/{list_id}", response_model=ShoppingListResponse)
async def update_list(
    list_id: int,
    data: ShoppingListUpdate,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        return await service.update_list(list_id, data, user_id=current_user.id)
    except ShoppingListNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except ShoppingInvalidHouseholdError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        await service.delete_list(list_id, user_id=current_user.id)
    except ShoppingListNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can delete this list")


@router.post("/lists/{list_id}/complete", response_model=ShoppingListResponse)
async def complete_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        return await service.complete_list(list_id, user_id=current_user.id)
    except ShoppingListNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


# ============================================================
# Items
# ============================================================

@router.post("/lists/{list_id}/items", response_model=ShoppingListItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    list_id: int,
    data: ShoppingListItemCreate,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        return await service.add_item(list_id, data, user_id=current_user.id)
    except ShoppingListNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.put("/items/{item_id}", response_model=ShoppingListItemResponse)
async def update_item(
    item_id: int,
    data: ShoppingListItemUpdate,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        return await service.update_item(item_id, data, user_id=current_user.id)
    except ShoppingItemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.patch("/items/{item_id}/status", response_model=ShoppingListItemResponse)
async def update_item_status(
    item_id: int,
    data: ShoppingItemStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        return await service.update_item_status(item_id, data, user_id=current_user.id)
    except ShoppingItemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    service: ShoppingService = Depends(get_shopping_service),
):
    try:
        await service.delete_item(item_id, user_id=current_user.id)
    except ShoppingItemNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    except ShoppingAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
