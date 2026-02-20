"""Repository for backup settings database operations."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.backup import BackupSettings, HouseholdBackupSettings
from ..models.base import utc_now


class BackupSettingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> Optional[BackupSettings]:
        result = await self.db.execute(
            select(BackupSettings).where(BackupSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: int) -> BackupSettings:
        existing = await self.get_by_user_id(user_id)
        if existing:
            return existing
        settings = BackupSettings(
            user_id=user_id,
            created_at=utc_now().isoformat(),
        )
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def update(self, settings: BackupSettings, **kwargs) -> BackupSettings:
        for key, value in kwargs.items():
            setattr(settings, key, value)
        settings.updated_at = utc_now().isoformat()
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def get_all_enabled_auto_backup(self) -> list[BackupSettings]:
        result = await self.db.execute(
            select(BackupSettings).where(BackupSettings.auto_backup_enabled == True)
        )
        return list(result.scalars().all())


class HouseholdBackupSettingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_household_id(self, household_id: int) -> Optional[HouseholdBackupSettings]:
        result = await self.db.execute(
            select(HouseholdBackupSettings).where(
                HouseholdBackupSettings.household_id == household_id
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self, household_id: int, configured_by_user_id: int
    ) -> HouseholdBackupSettings:
        existing = await self.get_by_household_id(household_id)
        if existing:
            return existing
        settings = HouseholdBackupSettings(
            household_id=household_id,
            configured_by_user_id=configured_by_user_id,
            created_at=utc_now().isoformat(),
        )
        self.db.add(settings)
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def update(self, settings: HouseholdBackupSettings, **kwargs) -> HouseholdBackupSettings:
        for key, value in kwargs.items():
            setattr(settings, key, value)
        settings.updated_at = utc_now().isoformat()
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def get_all_enabled_auto_backup(self) -> list[HouseholdBackupSettings]:
        result = await self.db.execute(
            select(HouseholdBackupSettings).where(
                HouseholdBackupSettings.auto_backup_enabled == True
            )
        )
        return list(result.scalars().all())
