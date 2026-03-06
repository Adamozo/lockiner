"""Food Recipes Service — CRUD, AI generation, inventory matching."""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import User
from ..models.food import FoodRecipe, FoodRecipeIngredient, FoodInventory, FoodProduct
from ..schemas.food_recipes import (
    FoodRecipeCreate,
    FoodRecipeUpdate,
    FoodRecipeRating,
    FoodRecipeResponse,
    RecipeIngredientCreate,
    RecipeIngredientResponse,
    RecipeGenerateRequest,
    RecipeMatchIngredient,
    RecipeMatchResult,
)
from ..integrations.ocr_provider import OCRProvider
from .food import normalize_name

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _recipe_to_response(recipe: FoodRecipe) -> FoodRecipeResponse:
    instructions = []
    if recipe.instructions:
        try:
            instructions = json.loads(recipe.instructions)
        except Exception:
            instructions = [recipe.instructions]

    tags = []
    if recipe.tags:
        tags = [t.strip() for t in recipe.tags.split(",") if t.strip()]

    return FoodRecipeResponse(
        id=recipe.id,
        user_id=recipe.user_id,
        name=recipe.name,
        description=recipe.description,
        prep_time_minutes=recipe.prep_time_minutes,
        servings=recipe.servings,
        instructions=instructions,
        tags=tags,
        rating=recipe.rating,
        source=recipe.source,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        ingredients=[
            RecipeIngredientResponse(
                id=i.id,
                name=i.name,
                quantity=i.quantity,
                unit=i.unit,
                food_product_id=i.food_product_id,
            )
            for i in recipe.ingredients
        ],
    )


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class RecipeNotFoundError(Exception):
    pass

class RecipeAccessDeniedError(Exception):
    pass

class RecipeAIUnavailableError(Exception):
    pass


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class FoodRecipeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def get_recipes(self, user_id: int) -> list[FoodRecipeResponse]:
        result = await self.db.execute(
            select(FoodRecipe)
            .where(FoodRecipe.user_id == user_id)
            .options(selectinload(FoodRecipe.ingredients))
            .order_by(FoodRecipe.created_at.desc())
        )
        recipes = result.scalars().all()
        return [_recipe_to_response(r) for r in recipes]

    async def get_recipe(self, recipe_id: int, user_id: int) -> FoodRecipeResponse:
        recipe = await self._get_or_404(recipe_id, user_id)
        return _recipe_to_response(recipe)

    async def create_recipe(self, data: FoodRecipeCreate, user_id: int) -> FoodRecipeResponse:
        recipe = FoodRecipe(
            user_id=user_id,
            name=data.name,
            description=data.description,
            prep_time_minutes=data.prep_time_minutes,
            servings=data.servings,
            instructions=json.dumps(data.instructions or [], ensure_ascii=False),
            tags=",".join(data.tags) if data.tags else None,
            source=data.source,
            created_at=_utc_now(),
        )
        self.db.add(recipe)
        await self.db.flush()

        for ing in data.ingredients:
            self.db.add(FoodRecipeIngredient(
                recipe_id=recipe.id,
                name=ing.name,
                quantity=ing.quantity,
                unit=ing.unit,
                food_product_id=ing.food_product_id,
            ))

        await self.db.commit()
        await self.db.refresh(recipe)

        result = await self.db.execute(
            select(FoodRecipe)
            .where(FoodRecipe.id == recipe.id)
            .options(selectinload(FoodRecipe.ingredients))
        )
        return _recipe_to_response(result.scalar_one())

    async def update_recipe(self, recipe_id: int, data: FoodRecipeUpdate, user_id: int) -> FoodRecipeResponse:
        recipe = await self._get_or_404(recipe_id, user_id)

        if data.name is not None:
            recipe.name = data.name
        if data.description is not None:
            recipe.description = data.description
        if data.prep_time_minutes is not None:
            recipe.prep_time_minutes = data.prep_time_minutes
        if data.servings is not None:
            recipe.servings = data.servings
        if data.instructions is not None:
            recipe.instructions = json.dumps(data.instructions, ensure_ascii=False)
        if data.tags is not None:
            recipe.tags = ",".join(data.tags)
        if data.ingredients is not None:
            # Replace all ingredients
            await self.db.execute(
                FoodRecipeIngredient.__table__.delete().where(
                    FoodRecipeIngredient.recipe_id == recipe_id
                )
            )
            for ing in data.ingredients:
                self.db.add(FoodRecipeIngredient(
                    recipe_id=recipe_id,
                    name=ing.name,
                    quantity=ing.quantity,
                    unit=ing.unit,
                    food_product_id=ing.food_product_id,
                ))

        recipe.updated_at = _utc_now()
        await self.db.commit()

        result = await self.db.execute(
            select(FoodRecipe)
            .where(FoodRecipe.id == recipe_id)
            .options(selectinload(FoodRecipe.ingredients))
        )
        return _recipe_to_response(result.scalar_one())

    async def delete_recipe(self, recipe_id: int, user_id: int) -> None:
        recipe = await self._get_or_404(recipe_id, user_id)
        await self.db.delete(recipe)
        await self.db.commit()

    async def rate_recipe(self, recipe_id: int, data: FoodRecipeRating, user_id: int) -> FoodRecipeResponse:
        recipe = await self._get_or_404(recipe_id, user_id)
        recipe.rating = data.rating
        recipe.updated_at = _utc_now()
        await self.db.commit()

        result = await self.db.execute(
            select(FoodRecipe)
            .where(FoodRecipe.id == recipe_id)
            .options(selectinload(FoodRecipe.ingredients))
        )
        return _recipe_to_response(result.scalar_one())

    # ------------------------------------------------------------------
    # AI Generation
    # ------------------------------------------------------------------

    async def generate_recipes(
        self,
        data: RecipeGenerateRequest,
        user: User,
        provider_type: Optional[OCRProvider],
        api_key: Optional[str],
    ) -> list[FoodRecipeCreate]:
        if not provider_type or not api_key:
            raise RecipeAIUnavailableError("No AI provider configured. Add an API key in Settings.")

        # Build inventory context
        query = (
            select(FoodInventory)
            .where(
                FoodInventory.user_id == user.id,
                FoodInventory.status.in_(["available", "opened"]),
            )
            .options(selectinload(FoodInventory.product))
        )
        if data.product_ids:
            query = query.where(FoodInventory.product_id.in_(data.product_ids))

        result = await self.db.execute(query)
        inventory = result.scalars().all()

        if not inventory:
            raise ValueError("No products in inventory to base recipes on.")

        products_list = []
        for item in inventory:
            if not item.product:
                continue
            line = f"- {item.product.name} ({item.quantity} {item.unit})"
            if item.expiry_date:
                line += f", wygasa: {item.expiry_date}"
            products_list.append(line)

        products_text = "\n".join(products_list)
        prefs = f"\nPreferencje: {data.preferences}" if data.preferences else ""

        prompt = f"""Mam następujące produkty w spiżarni/lodówce:
{products_text}
{prefs}

Zaproponuj {data.max_recipes} przepisów kulinarnych które mogę zrobić z tych składników (lub większości z nich). Dla każdego przepisu podaj JSON według schematu:
{{
  "name": "Nazwa przepisu",
  "description": "Krótki opis (1-2 zdania)",
  "prep_time_minutes": 30,
  "servings": 4,
  "tags": ["szybkie", "wegetariańskie"],
  "ingredients": [
    {{"name": "Nazwa składnika", "quantity": 200, "unit": "g"}}
  ],
  "instructions": [
    "Krok 1: ...",
    "Krok 2: ..."
  ]
}}

Odpowiedz TYLKO tablicą JSON z przepisami, bez dodatkowego tekstu."""

        logger.info(f"Calling AI ({provider_type}) with {len(products_list)} products")
        raw = await self._call_ai(provider_type, api_key, prompt)
        logger.info(f"AI response received, length={len(raw)}")

        try:
            # Extract JSON array from response
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array in response")
            recipes_data = json.loads(raw[start:end])
        except Exception as e:
            logger.error(f"Failed to parse AI recipe response: {e}\nRaw: {raw[:500]}")
            raise ValueError("AI returned invalid response. Try again.")

        results = []
        for r in recipes_data:
            try:
                results.append(FoodRecipeCreate(
                    name=r.get("name", "Przepis"),
                    description=r.get("description"),
                    prep_time_minutes=r.get("prep_time_minutes"),
                    servings=r.get("servings"),
                    tags=r.get("tags", []),
                    instructions=r.get("instructions", []),
                    ingredients=[
                        RecipeIngredientCreate(
                            name=i.get("name", "Składnik"),
                            quantity=i.get("quantity"),
                            unit=i.get("unit"),
                            food_product_id=None,
                        )
                        for i in r.get("ingredients", [])
                        if i.get("name")
                    ],
                    source="saved_from_ai",
                ))
            except Exception as e:
                logger.warning(f"Skipping malformed recipe: {e}")

        return results

    async def _call_ai(self, provider_type: OCRProvider, api_key: str, prompt: str) -> str:
        if provider_type == OCRProvider.CLAUDE:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        elif provider_type == OCRProvider.OPENAI:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
            )
            return response.choices[0].message.content

        elif provider_type == OCRProvider.GEMINI:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text

        raise RecipeAIUnavailableError(f"Unsupported provider: {provider_type}")

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    async def match_recipes(self, user_id: int) -> list[RecipeMatchResult]:
        # Load all user recipes with ingredients
        recipes_result = await self.db.execute(
            select(FoodRecipe)
            .where(FoodRecipe.user_id == user_id)
            .options(selectinload(FoodRecipe.ingredients))
        )
        recipes = recipes_result.scalars().all()

        if not recipes:
            return []

        # Load user inventory (available/opened)
        inv_result = await self.db.execute(
            select(FoodInventory)
            .where(
                FoodInventory.user_id == user_id,
                FoodInventory.status.in_(["available", "opened"]),
            )
            .options(selectinload(FoodInventory.product))
        )
        inventory = inv_result.scalars().all()

        # Build lookup: product_id → (total_quantity, unit, expiring_soon)
        now = datetime.now(timezone.utc).date()
        expiry_threshold = now + timedelta(days=3)

        inventory_by_product: dict[int, dict] = {}
        for item in inventory:
            pid = item.product_id
            expiring = False
            if item.expiry_date:
                try:
                    exp = datetime.fromisoformat(item.expiry_date).date()
                    expiring = exp <= expiry_threshold
                except Exception:
                    pass

            if pid not in inventory_by_product:
                inventory_by_product[pid] = {
                    "quantity": item.quantity or 0,
                    "unit": item.unit,
                    "expiring_soon": expiring,
                }
            else:
                inventory_by_product[pid]["quantity"] += item.quantity or 0
                if expiring:
                    inventory_by_product[pid]["expiring_soon"] = True

        # Also build lookup by normalized name for unlinked ingredients
        inv_by_name: dict[str, dict] = {}
        for item in inventory:
            key = item.product.name_normalized.lower()
            if key not in inv_by_name:
                inv_by_name[key] = inventory_by_product.get(item.product_id, {})

        results = []
        for recipe in recipes:
            if not recipe.ingredients:
                continue

            available = []
            missing = []
            expiring_count = 0

            for ing in recipe.ingredients:
                in_inv = False
                inv_qty = None
                inv_expiring = False

                if ing.food_product_id and ing.food_product_id in inventory_by_product:
                    inv_data = inventory_by_product[ing.food_product_id]
                    in_inv = True
                    inv_qty = inv_data["quantity"]
                    inv_expiring = inv_data["expiring_soon"]
                else:
                    # Try name-based match (normalize same way as name_normalized in DB)
                    # Also handle cases where AI adds descriptions like "Wołowina (mielona)"
                    name_key = normalize_name(ing.name)
                    matched_inv_data = inv_by_name.get(name_key)
                    if not matched_inv_data:
                        # Fuzzy: check if any inventory product name is contained in ingredient name or vice versa
                        for inv_name, inv_data in inv_by_name.items():
                            if inv_name in name_key or name_key.startswith(inv_name):
                                matched_inv_data = inv_data
                                break
                    if matched_inv_data:
                        in_inv = True
                        inv_qty = matched_inv_data.get("quantity")
                        inv_expiring = matched_inv_data.get("expiring_soon", False)

                match_ing = RecipeMatchIngredient(
                    name=ing.name,
                    quantity=ing.quantity,
                    unit=ing.unit,
                    food_product_id=ing.food_product_id,
                    in_inventory=in_inv,
                    inventory_quantity=inv_qty,
                    expiring_soon=inv_expiring,
                )

                if in_inv:
                    available.append(match_ing)
                    if inv_expiring:
                        expiring_count += 1
                else:
                    missing.append(match_ing)

            total = len(recipe.ingredients)
            match_pct = (len(available) / total * 100) if total > 0 else 0.0

            results.append(RecipeMatchResult(
                recipe=_recipe_to_response(recipe),
                match_percentage=round(match_pct, 1),
                missing_ingredients=missing,
                available_ingredients=available,
                expiring_soon_count=expiring_count,
            ))

        # Sort: expiring_soon_count desc, then match_percentage desc
        results.sort(key=lambda r: (r.expiring_soon_count, r.match_percentage), reverse=True)
        return results

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _get_or_404(self, recipe_id: int, user_id: int) -> FoodRecipe:
        result = await self.db.execute(
            select(FoodRecipe)
            .where(FoodRecipe.id == recipe_id)
            .options(selectinload(FoodRecipe.ingredients))
        )
        recipe = result.scalar_one_or_none()
        if recipe is None:
            raise RecipeNotFoundError(f"Recipe {recipe_id} not found")
        if recipe.user_id != user_id:
            raise RecipeAccessDeniedError("Access denied")
        return recipe
