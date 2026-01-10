from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from ..services.category import (
    CategoryService,
    CategoryNotFoundError,
    CategoryAccessDeniedError,
    CategoryNameExistsError,
    CategoryInUseError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

# ---------------------------------------

async def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

# ---------------------------------------

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    household_id: Optional[str] = Query(None, description="Include categories from household (UUID)"),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    return await service.list_categories(
        user_id=current_user.id,
        household_uid=household_id,
    )


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    household_id: Optional[str] = Query(None, description="Assign to household instead of personal (UUID)"),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    try:
        return await service.create_category(
            category,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except CategoryNameExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    try:
        return await service.get_category(
            category_id,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except CategoryAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    try:
        return await service.update_category(
            category_id,
            category_update,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except CategoryAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except CategoryNameExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    try:
        await service.delete_category(
            category_id,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except CategoryAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except CategoryInUseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
