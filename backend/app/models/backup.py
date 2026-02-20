"""Backup settings models for user and household backups."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class BackupSettings(Base):
    """Per-user backup configuration."""
    __tablename__ = "backup_settings"
    __table_args__ = (UniqueConstraint("user_id", name="uq_backup_settings_user"),)

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    user_id                = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    encrypted_password     = Column(Text, nullable=True)
    auto_backup_enabled    = Column(Boolean, nullable=False, default=False)
    frequency              = Column(String(20), nullable=False, default="weekly")  # daily|weekly|monthly
    hour                   = Column(Integer, nullable=False, default=3)
    minute                 = Column(Integer, nullable=False, default=0)
    day_of_week            = Column(Integer, nullable=True)
    day_of_month           = Column(Integer, nullable=True)
    google_drive_connected = Column(Boolean, nullable=False, default=False)
    google_drive_folder_id = Column(String, nullable=True)
    last_backup_at         = Column(String, nullable=True)
    last_backup_filename   = Column(String, nullable=True)
    last_backup_size_bytes = Column(Integer, nullable=True)
    last_backup_error      = Column(Text, nullable=True)
    created_at             = Column(String, nullable=False, default=lambda: utc_now().isoformat())
    updated_at             = Column(String, nullable=True)

    user = relationship("User")

    def __repr__(self):
        return f"<BackupSettings(id={self.id}, user_id={self.user_id})>"


class HouseholdBackupSettings(Base):
    """Per-household backup configuration (managed by household admin)."""
    __tablename__ = "household_backup_settings"
    __table_args__ = (UniqueConstraint("household_id", name="uq_household_backup_settings"),)

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    household_id           = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    configured_by_user_id  = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    encrypted_password     = Column(Text, nullable=True)
    auto_backup_enabled    = Column(Boolean, nullable=False, default=False)
    frequency              = Column(String(20), nullable=False, default="weekly")
    hour                   = Column(Integer, nullable=False, default=3)
    minute                 = Column(Integer, nullable=False, default=0)
    day_of_week            = Column(Integer, nullable=True)
    day_of_month           = Column(Integer, nullable=True)
    google_drive_connected = Column(Boolean, nullable=False, default=False)
    google_drive_folder_id = Column(String, nullable=True)
    last_backup_at         = Column(String, nullable=True)
    last_backup_filename   = Column(String, nullable=True)
    last_backup_size_bytes = Column(Integer, nullable=True)
    last_backup_error      = Column(Text, nullable=True)
    created_at             = Column(String, nullable=False, default=lambda: utc_now().isoformat())
    updated_at             = Column(String, nullable=True)

    household    = relationship("Household")
    configured_by = relationship("User")

    def __repr__(self):
        return f"<HouseholdBackupSettings(id={self.id}, household_id={self.household_id})>"
