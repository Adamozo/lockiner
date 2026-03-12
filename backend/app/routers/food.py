"""
Food module API router.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import (
    FoodCategoryResponse,
    FoodProductCreate,
    FoodProductUpdate,
    FoodProductResponse,
    FoodProductAliasCreate,
    FoodProductAliasResponse,
    FoodPendingImportResponse,
    FoodPendingImportItemAccept,
    FoodInventoryCreate,
    FoodInventoryUpdate,
    FoodInventoryResponse,
    FoodInventoryConsumeRequest,
    FoodExpiryReminderResponse,
    FoodReminderSettingsResponse,
    FoodReminderSettingsUpdate,
    FoodConsumptionLogResponse,
    DirectConsumptionRequest,
    DailyNutritionSummary,
    FoodDailyGoalResponse,
    FoodDailyGoalUpdate,
    WeeklyNutritionDay,
)
from ..services.food import (
    FoodService,
    FoodCategoryNotFoundError,
    FoodProductNotFoundError,
    FoodInventoryNotFoundError,
    FoodPendingImportNotFoundError,
    FoodPendingImportItemNotFoundError,
    FoodAccessDeniedError,
    FoodReminderNotFoundError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/food", tags=["food"])

# ---------------------------------------


async def get_food_service(db: AsyncSession = Depends(get_db)) -> FoodService:
    return FoodService(db)


# ============================================================================
# Categories
# ============================================================================

@router.get("/categories", response_model=List[FoodCategoryResponse])
async def list_categories(
    service: FoodService = Depends(get_food_service),
):
    """Get all food categories."""
    return await service.list_categories()


@router.get("/categories/{category_id}", response_model=FoodCategoryResponse)
async def get_category(
    category_id: int,
    service: FoodService = Depends(get_food_service),
):
    """Get a food category by ID."""
    try:
        return await service.get_category(category_id)
    except FoodCategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Products
# ============================================================================

@router.get("/products", response_model=List[FoodProductResponse])
async def list_products(
    search: Optional[str] = Query(None, description="Search by name or barcode"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: FoodService = Depends(get_food_service),
):
    """Get all products with optional filters."""
    return await service.list_products(
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
    )


@router.get("/products/search", response_model=List[FoodProductResponse])
async def search_products(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=50),
    service: FoodService = Depends(get_food_service),
):
    """Search products by name or barcode."""
    return await service.search_products(query, limit)


@router.get("/products/barcode/{barcode}", response_model=FoodProductResponse)
async def get_product_by_barcode(
    barcode: str,
    service: FoodService = Depends(get_food_service),
):
    """Get a product by barcode."""
    product = await service.get_product_by_barcode(barcode)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with barcode {barcode} not found",
        )
    return product


@router.get("/products/scan/{ean}")
async def scan_barcode(
    ean: str,
    household_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Scan a barcode and return product + inventory availability."""
    result = await service.scan_barcode(current_user.id, ean, household_uid=household_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Serialize result
    product_data = None
    if result.get("product"):
        p = result["product"]
        product_data = {
            "id": p.id,
            "name": p.name,
            "barcode": p.barcode,
            "calories": p.calories,
            "protein": p.protein,
            "carbohydrates": p.carbohydrates,
            "fat": p.fat,
            "default_unit": p.default_unit,
        }

    off_data = None
    if result.get("off_product"):
        op = result["off_product"]
        n = op.get("nutriments", {})
        cal = op.get("calories") or n.get("energy-kcal_100g") or n.get("energy_100g")
        off_data = {
            "code": op.get("code", ean),
            "name": op.get("product_name") or op.get("product_name_pl") or op.get("product_name_en"),
            "brands": op.get("brands"),
            "quantity": op.get("quantity"),
            "nutriscore_grade": op.get("nutriscore_grade"),
            "calories_100g": cal,
            "protein_100g": op.get("protein") or n.get("proteins_100g"),
            "carbohydrates_100g": op.get("carbohydrates") or n.get("carbohydrates_100g"),
            "fat_100g": op.get("fat") or n.get("fat_100g"),
            "image_url": op.get("image_url_full") or op.get("image_url"),
        }

    inv_items = [
        {"id": i.id, "location": i.location, "quantity": i.quantity, "unit": i.unit, "expiry_date": i.expiry_date, "status": i.status}
        for i in result.get("inventory_items", [])
    ]

    return {
        "source": result["source"],
        "product": product_data,
        "off_product": off_data,
        "inventory_items": inv_items,
        "in_stock": len(inv_items) > 0,
    }


@router.get("/products/search-global")
async def search_products_global(
    q: str = Query(..., min_length=1),
    lang: Optional[str] = Query(None),
    household_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Search products in local DB + OFF catalog."""
    results = await service.search_products_global(
        user_id=current_user.id,
        query=q,
        lang=lang,
        household_uid=household_id,
    )
    # Serialize
    serialized = []
    for r in results:
        product_data = None
        if r.get("product"):
            p = r["product"]
            product_data = {
                "id": p.id,
                "name": p.name,
                "barcode": p.barcode,
                "calories": p.calories,
                "protein": p.protein,
                "carbohydrates": p.carbohydrates,
                "fat": p.fat,
                "default_unit": p.default_unit,
            }
        off_data = None
        if r.get("off_product"):
            op = r["off_product"]
            n = op.get("nutriments", {})
            cal = op.get("calories") or n.get("energy-kcal_100g") or n.get("energy_100g")
            off_data = {
                "code": op.get("code"),
                "name": op.get("product_name") or op.get("product_name_pl") or op.get("product_name_en"),
                "brands": op.get("brands"),
                "quantity": op.get("quantity"),
                "nutriscore_grade": op.get("nutriscore_grade"),
                "calories_100g": cal,
                "protein_100g": op.get("protein") or n.get("proteins_100g"),
                "carbohydrates_100g": op.get("carbohydrates") or n.get("carbohydrates_100g"),
                "fat_100g": op.get("fat") or n.get("fat_100g"),
                "image_url": op.get("image_url_full") or op.get("image_url"),
            }
        inv_items = [
            {"id": i.id, "location": i.location, "quantity": i.quantity, "unit": i.unit, "expiry_date": i.expiry_date, "status": i.status}
            for i in r.get("inventory_items", [])
        ]
        serialized.append({
            "source": r["source"],
            "product": product_data,
            "off_product": off_data,
            "inventory_items": inv_items,
            "in_stock": r.get("in_stock", False),
        })
    return serialized


@router.get("/products/{product_id}", response_model=FoodProductResponse)
async def get_product(
    product_id: int,
    service: FoodService = Depends(get_food_service),
):
    """Get a product by ID."""
    try:
        return await service.get_product(product_id)
    except FoodProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/products", response_model=FoodProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: FoodProductCreate,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Create a new product."""
    return await service.create_product(data, current_user.id)


@router.put("/products/{product_id}", response_model=FoodProductResponse)
async def update_product(
    product_id: int,
    data: FoodProductUpdate,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Update a product."""
    try:
        return await service.update_product(product_id, data)
    except FoodProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Product Aliases
# ============================================================================

@router.get("/products/{product_id}/aliases", response_model=List[FoodProductAliasResponse])
async def get_product_aliases(
    product_id: int,
    service: FoodService = Depends(get_food_service),
):
    """Get all aliases for a product."""
    return await service.get_aliases_for_product(product_id)


@router.post("/products/aliases", response_model=FoodProductAliasResponse, status_code=status.HTTP_201_CREATED)
async def create_product_alias(
    data: FoodProductAliasCreate,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Create a product alias."""
    return await service.create_alias(data, current_user.id)


# ============================================================================
# Pending Imports
# ============================================================================

@router.get("/pending-imports", response_model=List[FoodPendingImportResponse])
async def list_pending_imports(
    household_id: Optional[str] = Query(None, description="Household UUID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get pending imports for the current user."""
    return await service.list_pending_imports(
        user_id=current_user.id,
        household_uid=household_id,
        status=status_filter,
    )


@router.get("/pending-imports/{import_id}", response_model=FoodPendingImportResponse)
async def get_pending_import(
    import_id: int,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get a pending import by ID."""
    try:
        return await service.get_pending_import(
            import_id,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodPendingImportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/pending-imports/{import_id}/items/{item_id}/accept", response_model=FoodInventoryResponse)
async def accept_pending_import_item(
    import_id: int,
    item_id: int,
    data: FoodPendingImportItemAccept,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Accept a pending import item and add to inventory."""
    try:
        return await service.accept_pending_import_item(
            import_id,
            item_id,
            data,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodPendingImportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodPendingImportItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/pending-imports/{import_id}/items/{item_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_pending_import_item(
    import_id: int,
    item_id: int,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Reject a pending import item."""
    try:
        await service.reject_pending_import_item(
            import_id,
            item_id,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodPendingImportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodPendingImportItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ============================================================================
# Inventory
# ============================================================================

@router.get("/inventory", response_model=List[FoodInventoryResponse])
async def list_inventory(
    household_id: Optional[str] = Query(None, description="Household UUID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location (fridge, freezer, pantry)"),
    category_id: Optional[int] = Query(None, description="Filter by product category"),
    expiring_days: Optional[int] = Query(None, ge=1, description="Show items expiring within N days"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get inventory items with filters."""
    return await service.list_inventory(
        user_id=current_user.id,
        household_uid=household_id,
        status=status_filter,
        location=location,
        category_id=category_id,
        expiring_within_days=expiring_days,
        skip=skip,
        limit=limit,
    )


@router.get("/inventory/expiring", response_model=List[FoodInventoryResponse])
async def get_expiring_inventory(
    household_id: Optional[str] = Query(None, description="Household UUID"),
    days: int = Query(3, ge=1, le=30, description="Days until expiry"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get items expiring within specified days."""
    return await service.get_expiring_soon(
        user_id=current_user.id,
        household_uid=household_id,
        days=days,
    )


@router.get("/inventory/{item_id}", response_model=FoodInventoryResponse)
async def get_inventory_item(
    item_id: int,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get an inventory item by ID."""
    try:
        return await service.get_inventory_item(
            item_id,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodInventoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/inventory", response_model=FoodInventoryResponse, status_code=status.HTTP_201_CREATED)
async def add_to_inventory(
    data: FoodInventoryCreate,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Manually add an item to inventory."""
    try:
        return await service.add_to_inventory(
            data,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/inventory/{item_id}", response_model=FoodInventoryResponse)
async def update_inventory_item(
    item_id: int,
    data: FoodInventoryUpdate,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Update an inventory item."""
    try:
        return await service.update_inventory_item(
            item_id,
            data,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodInventoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/inventory/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: int,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Remove an item from inventory."""
    try:
        await service.delete_inventory_item(
            item_id,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodInventoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/inventory/{item_id}/consume", response_model=FoodInventoryResponse)
async def consume_inventory_item(
    item_id: int,
    data: FoodInventoryConsumeRequest,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Consume (part of) an inventory item."""
    try:
        return await service.consume_inventory_item(
            item_id,
            quantity=data.quantity,
            user_id=current_user.id,
            household_uid=household_id,
            meal_type=data.meal_type,
            notes=data.notes,
        )
    except FoodInventoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/inventory/{item_id}/open", response_model=FoodInventoryResponse)
async def open_inventory_item(
    item_id: int,
    household_id: Optional[str] = Query(None, description="Household UUID"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Mark an inventory item as opened."""
    try:
        return await service.open_inventory_item(
            item_id,
            user_id=current_user.id,
            household_uid=household_id,
        )
    except FoodInventoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ============================================================================
# Reminders
# ============================================================================

@router.get("/reminders", response_model=List[FoodExpiryReminderResponse])
async def list_reminders(
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get pending expiry reminders for the current user."""
    return await service.list_reminders(current_user.id)


@router.post("/reminders/{reminder_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Dismiss an expiry reminder."""
    try:
        await service.dismiss_reminder(reminder_id, current_user.id)
    except FoodReminderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except FoodAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ============================================================================
# Reminder Settings
# ============================================================================

@router.get("/settings/reminders", response_model=FoodReminderSettingsResponse)
async def get_reminder_settings(
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get user's reminder settings."""
    return await service.get_reminder_settings(current_user.id)


@router.put("/settings/reminders", response_model=FoodReminderSettingsResponse)
async def update_reminder_settings(
    data: FoodReminderSettingsUpdate,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Update user's reminder settings."""
    return await service.update_reminder_settings(current_user.id, data)


# ============================================================================
# Consumption Logs
# ============================================================================

@router.get("/consumption", response_model=List[FoodConsumptionLogResponse])
async def list_consumption_logs(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get consumption logs for the current user."""
    return await service.list_consumption_logs(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        meal_type=meal_type,
        skip=skip,
        limit=limit,
    )


@router.post("/consumption/direct", response_model=FoodConsumptionLogResponse)
async def log_consumption_direct(
    data: DirectConsumptionRequest,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Log food consumption directly without using inventory."""
    return await service.log_consumption_direct(current_user.id, data)


@router.delete("/consumption/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consumption_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Delete a consumption log entry."""
    try:
        await service.delete_consumption_log(log_id, current_user.id)
    except FoodInventoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FoodAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/consumption/daily-summary")
async def get_daily_summary(
    date: Optional[str] = Query(None, description="Date YYYY-MM-DD, defaults to today"),
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get daily nutrition summary."""
    from datetime import datetime
    if not date:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    return await service.get_daily_summary(current_user.id, date)


@router.get("/consumption/weekly-summary")
async def get_weekly_summary(
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get 7-day calorie trend."""
    return await service.get_weekly_summary(current_user.id)


# ============================================================================
# Daily Goals
# ============================================================================

@router.get("/goals", response_model=FoodDailyGoalResponse)
async def get_daily_goal(
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Get user's daily nutrition goal."""
    return await service.get_daily_goal(current_user.id)


@router.put("/goals", response_model=FoodDailyGoalResponse)
async def update_daily_goal(
    data: FoodDailyGoalUpdate,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    """Update user's daily nutrition goal."""
    return await service.update_daily_goal(current_user.id, data)
