"""
Food module service for business logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
import unicodedata
import re

from ..models import (
    FoodCategory,
    FoodProduct,
    FoodProductAlias,
    FoodPendingImport,
    FoodPendingImportItem,
    FoodInventory,
    FoodExpiryReminder,
    FoodReminderSettings,
    FoodConsumptionLog,
)
from ..schemas import (
    FoodProductCreate,
    FoodProductUpdate,
    FoodProductAliasCreate,
    FoodInventoryCreate,
    FoodInventoryUpdate,
    FoodPendingImportItemAccept,
    FoodReminderSettingsUpdate,
    FoodConsumptionLogCreate,
)
from ..repositories.food import (
    FoodCategoryRepository,
    FoodProductRepository,
    FoodProductAliasRepository,
    FoodPendingImportRepository,
    FoodPendingImportItemRepository,
    FoodInventoryRepository,
    FoodExpiryReminderRepository,
    FoodReminderSettingsRepository,
    FoodConsumptionLogRepository,
)
from ..repositories.household import HouseholdRepository


# ============================================================================
# Exceptions
# ============================================================================

class FoodCategoryNotFoundError(Exception):
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"Food category {category_id} not found")


class FoodProductNotFoundError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Food product {product_id} not found")


class FoodInventoryNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__(f"Inventory item {item_id} not found")


class FoodPendingImportNotFoundError(Exception):
    def __init__(self, import_id: int):
        self.import_id = import_id
        super().__init__(f"Pending import {import_id} not found")


class FoodPendingImportItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__(f"Pending import item {item_id} not found")


class FoodAccessDeniedError(Exception):
    def __init__(self, resource_type: str, resource_id: int):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"Access denied to {resource_type} {resource_id}")


class FoodReminderNotFoundError(Exception):
    def __init__(self, reminder_id: int):
        self.reminder_id = reminder_id
        super().__init__(f"Reminder {reminder_id} not found")


# ============================================================================
# Match Result
# ============================================================================

class MatchResult:
    """Result of product matching."""

    def __init__(
        self,
        product: Optional[FoodProduct] = None,
        method: Optional[str] = None,
        confidence: float = 0.0,
    ):
        self.product = product
        self.method = method
        self.confidence = confidence

    @property
    def matched(self) -> bool:
        return self.product is not None


# ============================================================================
# Helper Functions
# ============================================================================

def normalize_name(name: str) -> str:
    """
    Normalize a product name for matching.

    - Convert to lowercase
    - Remove accents/diacritics
    - Remove extra whitespace
    - Remove special characters
    """
    # Convert to lowercase
    name = name.lower()

    # Remove accents/diacritics
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))

    # Remove special characters except spaces
    name = re.sub(r"[^\w\s]", "", name)

    # Normalize whitespace
    name = " ".join(name.split())

    return name


def calculate_expiry_date(days: int) -> str:
    """Calculate expiry date from today + days."""
    return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")


# ============================================================================
# Food Service
# ============================================================================

class FoodService:
    """Main service for food module operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repo = FoodCategoryRepository(db)
        self.product_repo = FoodProductRepository(db)
        self.alias_repo = FoodProductAliasRepository(db)
        self.pending_import_repo = FoodPendingImportRepository(db)
        self.pending_item_repo = FoodPendingImportItemRepository(db)
        self.inventory_repo = FoodInventoryRepository(db)
        self.reminder_repo = FoodExpiryReminderRepository(db)
        self.settings_repo = FoodReminderSettingsRepository(db)
        self.consumption_repo = FoodConsumptionLogRepository(db)
        self.household_repo = HouseholdRepository(db)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    async def _resolve_household_id(self, household_uid: Optional[str]) -> Optional[int]:
        """Convert household UID (string) to household ID (int)."""
        if not household_uid:
            return None
        household = await self.household_repo.get_by_uid(household_uid)
        return household.id if household else None

    async def _check_inventory_access(
        self,
        item: FoodInventory,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> bool:
        """Check if user has access to an inventory item."""
        if item.user_id == user_id and item.household_id is None:
            return True
        if household_id and item.household_id == household_id:
            return True
        return False

    async def _check_pending_import_access(
        self,
        pending_import: FoodPendingImport,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> bool:
        """Check if user has access to a pending import."""
        if pending_import.user_id == user_id and pending_import.household_id is None:
            return True
        if household_id and pending_import.household_id == household_id:
            return True
        return False

    # -------------------------------------------------------------------------
    # Categories
    # -------------------------------------------------------------------------

    async def list_categories(self) -> List[FoodCategory]:
        """Get all food categories."""
        return await self.category_repo.get_all()

    async def get_category(self, category_id: int) -> FoodCategory:
        """Get a category by ID."""
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise FoodCategoryNotFoundError(category_id)
        return category

    # -------------------------------------------------------------------------
    # Products
    # -------------------------------------------------------------------------

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[FoodProduct]:
        """Get all products with optional filters."""
        return await self.product_repo.get_all(
            skip=skip,
            limit=limit,
            category_id=category_id,
            search=search,
        )

    async def get_product(self, product_id: int) -> FoodProduct:
        """Get a product by ID."""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise FoodProductNotFoundError(product_id)
        return product

    async def get_product_by_barcode(self, barcode: str) -> Optional[FoodProduct]:
        """Get a product by barcode."""
        return await self.product_repo.get_by_barcode(barcode)

    async def search_products(self, query: str, limit: int = 20) -> List[FoodProduct]:
        """Search products by name or barcode."""
        return await self.product_repo.search(query, limit)

    async def create_product(
        self,
        data: FoodProductCreate,
        user_id: int,
    ) -> FoodProduct:
        """Create a new product."""
        product = FoodProduct(
            name=data.name,
            name_normalized=normalize_name(data.name),
            barcode=data.barcode,
            barcode_type=data.barcode_type,
            food_category_id=data.food_category_id,
            calories=data.calories,
            protein=data.protein,
            carbohydrates=data.carbohydrates,
            fat=data.fat,
            fiber=data.fiber,
            sugar=data.sugar,
            sodium=data.sodium,
            default_unit=data.default_unit,
            is_verified=False,
            created_by_user_id=user_id,
        )
        created = await self.product_repo.create(product)
        return await self.product_repo.get_by_id(created.id)

    async def update_product(
        self,
        product_id: int,
        data: FoodProductUpdate,
    ) -> FoodProduct:
        """Update a product."""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise FoodProductNotFoundError(product_id)

        update_data = data.model_dump(exclude_unset=True)

        # Update name_normalized if name changed
        if "name" in update_data:
            update_data["name_normalized"] = normalize_name(update_data["name"])

        update_data["updated_at"] = datetime.utcnow().isoformat()

        for field, value in update_data.items():
            setattr(product, field, value)

        return await self.product_repo.update(product)

    # -------------------------------------------------------------------------
    # Product Aliases
    # -------------------------------------------------------------------------

    async def create_alias(
        self,
        data: FoodProductAliasCreate,
        user_id: int,
    ) -> FoodProductAlias:
        """Create a product alias."""
        alias = FoodProductAlias(
            product_id=data.product_id,
            alias=data.alias,
            alias_normalized=normalize_name(data.alias),
            source=data.source,
            created_by_user_id=user_id,
        )
        return await self.alias_repo.create(alias)

    async def get_aliases_for_product(self, product_id: int) -> List[FoodProductAlias]:
        """Get all aliases for a product."""
        return await self.alias_repo.get_by_product_id(product_id)

    # -------------------------------------------------------------------------
    # Product Matching
    # -------------------------------------------------------------------------

    async def match_product(self, original_name: str) -> MatchResult:
        """
        Match a product name to an existing product.

        Order of matching:
        1. Exact match on normalized name
        2. Match via alias
        3. Return None (for AI suggestion later)
        """
        name_normalized = normalize_name(original_name)

        # 1. Exact match on normalized name
        product = await self.product_repo.get_by_name_normalized(name_normalized)
        if product:
            return MatchResult(product=product, method="exact_name", confidence=1.0)

        # 2. Match via alias
        alias = await self.alias_repo.get_by_alias_normalized(name_normalized)
        if alias and alias.product:
            return MatchResult(product=alias.product, method="alias", confidence=0.9)

        # 3. No match found
        return MatchResult()

    # -------------------------------------------------------------------------
    # Pending Imports
    # -------------------------------------------------------------------------

    async def list_pending_imports(
        self,
        user_id: int,
        household_uid: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[FoodPendingImport]:
        """Get pending imports for user."""
        household_id = await self._resolve_household_id(household_uid)
        return await self.pending_import_repo.get_by_user(
            user_id=user_id,
            household_id=household_id,
            status=status,
        )

    async def get_pending_import(
        self,
        import_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> FoodPendingImport:
        """Get a pending import by ID."""
        pending_import = await self.pending_import_repo.get_by_id(import_id)
        if not pending_import:
            raise FoodPendingImportNotFoundError(import_id)

        household_id = await self._resolve_household_id(household_uid)
        if not await self._check_pending_import_access(pending_import, user_id, household_id):
            raise FoodAccessDeniedError("pending_import", import_id)

        return pending_import

    async def create_pending_import_from_receipt(
        self,
        receipt_id: int,
        items: List[dict],
        user_id: int,
        household_id: Optional[int] = None,
    ) -> FoodPendingImport:
        """
        Create a pending import from receipt items.

        Items format: [{"name": str, "quantity": int, "unit_price": float, "total_price": float}, ...]
        """
        # Create pending import
        pending_import = FoodPendingImport(
            receipt_id=receipt_id,
            user_id=user_id,
            household_id=household_id,
            status="pending",
        )
        pending_import = await self.pending_import_repo.create(pending_import)

        # Create pending import items with automatic matching
        for item in items:
            original_name = item.get("name", "")
            if not original_name:
                continue

            # Try to match the product
            match_result = await self.match_product(original_name)

            # Calculate suggested expiry date
            suggested_expiry_date = None
            if match_result.matched and match_result.product.food_category:
                category = match_result.product.food_category
                if category.default_expiry_days:
                    suggested_expiry_date = calculate_expiry_date(category.default_expiry_days)

            pending_item = FoodPendingImportItem(
                pending_import_id=pending_import.id,
                original_name=original_name,
                original_name_normalized=normalize_name(original_name),
                quantity=item.get("quantity", 1),
                unit_price=item.get("unit_price"),
                total_price=item.get("total_price"),
                matched_product_id=match_result.product.id if match_result.matched else None,
                match_method=match_result.method,
                match_confidence=match_result.confidence,
                suggested_expiry_date=suggested_expiry_date,
                status="pending",
            )
            await self.pending_item_repo.create(pending_item)

        # Refresh to get items
        return await self.pending_import_repo.get_by_id(pending_import.id)

    async def accept_pending_import_item(
        self,
        import_id: int,
        item_id: int,
        data: FoodPendingImportItemAccept,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> FoodInventory:
        """Accept a pending import item and add to inventory."""
        household_id = await self._resolve_household_id(household_uid)

        # Get and validate pending import
        pending_import = await self.pending_import_repo.get_by_id(import_id)
        if not pending_import:
            raise FoodPendingImportNotFoundError(import_id)
        if not await self._check_pending_import_access(pending_import, user_id, household_id):
            raise FoodAccessDeniedError("pending_import", import_id)

        # Get and validate item
        item = await self.pending_item_repo.get_by_id(item_id)
        if not item or item.pending_import_id != import_id:
            raise FoodPendingImportItemNotFoundError(item_id)

        # Determine final product
        final_product_id = data.final_product_id
        created_new_product = False

        if not final_product_id and data.new_product_name:
            # Create new product
            new_product = FoodProduct(
                name=data.new_product_name,
                name_normalized=normalize_name(data.new_product_name),
                food_category_id=data.new_product_category_id,
                created_by_user_id=user_id,
            )
            new_product = await self.product_repo.create(new_product)
            final_product_id = new_product.id
            created_new_product = True

            # Create alias from original name
            alias = FoodProductAlias(
                product_id=new_product.id,
                alias=item.original_name,
                alias_normalized=item.original_name_normalized,
                source="ocr",
                created_by_user_id=user_id,
            )
            await self.alias_repo.create(alias)
        elif not final_product_id and item.matched_product_id:
            final_product_id = item.matched_product_id

        if not final_product_id:
            raise ValueError("No product specified and no match found")

        # Update pending item
        item.status = "accepted"
        item.final_product_id = final_product_id
        item.final_expiry_date = data.final_expiry_date or item.suggested_expiry_date
        item.final_quantity = data.final_quantity or item.quantity or 1
        item.final_unit = data.final_unit or "szt"
        item.created_new_product = created_new_product
        item.processed_at = datetime.utcnow().isoformat()
        await self.pending_item_repo.update(item)

        # Add to inventory
        inventory_item = FoodInventory(
            user_id=user_id,
            household_id=household_id,
            product_id=final_product_id,
            quantity=item.final_quantity,
            unit=item.final_unit,
            purchase_date=datetime.utcnow().strftime("%Y-%m-%d"),
            expiry_date=item.final_expiry_date,
            receipt_id=pending_import.receipt_id,
            pending_import_item_id=item.id,
            added_manually=False,
            status="available",
            location="pantry",
        )
        inventory_item = await self.inventory_repo.create(inventory_item)

        # Create reminder if expiry date is set
        if item.final_expiry_date:
            await self._create_expiry_reminder(inventory_item, user_id)

        # Update pending import status
        await self._update_pending_import_status(import_id)

        return await self.inventory_repo.get_by_id(inventory_item.id)

    async def reject_pending_import_item(
        self,
        import_id: int,
        item_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> None:
        """Reject a pending import item."""
        household_id = await self._resolve_household_id(household_uid)

        pending_import = await self.pending_import_repo.get_by_id(import_id)
        if not pending_import:
            raise FoodPendingImportNotFoundError(import_id)
        if not await self._check_pending_import_access(pending_import, user_id, household_id):
            raise FoodAccessDeniedError("pending_import", import_id)

        item = await self.pending_item_repo.get_by_id(item_id)
        if not item or item.pending_import_id != import_id:
            raise FoodPendingImportItemNotFoundError(item_id)

        item.status = "rejected"
        item.processed_at = datetime.utcnow().isoformat()
        await self.pending_item_repo.update(item)

        await self._update_pending_import_status(import_id)

    async def _update_pending_import_status(self, import_id: int) -> None:
        """Update pending import status based on items."""
        pending_import = await self.pending_import_repo.get_by_id(import_id)
        if not pending_import:
            return

        items = pending_import.items
        if not items:
            return

        pending_count = sum(1 for i in items if i.status == "pending")
        accepted_count = sum(1 for i in items if i.status == "accepted")
        rejected_count = sum(1 for i in items if i.status == "rejected")

        if pending_count == 0:
            if accepted_count > 0 and rejected_count > 0:
                status = "partially_accepted"
            elif accepted_count > 0:
                status = "accepted"
            else:
                status = "rejected"

            pending_import.status = status
            pending_import.processed_at = datetime.utcnow().isoformat()
            await self.pending_import_repo.update(pending_import)

    # -------------------------------------------------------------------------
    # Inventory
    # -------------------------------------------------------------------------

    async def list_inventory(
        self,
        user_id: int,
        household_uid: Optional[str] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        category_id: Optional[int] = None,
        expiring_within_days: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FoodInventory]:
        """Get inventory items with filters."""
        household_id = await self._resolve_household_id(household_uid)

        expiring_before = None
        if expiring_within_days:
            expiring_before = (datetime.utcnow() + timedelta(days=expiring_within_days)).strftime("%Y-%m-%d")

        return await self.inventory_repo.get_all(
            user_id=user_id,
            household_id=household_id,
            status=status,
            location=location,
            category_id=category_id,
            expiring_before=expiring_before,
            skip=skip,
            limit=limit,
        )

    async def get_inventory_item(
        self,
        item_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> FoodInventory:
        """Get an inventory item by ID."""
        item = await self.inventory_repo.get_by_id(item_id)
        if not item:
            raise FoodInventoryNotFoundError(item_id)

        household_id = await self._resolve_household_id(household_uid)
        if not await self._check_inventory_access(item, user_id, household_id):
            raise FoodAccessDeniedError("inventory", item_id)

        return item

    async def add_to_inventory(
        self,
        data: FoodInventoryCreate,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> FoodInventory:
        """Manually add an item to inventory."""
        household_id = await self._resolve_household_id(household_uid)

        # Validate product exists
        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise FoodProductNotFoundError(data.product_id)

        item = FoodInventory(
            user_id=user_id,
            household_id=household_id,
            product_id=data.product_id,
            quantity=data.quantity,
            unit=data.unit,
            purchase_date=data.purchase_date or datetime.utcnow().strftime("%Y-%m-%d"),
            expiry_date=data.expiry_date,
            added_manually=True,
            status="available",
            location=data.location,
            notes=data.notes,
        )
        item = await self.inventory_repo.create(item)

        # Create reminder if expiry date is set
        if data.expiry_date:
            await self._create_expiry_reminder(item, user_id)

        return await self.inventory_repo.get_by_id(item.id)

    async def update_inventory_item(
        self,
        item_id: int,
        data: FoodInventoryUpdate,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> FoodInventory:
        """Update an inventory item."""
        item = await self.inventory_repo.get_by_id(item_id)
        if not item:
            raise FoodInventoryNotFoundError(item_id)

        household_id = await self._resolve_household_id(household_uid)
        if not await self._check_inventory_access(item, user_id, household_id):
            raise FoodAccessDeniedError("inventory", item_id)

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()

        old_expiry = item.expiry_date
        for field, value in update_data.items():
            setattr(item, field, value)

        item = await self.inventory_repo.update(item)

        # Update reminders if expiry date changed
        if "expiry_date" in update_data and update_data["expiry_date"] != old_expiry:
            await self.reminder_repo.delete_by_inventory_item(item_id)
            if item.expiry_date:
                await self._create_expiry_reminder(item, user_id)

        return item

    async def delete_inventory_item(
        self,
        item_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> None:
        """Delete an inventory item."""
        item = await self.inventory_repo.get_by_id(item_id)
        if not item:
            raise FoodInventoryNotFoundError(item_id)

        household_id = await self._resolve_household_id(household_uid)
        if not await self._check_inventory_access(item, user_id, household_id):
            raise FoodAccessDeniedError("inventory", item_id)

        await self.inventory_repo.delete(item)

    async def consume_inventory_item(
        self,
        item_id: int,
        quantity: Optional[float],
        user_id: int,
        household_uid: Optional[str] = None,
        meal_type: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> FoodInventory:
        """Consume (part of) an inventory item."""
        item = await self.inventory_repo.get_by_id(item_id)
        if not item:
            raise FoodInventoryNotFoundError(item_id)

        household_id = await self._resolve_household_id(household_uid)
        if not await self._check_inventory_access(item, user_id, household_id):
            raise FoodAccessDeniedError("inventory", item_id)

        consume_quantity = quantity or item.quantity

        # Log consumption
        product = await self.product_repo.get_by_id(item.product_id)
        log = FoodConsumptionLog(
            user_id=user_id,
            product_id=item.product_id,
            inventory_item_id=item_id,
            quantity=consume_quantity,
            unit=item.unit,
            calories=product.calories if product else None,
            protein=product.protein if product else None,
            carbohydrates=product.carbohydrates if product else None,
            fat=product.fat if product else None,
            consumed_at=datetime.utcnow().isoformat(),
            meal_type=meal_type,
            notes=notes,
        )
        await self.consumption_repo.create(log)

        # Update inventory
        if consume_quantity >= item.quantity:
            item.quantity = 0
            item.status = "consumed"
        else:
            item.quantity -= consume_quantity

        item.updated_at = datetime.utcnow().isoformat()
        return await self.inventory_repo.update(item)

    async def open_inventory_item(
        self,
        item_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> FoodInventory:
        """Mark an inventory item as opened."""
        item = await self.inventory_repo.get_by_id(item_id)
        if not item:
            raise FoodInventoryNotFoundError(item_id)

        household_id = await self._resolve_household_id(household_uid)
        if not await self._check_inventory_access(item, user_id, household_id):
            raise FoodAccessDeniedError("inventory", item_id)

        item.status = "opened"
        item.opened_date = datetime.utcnow().strftime("%Y-%m-%d")
        item.updated_at = datetime.utcnow().isoformat()
        return await self.inventory_repo.update(item)

    async def get_expiring_soon(
        self,
        user_id: int,
        household_uid: Optional[str] = None,
        days: int = 3,
    ) -> List[FoodInventory]:
        """Get items expiring within specified days."""
        household_id = await self._resolve_household_id(household_uid)
        return await self.inventory_repo.get_expiring_soon(
            user_id=user_id,
            household_id=household_id,
            days=days,
        )

    # -------------------------------------------------------------------------
    # Reminders
    # -------------------------------------------------------------------------

    async def _create_expiry_reminder(
        self,
        inventory_item: FoodInventory,
        user_id: int,
    ) -> FoodExpiryReminder:
        """Create an expiry reminder for an inventory item."""
        if not inventory_item.expiry_date:
            return None

        # Get user's reminder settings
        settings = await self.settings_repo.get_by_user_id(user_id)
        if not settings:
            settings = FoodReminderSettings(user_id=user_id)
            settings = await self.settings_repo.create(settings)

        if not settings.enabled:
            return None

        # Determine days before based on category
        days_before = settings.default_days_before
        # Could add category-specific logic here

        # Calculate remind_at date
        expiry_date = datetime.strptime(inventory_item.expiry_date, "%Y-%m-%d")
        remind_at = expiry_date - timedelta(days=days_before)

        # Don't create if remind_at is in the past
        if remind_at < datetime.utcnow():
            remind_at = datetime.utcnow()

        reminder = FoodExpiryReminder(
            user_id=user_id,
            inventory_item_id=inventory_item.id,
            remind_at=remind_at.strftime("%Y-%m-%d"),
            days_before_expiry=days_before,
            status="pending",
        )
        return await self.reminder_repo.create(reminder)

    async def list_reminders(self, user_id: int) -> List[FoodExpiryReminder]:
        """Get pending reminders for a user."""
        return await self.reminder_repo.get_pending_for_user(user_id)

    async def dismiss_reminder(self, reminder_id: int, user_id: int) -> None:
        """Dismiss a reminder."""
        reminder = await self.reminder_repo.get_by_id(reminder_id)
        if not reminder:
            raise FoodReminderNotFoundError(reminder_id)
        if reminder.user_id != user_id:
            raise FoodAccessDeniedError("reminder", reminder_id)

        await self.reminder_repo.update_status(reminder_id, "dismissed")

    # -------------------------------------------------------------------------
    # Reminder Settings
    # -------------------------------------------------------------------------

    async def get_reminder_settings(self, user_id: int) -> FoodReminderSettings:
        """Get user's reminder settings."""
        settings = await self.settings_repo.get_by_user_id(user_id)
        if not settings:
            settings = FoodReminderSettings(user_id=user_id)
            settings = await self.settings_repo.create(settings)
        return settings

    async def update_reminder_settings(
        self,
        user_id: int,
        data: FoodReminderSettingsUpdate,
    ) -> FoodReminderSettings:
        """Update user's reminder settings."""
        settings = await self.settings_repo.get_by_user_id(user_id)
        if not settings:
            settings = FoodReminderSettings(user_id=user_id)
            settings = await self.settings_repo.create(settings)

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()

        for field, value in update_data.items():
            setattr(settings, field, value)

        return await self.settings_repo.update(settings)

    # -------------------------------------------------------------------------
    # Consumption Log
    # -------------------------------------------------------------------------

    async def list_consumption_logs(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        meal_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FoodConsumptionLog]:
        """Get consumption logs for a user."""
        return await self.consumption_repo.get_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            meal_type=meal_type,
            skip=skip,
            limit=limit,
        )
