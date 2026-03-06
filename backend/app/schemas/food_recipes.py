"""Food Recipes schemas."""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class RecipeIngredientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    quantity: Optional[float] = None
    unit: Optional[str] = None
    food_product_id: Optional[int] = None


class RecipeIngredientResponse(BaseModel):
    id: int
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    food_product_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class FoodRecipeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = Field(None, ge=1)
    servings: Optional[int] = Field(None, ge=1)
    instructions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    ingredients: List[RecipeIngredientCreate] = []
    source: str = "manual"


class FoodRecipeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = Field(None, ge=1)
    servings: Optional[int] = Field(None, ge=1)
    instructions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    ingredients: Optional[List[RecipeIngredientCreate]] = None


class FoodRecipeRating(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class FoodRecipeResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    instructions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    rating: Optional[int] = None
    source: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    ingredients: List[RecipeIngredientResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RecipeGenerateRequest(BaseModel):
    product_ids: Optional[List[int]] = None  # None = użyj całego inwentarza
    preferences: Optional[str] = None        # np. "wegetariańskie, szybkie"
    max_recipes: int = Field(3, ge=1, le=5)


class RecipeMatchIngredient(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    food_product_id: Optional[int] = None
    in_inventory: bool = False
    inventory_quantity: Optional[float] = None
    expiring_soon: bool = False   # wygasa w ciągu 3 dni


class RecipeMatchResult(BaseModel):
    recipe: FoodRecipeResponse
    match_percentage: float           # % składników dostępnych w inwentarzu
    missing_ingredients: List[RecipeMatchIngredient]
    available_ingredients: List[RecipeMatchIngredient]
    expiring_soon_count: int          # ile składników wymaganych kończy ważność
