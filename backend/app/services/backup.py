"""Backup service — orchestrates data export, encryption, and Google Drive upload."""

import logging
from datetime import datetime, timezone
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import UserAPIKey
from ..models.backup import BackupSettings, HouseholdBackupSettings
from ..models.base import utc_now
from ..repositories.backup import BackupSettingsRepository, HouseholdBackupSettingsRepository
from .backup_export import export_full_user_data, export_household_data, build_zip

logger = logging.getLogger(__name__)

_GOOGLE_DRIVE_PROVIDER = "google_drive"


# ---------------------------------------------------------------------------
# Encryption helpers
# ---------------------------------------------------------------------------

def _get_fernet() -> Fernet:
    settings = get_settings()
    env_key = settings.encryption_key
    if not env_key:
        if settings.environment == "production":
            raise RuntimeError("ENCRYPTION_KEY is required in production")
        logger.warning("ENCRYPTION_KEY not set. Using temporary key.")
        env_key = Fernet.generate_key().decode()
    return Fernet(env_key.encode())


def _encrypt(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def _decrypt(encrypted_value: str) -> str:
    try:
        return _get_fernet().decrypt(encrypted_value.encode()).decode()
    except InvalidToken:
        raise RuntimeError("Failed to decrypt value. ENCRYPTION_KEY may have changed.")


# ---------------------------------------------------------------------------
# Google Drive error classification
# ---------------------------------------------------------------------------

class DriveAuthRevokedError(Exception):
    """User revoked OAuth access to Google Drive."""


class DriveQuotaExceededError(Exception):
    """User's Google Drive is full."""


class DriveRateLimitError(Exception):
    """Google Drive API rate limit exceeded."""


class DriveFolderNotFoundError(Exception):
    """Target Google Drive folder was deleted or is no longer accessible."""


def _classify_drive_error(exc: Exception) -> Exception:
    """
    Inspect a googleapiclient/google-auth exception and re-raise as a
    domain-specific error class when possible.
    """
    try:
        from googleapiclient.errors import HttpError
        if isinstance(exc, HttpError):
            status = exc.resp.status
            reason = ""
            try:
                import json as _json
                detail = _json.loads(exc.content.decode())
                errors = detail.get("error", {}).get("errors", [])
                reason = errors[0].get("reason", "") if errors else ""
            except Exception:
                pass

            if status == 401:
                return DriveAuthRevokedError(
                    "Google Drive access was revoked. Please reconnect your account."
                )
            if status == 403:
                if reason in ("storageQuotaExceeded", "teamDriveFileLimitExceeded"):
                    return DriveQuotaExceededError(
                        "Your Google Drive is full. Free up space and try again."
                    )
                if reason in ("rateLimitExceeded", "userRateLimitExceeded"):
                    return DriveRateLimitError(
                        "Google Drive rate limit exceeded. Will retry automatically next cycle."
                    )
                # Other 403 (e.g. insufficientPermissions after folder share revoked)
                return DriveAuthRevokedError(
                    "Google Drive access denied. Please reconnect your account."
                )
            if status == 404:
                return DriveFolderNotFoundError(
                    "Target Google Drive folder was not found. It may have been deleted."
                )
    except ImportError:
        pass

    # Check google-auth token refresh errors
    exc_name = type(exc).__name__
    exc_str = str(exc).lower()
    if "invalid_grant" in exc_str or "token has been expired or revoked" in exc_str:
        return DriveAuthRevokedError(
            "Google Drive access was revoked. Please reconnect your account."
        )

    return exc  # return original if unclassified


# ---------------------------------------------------------------------------
# Notification helper
# ---------------------------------------------------------------------------

async def _notify_user(db: AsyncSession, user_id: int, title: str, body: str) -> None:
    """Create an in-app notification for the user."""
    try:
        from ..repositories.notification import NotificationRepository
        repo = NotificationRepository(db)
        notification = await repo.create_notification(
            title=title,
            body=body,
            notification_type="alert",
            created_by_user_id=None,
        )
        await repo.create_user_notifications(notification.id, [user_id])
    except Exception as e:
        logger.error(f"Failed to send backup failure notification to user {user_id}: {e}")


# ---------------------------------------------------------------------------
# User backup service
# ---------------------------------------------------------------------------

class BackupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._repo = BackupSettingsRepository(db)

    async def get_settings(self, user_id: int) -> BackupSettings:
        return await self._repo.get_or_create(user_id)

    async def get_decrypted_password(self, user_id: int) -> Optional[str]:
        settings = await self._repo.get_by_user_id(user_id)
        if not settings or not settings.encrypted_password:
            return None
        return _decrypt(settings.encrypted_password)

    async def set_password(self, user_id: int, password: str) -> BackupSettings:
        settings = await self._repo.get_or_create(user_id)
        return await self._repo.update(
            settings, encrypted_password=_encrypt(password)
        )

    async def update_schedule(
        self,
        user_id: int,
        auto_backup_enabled: bool,
        frequency: str,
        hour: int,
        minute: int,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
    ) -> BackupSettings:
        settings = await self._repo.get_or_create(user_id)
        return await self._repo.update(
            settings,
            auto_backup_enabled=auto_backup_enabled,
            frequency=frequency,
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
        )

    async def generate_user_backup_zip(self, user_id: int) -> tuple[bytes, str]:
        password = await self.get_decrypted_password(user_id)
        if not password:
            raise ValueError("Backup password not configured")
        data = await export_full_user_data(self.db, user_id)
        zip_bytes = build_zip(data, password)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"lockiner_backup_{user_id}_{timestamp}.zip"
        return zip_bytes, filename

    async def store_google_drive_token(
        self, user_id: int, refresh_token: str, provider: str = _GOOGLE_DRIVE_PROVIDER
    ) -> None:
        encrypted = _encrypt(refresh_token)
        now = utc_now().isoformat()
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.encrypted_key = encrypted
            existing.updated_at = now
        else:
            self.db.add(UserAPIKey(
                user_id=user_id,
                provider=provider,
                encrypted_key=encrypted,
                is_active=True,
                created_at=now,
            ))
        settings = await self._repo.get_or_create(user_id)
        # Clear any previous error when reconnecting
        await self._repo.update(
            settings,
            google_drive_connected=True,
            last_backup_error=None,
        )
        await self.db.commit()

    async def disconnect_google_drive(
        self, user_id: int, provider: str = _GOOGLE_DRIVE_PROVIDER
    ) -> None:
        await self.db.execute(
            delete(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
            )
        )
        settings = await self._repo.get_by_user_id(user_id)
        if settings:
            await self._repo.update(settings, google_drive_connected=False)
        await self.db.commit()

    async def _get_drive_service(self, user_id: int, provider: str = _GOOGLE_DRIVE_PROVIDER):
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
            )
        )
        key_row = result.scalar_one_or_none()
        if not key_row:
            raise ValueError("Google Drive not connected")
        refresh_token = _decrypt(key_row.encrypted_key)

        cfg = get_settings()
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cfg.google_client_id,
            client_secret=cfg.google_client_secret,
            scopes=["https://www.googleapis.com/auth/drive.file"],
        )
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    async def upload_to_google_drive(
        self,
        user_id: int,
        zip_bytes: bytes,
        filename: str,
        provider: str = _GOOGLE_DRIVE_PROVIDER,
    ) -> str:
        import io as _io
        from googleapiclient.http import MediaIoBaseUpload

        try:
            service = await self._get_drive_service(user_id, provider)
            settings = await self._repo.get_or_create(user_id)

            file_metadata: dict = {"name": filename}
            if settings.google_drive_folder_id:
                file_metadata["parents"] = [settings.google_drive_folder_id]

            media = MediaIoBaseUpload(
                _io.BytesIO(zip_bytes),
                mimetype="application/zip",
                resumable=False,
            )
            uploaded = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id",
            ).execute()
            return uploaded.get("id", "")

        except Exception as raw_exc:
            classified = _classify_drive_error(raw_exc)
            raise classified from raw_exc

    async def run_user_auto_backup(self, user_id: int, settings: BackupSettings) -> None:
        try:
            zip_bytes, filename = await self.generate_user_backup_zip(user_id)
        except Exception as e:
            error_msg = f"Failed to generate backup: {e}"
            logger.error(f"Auto-backup generation failed for user {user_id}: {e}", exc_info=True)
            await self._repo.update(settings, last_backup_error=error_msg)
            await _notify_user(
                self.db, user_id,
                title="Backup Failed",
                body=f"Could not generate your backup. {e}",
            )
            return

        # Drive upload (if connected)
        if settings.google_drive_connected:
            try:
                await self.upload_to_google_drive(user_id, zip_bytes, filename)

            except DriveAuthRevokedError as e:
                logger.warning(f"Drive auth revoked for user {user_id}, disconnecting")
                await self.disconnect_google_drive(user_id)
                await self._repo.update(settings, last_backup_error=str(e))
                await _notify_user(
                    self.db, user_id,
                    title="Google Drive Disconnected",
                    body=str(e),
                )
                return

            except DriveFolderNotFoundError as e:
                logger.warning(f"Drive folder not found for user {user_id}, clearing folder_id")
                await self._repo.update(
                    settings,
                    google_drive_folder_id=None,
                    last_backup_error=str(e),
                )
                await _notify_user(
                    self.db, user_id,
                    title="Backup Folder Missing",
                    body=str(e),
                )
                return

            except DriveQuotaExceededError as e:
                logger.warning(f"Drive quota exceeded for user {user_id}")
                await self._repo.update(settings, last_backup_error=str(e))
                await _notify_user(
                    self.db, user_id,
                    title="Google Drive Full",
                    body=str(e),
                )
                return

            except DriveRateLimitError as e:
                # Don't mark as hard failure — will retry next scheduled cycle
                logger.warning(f"Drive rate limit for user {user_id}: {e}")
                await self._repo.update(settings, last_backup_error=str(e))
                return

            except Exception as e:
                error_msg = f"Unexpected Drive error: {e}"
                logger.error(f"Drive upload failed for user {user_id}: {e}", exc_info=True)
                await self._repo.update(settings, last_backup_error=error_msg)
                await _notify_user(
                    self.db, user_id,
                    title="Backup Upload Failed",
                    body=f"Could not upload backup to Google Drive. {e}",
                )
                return

        # Success
        await self._repo.update(
            settings,
            last_backup_at=utc_now().isoformat(),
            last_backup_filename=filename,
            last_backup_size_bytes=len(zip_bytes),
            last_backup_error=None,  # clear any previous error
        )
        logger.info(f"Auto-backup completed for user {user_id}: {filename}")


# ---------------------------------------------------------------------------
# Household backup service
# ---------------------------------------------------------------------------

class HouseholdBackupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._repo = HouseholdBackupSettingsRepository(db)

    def _drive_provider(self, household_id: int) -> str:
        return f"google_drive_hh_{household_id}"

    async def _assert_manager(self, user_id: int, household_id: int) -> None:
        from ..models import HouseholdMember
        result = await self.db.execute(
            select(HouseholdMember).where(
                HouseholdMember.user_id == user_id,
                HouseholdMember.household_id == household_id,
                HouseholdMember.role == "manager",
                HouseholdMember.status == "active",
            )
        )
        if not result.scalar_one_or_none():
            raise PermissionError("Only household managers can manage household backups")

    async def get_settings(self, household_id: int, user_id: int) -> HouseholdBackupSettings:
        await self._assert_manager(user_id, household_id)
        return await self._repo.get_or_create(household_id, user_id)

    async def get_decrypted_password(self, household_id: int, user_id: int) -> Optional[str]:
        await self._assert_manager(user_id, household_id)
        settings = await self._repo.get_by_household_id(household_id)
        if not settings or not settings.encrypted_password:
            return None
        return _decrypt(settings.encrypted_password)

    async def set_password(
        self, household_id: int, user_id: int, password: str
    ) -> HouseholdBackupSettings:
        await self._assert_manager(user_id, household_id)
        settings = await self._repo.get_or_create(household_id, user_id)
        return await self._repo.update(
            settings, encrypted_password=_encrypt(password)
        )

    async def update_schedule(
        self,
        household_id: int,
        user_id: int,
        auto_backup_enabled: bool,
        frequency: str,
        hour: int,
        minute: int,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
    ) -> HouseholdBackupSettings:
        await self._assert_manager(user_id, household_id)
        settings = await self._repo.get_or_create(household_id, user_id)
        return await self._repo.update(
            settings,
            configured_by_user_id=user_id,
            auto_backup_enabled=auto_backup_enabled,
            frequency=frequency,
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
        )

    async def generate_household_backup_zip(
        self, household_id: int, user_id: int
    ) -> tuple[bytes, str]:
        await self._assert_manager(user_id, household_id)
        settings = await self._repo.get_by_household_id(household_id)
        if not settings or not settings.encrypted_password:
            raise ValueError("Backup password not configured for this household")
        password = _decrypt(settings.encrypted_password)
        data = await export_household_data(self.db, household_id)
        zip_bytes = build_zip(data, password)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"lockiner_household_{household_id}_{timestamp}.zip"
        return zip_bytes, filename

    async def store_google_drive_token(
        self, household_id: int, user_id: int, refresh_token: str
    ) -> None:
        await self._assert_manager(user_id, household_id)
        provider = self._drive_provider(household_id)
        encrypted = _encrypt(refresh_token)
        now = utc_now().isoformat()
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.encrypted_key = encrypted
            existing.updated_at = now
        else:
            self.db.add(UserAPIKey(
                user_id=user_id,
                provider=provider,
                encrypted_key=encrypted,
                is_active=True,
                created_at=now,
            ))
        settings = await self._repo.get_or_create(household_id, user_id)
        await self._repo.update(
            settings,
            google_drive_connected=True,
            configured_by_user_id=user_id,
            last_backup_error=None,
        )
        await self.db.commit()

    async def disconnect_google_drive(self, household_id: int, user_id: int) -> None:
        await self._assert_manager(user_id, household_id)
        provider = self._drive_provider(household_id)
        await self.db.execute(
            delete(UserAPIKey).where(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
            )
        )
        settings = await self._repo.get_by_household_id(household_id)
        if settings:
            await self._repo.update(settings, google_drive_connected=False)
        await self.db.commit()

    async def _get_drive_service(self, household_id: int, configured_by_user_id: int):
        provider = self._drive_provider(household_id)
        result = await self.db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == configured_by_user_id,
                UserAPIKey.provider == provider,
            )
        )
        key_row = result.scalar_one_or_none()
        if not key_row:
            raise ValueError("Google Drive not connected for this household")
        refresh_token = _decrypt(key_row.encrypted_key)

        cfg = get_settings()
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cfg.google_client_id,
            client_secret=cfg.google_client_secret,
            scopes=["https://www.googleapis.com/auth/drive.file"],
        )
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    async def run_household_auto_backup(
        self, household_id: int, settings: HouseholdBackupSettings
    ) -> None:
        if not settings.configured_by_user_id:
            logger.warning(f"Household {household_id}: no configured_by_user_id, skipping")
            return
        user_id = settings.configured_by_user_id

        if not settings.encrypted_password:
            logger.warning(f"Household {household_id}: no backup password, skipping")
            return

        try:
            password = _decrypt(settings.encrypted_password)
            data = await export_household_data(self.db, household_id)
            zip_bytes = build_zip(data, password)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"lockiner_household_{household_id}_{timestamp}.zip"
        except Exception as e:
            error_msg = f"Failed to generate backup: {e}"
            logger.error(f"Household {household_id} backup generation failed: {e}", exc_info=True)
            await self._repo.update(settings, last_backup_error=error_msg)
            await _notify_user(
                self.db, user_id,
                title="Household Backup Failed",
                body=f"Could not generate backup for your household. {e}",
            )
            return

        if settings.google_drive_connected:
            try:
                import io as _io
                from googleapiclient.http import MediaIoBaseUpload

                service = await self._get_drive_service(household_id, user_id)
                file_metadata: dict = {"name": filename}
                if settings.google_drive_folder_id:
                    file_metadata["parents"] = [settings.google_drive_folder_id]
                media = MediaIoBaseUpload(
                    _io.BytesIO(zip_bytes),
                    mimetype="application/zip",
                    resumable=False,
                )
                service.files().create(
                    body=file_metadata, media_body=media, fields="id"
                ).execute()

            except Exception as raw_exc:
                classified = _classify_drive_error(raw_exc)

                if isinstance(classified, DriveAuthRevokedError):
                    logger.warning(f"Drive auth revoked for household {household_id}")
                    await self.disconnect_google_drive(household_id, user_id)
                    await self._repo.update(settings, last_backup_error=str(classified))
                    await _notify_user(
                        self.db, user_id,
                        title="Household Drive Disconnected",
                        body=str(classified),
                    )
                elif isinstance(classified, DriveFolderNotFoundError):
                    logger.warning(f"Drive folder missing for household {household_id}")
                    await self._repo.update(
                        settings,
                        google_drive_folder_id=None,
                        last_backup_error=str(classified),
                    )
                    await _notify_user(
                        self.db, user_id,
                        title="Backup Folder Missing",
                        body=str(classified),
                    )
                elif isinstance(classified, DriveQuotaExceededError):
                    await self._repo.update(settings, last_backup_error=str(classified))
                    await _notify_user(
                        self.db, user_id,
                        title="Google Drive Full",
                        body=str(classified),
                    )
                elif isinstance(classified, DriveRateLimitError):
                    await self._repo.update(settings, last_backup_error=str(classified))
                    logger.warning(f"Rate limit for household {household_id}: {classified}")
                else:
                    error_msg = f"Unexpected Drive error: {raw_exc}"
                    await self._repo.update(settings, last_backup_error=error_msg)
                    await _notify_user(
                        self.db, user_id,
                        title="Household Backup Upload Failed",
                        body=f"Could not upload household backup to Google Drive. {raw_exc}",
                    )
                return

        # Success
        await self._repo.update(
            settings,
            last_backup_at=utc_now().isoformat(),
            last_backup_filename=filename,
            last_backup_size_bytes=len(zip_bytes),
            last_backup_error=None,
        )
        logger.info(f"Auto-backup completed for household {household_id}: {filename}")
