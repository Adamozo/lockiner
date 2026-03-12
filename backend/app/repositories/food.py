"""
Food module repositories for database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta

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
    FoodDailyGoal,
)


class FoodCategoryRepository:
    """Repository for food categories."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[FoodCategory]:
        """Get all food categories."""
        result = await self.db.execute(
            select(FoodCategory).order_by(FoodCategory.name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Optional[FoodCategory]:
        """Get category by ID."""
        result = await self.db.execute(
            select(FoodCategory).filter(FoodCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[FoodCategory]:
        """Get category by name."""
        result = await self.db.execute(
            select(FoodCategory).filter(FoodCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, category: FoodCategory) -> FoodCategory:
        """Create a new category."""
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category: FoodCategory) -> FoodCategory:
        """Update an existing category."""
        await self.db.commit()
        await self.db.refresh(category)
        return category


class FoodProductRepository:
    """Repository for food products."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[FoodProduct]:
        """Get all products with optional filters."""
        query = select(FoodProduct).options(selectinload(FoodProduct.food_category))

        if category_id:
            query = query.filter(FoodProduct.food_category_id == category_id)

        if search:
            search_normalized = search.lower().strip()
            query = query.filter(
                or_(
                    FoodProduct.name_normalized.contains(search_normalized),
                    FoodProduct.barcode == search,
                )
            )

        query = query.order_by(FoodProduct.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, product_id: int) -> Optional[FoodProduct]:
        """Get product by ID."""
        result = await self.db.execute(
            select(FoodProduct)
            .options(selectinload(FoodProduct.food_category))
            .filter(FoodProduct.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name_normalized(self, name_normalized: str) -> Optional[FoodProduct]:
        """Get product by normalized name."""
        result = await self.db.execute(
            select(FoodProduct)
            .options(selectinload(FoodProduct.food_category))
            .filter(FoodProduct.name_normalized == name_normalized)
        )
        return result.scalar_one_or_none()

    async def get_by_barcode(self, barcode: str) -> Optional[FoodProduct]:
        """Get product by barcode."""
        result = await self.db.execute(
            select(FoodProduct)
            .options(selectinload(FoodProduct.food_category))
            .filter(FoodProduct.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 20) -> List[FoodProduct]:
        """Search products by name or barcode."""
        search_normalized = query.lower().strip()
        result = await self.db.execute(
            select(FoodProduct)
            .options(selectinload(FoodProduct.food_category))
            .filter(
                or_(
                    FoodProduct.name_normalized.contains(search_normalized),
                    FoodProduct.barcode == query,
                )
            )
            .order_by(FoodProduct.name)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, product: FoodProduct) -> FoodProduct:
        """Create a new product."""
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product: FoodProduct) -> FoodProduct:
        """Update an existing product."""
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: FoodProduct) -> None:
        """Delete a product."""
        await self.db.delete(product)
        await self.db.commit()


class FoodProductAliasRepository:
    """Repository for product aliases."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_alias_normalized(self, alias_normalized: str) -> Optional[FoodProductAlias]:
        """Get alias by normalized alias string."""
        result = await self.db.execute(
            select(FoodProductAlias)
            .options(selectinload(FoodProductAlias.product))
            .filter(FoodProductAlias.alias_normalized == alias_normalized)
        )
        return result.scalar_one_or_none()

    async def get_by_product_id(self, product_id: int) -> List[FoodProductAlias]:
        """Get all aliases for a product."""
        result = await self.db.execute(
            select(FoodProductAlias)
            .filter(FoodProductAlias.product_id == product_id)
            .order_by(FoodProductAlias.alias)
        )
        return list(result.scalars().all())

    async def create(self, alias: FoodProductAlias) -> FoodProductAlias:
        """Create a new alias."""
        self.db.add(alias)
        await self.db.commit()
        await self.db.refresh(alias)
        return alias

    async def delete(self, alias: FoodProductAlias) -> None:
        """Delete an alias."""
        await self.db.delete(alias)
        await self.db.commit()


class FoodPendingImportRepository:
    """Repository for pending food imports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(
        self,
        user_id: int,
        household_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[FoodPendingImport]:
        """Get pending imports for a user."""
        query = select(FoodPendingImport).options(
            selectinload(FoodPendingImport.items)
        )

        if household_id:
            query = query.filter(FoodPendingImport.household_id == household_id)
        else:
            query = query.filter(
                FoodPendingImport.user_id == user_id,
                FoodPendingImport.household_id.is_(None),
            )

        if status:
            query = query.filter(FoodPendingImport.status == status)

        query = query.order_by(FoodPendingImport.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, import_id: int) -> Optional[FoodPendingImport]:
        """Get pending import by ID."""
        result = await self.db.execute(
            select(FoodPendingImport)
            .options(selectinload(FoodPendingImport.items))
            .filter(FoodPendingImport.id == import_id)
        )
        return result.scalar_one_or_none()

    async def get_by_receipt_id(self, receipt_id: int) -> Optional[FoodPendingImport]:
        """Get pending import by receipt ID."""
        result = await self.db.execute(
            select(FoodPendingImport)
            .options(selectinload(FoodPendingImport.items))
            .filter(FoodPendingImport.receipt_id == receipt_id)
        )
        return result.scalar_one_or_none()

    async def create(self, pending_import: FoodPendingImport) -> FoodPendingImport:
        """Create a new pending import."""
        self.db.add(pending_import)
        await self.db.commit()
        await self.db.refresh(pending_import)
        return pending_import

    async def update(self, pending_import: FoodPendingImport) -> FoodPendingImport:
        """Update a pending import."""
        await self.db.commit()
        await self.db.refresh(pending_import)
        return pending_import

    async def update_status(self, import_id: int, status: str) -> None:
        """Update pending import status."""
        result = await self.db.execute(
            select(FoodPendingImport).filter(FoodPendingImport.id == import_id)
        )
        pending_import = result.scalar_one_or_none()
        if pending_import:
            pending_import.status = status
            if status in ["accepted", "rejected"]:
                pending_import.processed_at = datetime.utcnow().isoformat()
            await self.db.commit()


class FoodPendingImportItemRepository:
    """Repository for pending import items."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_import_id(self, import_id: int) -> List[FoodPendingImportItem]:
        """Get all items for a pending import."""
        result = await self.db.execute(
            select(FoodPendingImportItem)
            .options(
                selectinload(FoodPendingImportItem.matched_product),
                selectinload(FoodPendingImportItem.final_product),
            )
            .filter(FoodPendingImportItem.pending_import_id == import_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, item_id: int) -> Optional[FoodPendingImportItem]:
        """Get item by ID."""
        result = await self.db.execute(
            select(FoodPendingImportItem)
            .options(
                selectinload(FoodPendingImportItem.matched_product),
                selectinload(FoodPendingImportItem.final_product),
            )
            .filter(FoodPendingImportItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create(self, item: FoodPendingImportItem) -> FoodPendingImportItem:
        """Create a new pending import item."""
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update(self, item: FoodPendingImportItem) -> FoodPendingImportItem:
        """Update a pending import item."""
        await self.db.commit()
        await self.db.refresh(item)
        return item


class FoodInventoryRepository:
    """Repository for food inventory."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        user_id: int,
        household_id: Optional[int] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        category_id: Optional[int] = None,
        expiring_before: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FoodInventory]:
        """Get inventory items with filters."""
        query = select(FoodInventory).options(
            selectinload(FoodInventory.product).selectinload(FoodProduct.food_category)
        )

        if household_id:
            query = query.filter(FoodInventory.household_id == household_id)
        else:
            query = query.filter(
                FoodInventory.user_id == user_id,
                FoodInventory.household_id.is_(None),
            )

        if status:
            query = query.filter(FoodInventory.status == status)

        if location:
            query = query.filter(FoodInventory.location == location)

        if category_id:
            query = query.join(FoodProduct).filter(FoodProduct.food_category_id == category_id)

        if expiring_before:
            query = query.filter(
                FoodInventory.expiry_date.isnot(None),
                FoodInventory.expiry_date <= expiring_before,
                FoodInventory.status.in_(["available", "opened"]),
            )

        query = query.order_by(FoodInventory.expiry_date.asc().nulls_last()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, item_id: int) -> Optional[FoodInventory]:
        """Get inventory item by ID."""
        result = await self.db.execute(
            select(FoodInventory)
            .options(
                selectinload(FoodInventory.product).selectinload(FoodProduct.food_category)
            )
            .filter(FoodInventory.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_expiring_soon(
        self,
        user_id: int,
        household_id: Optional[int] = None,
        days: int = 3,
    ) -> List[FoodInventory]:
        """Get items expiring within specified days."""
        expiry_threshold = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")

        query = select(FoodInventory).options(
            selectinload(FoodInventory.product).selectinload(FoodProduct.food_category)
        )

        if household_id:
            query = query.filter(FoodInventory.household_id == household_id)
        else:
            query = query.filter(
                FoodInventory.user_id == user_id,
                FoodInventory.household_id.is_(None),
            )

        query = query.filter(
            FoodInventory.expiry_date.isnot(None),
            FoodInventory.expiry_date <= expiry_threshold,
            FoodInventory.status.in_(["available", "opened"]),
        ).order_by(FoodInventory.expiry_date.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, item: FoodInventory) -> FoodInventory:
        """Create a new inventory item."""
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update(self, item: FoodInventory) -> FoodInventory:
        """Update an inventory item."""
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, item: FoodInventory) -> None:
        """Delete an inventory item."""
        await self.db.delete(item)
        await self.db.commit()

    async def get_available_by_product(
        self,
        user_id: int,
        product_id: int,
        household_id: Optional[int] = None,
    ) -> List[FoodInventory]:
        """Get available inventory items for a product, sorted FIFO (expiry_date ASC, NULLs last)."""
        query = select(FoodInventory).options(
            selectinload(FoodInventory.product).selectinload(FoodProduct.food_category)
        ).filter(
            FoodInventory.product_id == product_id,
            FoodInventory.status.in_(["available", "opened"]),
        )

        if household_id:
            query = query.filter(FoodInventory.household_id == household_id)
        else:
            query = query.filter(
                FoodInventory.user_id == user_id,
                FoodInventory.household_id.is_(None),
            )

        query = query.order_by(FoodInventory.expiry_date.asc().nulls_last())
        result = await self.db.execute(query)
        return list(result.scalars().all())


class FoodExpiryReminderRepository:
    """Repository for expiry reminders."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pending_for_user(self, user_id: int) -> List[FoodExpiryReminder]:
        """Get pending reminders for a user."""
        result = await self.db.execute(
            select(FoodExpiryReminder)
            .options(
                selectinload(FoodExpiryReminder.inventory_item)
                .selectinload(FoodInventory.product)
            )
            .filter(
                FoodExpiryReminder.user_id == user_id,
                FoodExpiryReminder.status == "pending",
            )
            .order_by(FoodExpiryReminder.remind_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, reminder_id: int) -> Optional[FoodExpiryReminder]:
        """Get reminder by ID."""
        result = await self.db.execute(
            select(FoodExpiryReminder)
            .options(
                selectinload(FoodExpiryReminder.inventory_item)
                .selectinload(FoodInventory.product)
            )
            .filter(FoodExpiryReminder.id == reminder_id)
        )
        return result.scalar_one_or_none()

    async def get_by_inventory_item(self, inventory_item_id: int) -> List[FoodExpiryReminder]:
        """Get reminders for an inventory item."""
        result = await self.db.execute(
            select(FoodExpiryReminder)
            .filter(FoodExpiryReminder.inventory_item_id == inventory_item_id)
        )
        return list(result.scalars().all())

    async def create(self, reminder: FoodExpiryReminder) -> FoodExpiryReminder:
        """Create a new reminder."""
        self.db.add(reminder)
        await self.db.commit()
        await self.db.refresh(reminder)
        return reminder

    async def update_status(self, reminder_id: int, status: str) -> None:
        """Update reminder status."""
        result = await self.db.execute(
            select(FoodExpiryReminder).filter(FoodExpiryReminder.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()
        if reminder:
            reminder.status = status
            if status == "sent":
                reminder.sent_at = datetime.utcnow().isoformat()
            await self.db.commit()

    async def delete_by_inventory_item(self, inventory_item_id: int) -> None:
        """Delete all reminders for an inventory item."""
        result = await self.db.execute(
            select(FoodExpiryReminder)
            .filter(FoodExpiryReminder.inventory_item_id == inventory_item_id)
        )
        reminders = result.scalars().all()
        for reminder in reminders:
            await self.db.delete(reminder)
        await self.db.commit()


class FoodReminderSettingsRepository:
    """Repository for reminder settings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> Optional[FoodReminderSettings]:
        """Get settings for a user."""
        result = await self.db.execute(
            select(FoodReminderSettings)
            .filter(FoodReminderSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, settings: FoodReminderSettings) -> FoodReminderSettings:
        """Create new settings."""
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def update(self, settings: FoodReminderSettings) -> FoodReminderSettings:
        """Update settings."""
        await self.db.commit()
        await self.db.refresh(settings)
        return settings


class FoodConsumptionLogRepository:
    """Repository for consumption logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        meal_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FoodConsumptionLog]:
        """Get consumption logs for a user."""
        query = select(FoodConsumptionLog).options(
            selectinload(FoodConsumptionLog.product)
        ).filter(FoodConsumptionLog.user_id == user_id)

        if start_date:
            query = query.filter(FoodConsumptionLog.consumed_at >= start_date)

        if end_date:
            query = query.filter(FoodConsumptionLog.consumed_at <= end_date)

        if meal_type:
            query = query.filter(FoodConsumptionLog.meal_type == meal_type)

        query = query.order_by(FoodConsumptionLog.consumed_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, log_id: int) -> Optional[FoodConsumptionLog]:
        """Get a consumption log entry by ID."""
        result = await self.db.execute(
            select(FoodConsumptionLog)
            .options(selectinload(FoodConsumptionLog.product))
            .filter(FoodConsumptionLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def get_by_date(
        self,
        user_id: int,
        date_str: str,
    ) -> List[FoodConsumptionLog]:
        """Get consumption logs for a specific date (YYYY-MM-DD)."""
        query = select(FoodConsumptionLog).options(
            selectinload(FoodConsumptionLog.product)
        ).filter(
            FoodConsumptionLog.user_id == user_id,
            FoodConsumptionLog.consumed_at >= date_str,
            FoodConsumptionLog.consumed_at < date_str + "T99",
        ).order_by(FoodConsumptionLog.consumed_at.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, log: FoodConsumptionLog) -> FoodConsumptionLog:
        """Create a consumption log entry."""
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def delete(self, log: FoodConsumptionLog) -> None:
        """Delete a consumption log entry."""
        await self.db.delete(log)
        await self.db.commit()


class FoodDailyGoalRepository:
    """Repository for daily nutrition goals."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: int) -> Optional[FoodDailyGoal]:
        """Get daily goal for a user."""
        result = await self.db.execute(
            select(FoodDailyGoal).filter(FoodDailyGoal.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: int, data: dict) -> FoodDailyGoal:
        """Create or update daily goal for a user."""
        goal = await self.get_by_user(user_id)
        if not goal:
            goal = FoodDailyGoal(user_id=user_id)
            self.db.add(goal)

        for field, value in data.items():
            setattr(goal, field, value)

        await self.db.commit()
        await self.db.refresh(goal)
        return goal
