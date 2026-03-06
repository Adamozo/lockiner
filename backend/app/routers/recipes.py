"""Food Recipes router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.food_recipes import (
    FoodRecipeCreate,
    FoodRecipeUpdate,
    FoodRecipeRating,
    FoodRecipeResponse,
    RecipeGenerateRequest,
    RecipeMatchResult,
)
from ..services.food_recipes import (
    FoodRecipeService,
    RecipeNotFoundError,
    RecipeAccessDeniedError,
    RecipeAIUnavailableError,
)
from ..services.user_api_keys import UserAPIKeyService

router = APIRouter(prefix="/api/v1/food/recipes", tags=["food-recipes"])


async def get_recipe_service(db: AsyncSession = Depends(get_db)) -> FoodRecipeService:
    return FoodRecipeService(db)


# ============================================================
# CRUD
# ============================================================

@router.get("/", response_model=List[FoodRecipeResponse])
async def list_recipes(
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
):
    return await service.get_recipes(current_user.id)


@router.post("/", response_model=FoodRecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    data: FoodRecipeCreate,
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
):
    return await service.create_recipe(data, current_user.id)


@router.get("/{recipe_id}", response_model=FoodRecipeResponse)
async def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
):
    try:
        return await service.get_recipe(recipe_id, current_user.id)
    except RecipeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    except RecipeAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.put("/{recipe_id}", response_model=FoodRecipeResponse)
async def update_recipe(
    recipe_id: int,
    data: FoodRecipeUpdate,
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
):
    try:
        return await service.update_recipe(recipe_id, data, current_user.id)
    except RecipeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    except RecipeAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
):
    try:
        await service.delete_recipe(recipe_id, current_user.id)
    except RecipeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    except RecipeAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.patch("/{recipe_id}/rating", response_model=FoodRecipeResponse)
async def rate_recipe(
    recipe_id: int,
    data: FoodRecipeRating,
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
):
    try:
        return await service.rate_recipe(recipe_id, data, current_user.id)
    except RecipeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    except RecipeAccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


# ============================================================
# AI Generation
# ============================================================

@router.post("/generate", response_model=List[FoodRecipeCreate])
async def generate_recipes(
    data: RecipeGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
    db: AsyncSession = Depends(get_db),
):
    api_key_service = UserAPIKeyService(db)
    provider_type, api_key = await api_key_service.get_active_provider(current_user)

    try:
        return await service.generate_recipes(data, current_user, provider_type, api_key)
    except RecipeAIUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        import traceback
        import logging
        logging.getLogger(__name__).error(f"Recipe generate error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI error: {str(e)}")


# ============================================================
# Matching
# ============================================================

@router.get("/match/inventory", response_model=List[RecipeMatchResult])
async def match_recipes_to_inventory(
    current_user: User = Depends(get_current_user),
    service: FoodRecipeService = Depends(get_recipe_service),
):
    return await service.match_recipes(current_user.id)
