"""Backup module schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class BackupScheduleUpdate(BaseModel):
    auto_backup_enabled: bool
    frequency: str = Field(..., pattern=r"^(daily|weekly|monthly)$")
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)


class BackupPasswordSet(BaseModel):
    password: str = Field(..., min_length=8)


class BackupSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    password_configured: bool
    auto_backup_enabled: bool
    frequency: str
    hour: int
    minute: int
    day_of_week: Optional[int]
    day_of_month: Optional[int]
    google_drive_connected: bool
    google_drive_folder_id: Optional[str]
    last_backup_at: Optional[str]
    last_backup_filename: Optional[str]
    last_backup_size_bytes: Optional[int]
    last_backup_error: Optional[str]
    created_at: str
    updated_at: Optional[str]

    @classmethod
    def from_orm_with_password_flag(cls, obj) -> "BackupSettingsResponse":
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            password_configured=bool(obj.encrypted_password),
            auto_backup_enabled=obj.auto_backup_enabled,
            frequency=obj.frequency,
            hour=obj.hour,
            minute=obj.minute,
            day_of_week=obj.day_of_week,
            day_of_month=obj.day_of_month,
            google_drive_connected=obj.google_drive_connected,
            google_drive_folder_id=obj.google_drive_folder_id,
            last_backup_at=obj.last_backup_at,
            last_backup_filename=obj.last_backup_filename,
            last_backup_size_bytes=obj.last_backup_size_bytes,
            last_backup_error=obj.last_backup_error,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class HouseholdBackupSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    household_id: int
    configured_by_user_id: Optional[int]
    password_configured: bool
    auto_backup_enabled: bool
    frequency: str
    hour: int
    minute: int
    day_of_week: Optional[int]
    day_of_month: Optional[int]
    google_drive_connected: bool
    google_drive_folder_id: Optional[str]
    last_backup_at: Optional[str]
    last_backup_filename: Optional[str]
    last_backup_size_bytes: Optional[int]
    last_backup_error: Optional[str]
    created_at: str
    updated_at: Optional[str]

    @classmethod
    def from_orm_with_password_flag(cls, obj) -> "HouseholdBackupSettingsResponse":
        return cls(
            id=obj.id,
            household_id=obj.household_id,
            configured_by_user_id=obj.configured_by_user_id,
            password_configured=bool(obj.encrypted_password),
            auto_backup_enabled=obj.auto_backup_enabled,
            frequency=obj.frequency,
            hour=obj.hour,
            minute=obj.minute,
            day_of_week=obj.day_of_week,
            day_of_month=obj.day_of_month,
            google_drive_connected=obj.google_drive_connected,
            google_drive_folder_id=obj.google_drive_folder_id,
            last_backup_at=obj.last_backup_at,
            last_backup_filename=obj.last_backup_filename,
            last_backup_size_bytes=obj.last_backup_size_bytes,
            last_backup_error=obj.last_backup_error,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
