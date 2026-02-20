"""Backup & Data Export router."""

import base64
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.backup import (
    BackupScheduleUpdate,
    BackupPasswordSet,
    BackupSettingsResponse,
    HouseholdBackupSettingsResponse,
)
from ..services.backup import BackupService, HouseholdBackupService
from ..config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/backup", tags=["backup"])


def _get_backup_service(db: AsyncSession = Depends(get_db)) -> BackupService:
    return BackupService(db)


def _get_household_backup_service(db: AsyncSession = Depends(get_db)) -> HouseholdBackupService:
    return HouseholdBackupService(db)


# =============================================================================
# User backup endpoints
# =============================================================================

@router.get("/settings", response_model=BackupSettingsResponse)
async def get_user_backup_settings(
    current_user: User = Depends(get_current_user),
    service: BackupService = Depends(_get_backup_service),
) -> BackupSettingsResponse:
    settings = await service.get_settings(current_user.id)
    return BackupSettingsResponse.from_orm_with_password_flag(settings)


@router.put("/settings/schedule", response_model=BackupSettingsResponse)
async def update_user_backup_schedule(
    data: BackupScheduleUpdate,
    current_user: User = Depends(get_current_user),
    service: BackupService = Depends(_get_backup_service),
) -> BackupSettingsResponse:
    settings = await service.update_schedule(
        user_id=current_user.id,
        auto_backup_enabled=data.auto_backup_enabled,
        frequency=data.frequency,
        hour=data.hour,
        minute=data.minute,
        day_of_week=data.day_of_week,
        day_of_month=data.day_of_month,
    )
    return BackupSettingsResponse.from_orm_with_password_flag(settings)


@router.get("/password")
async def get_user_backup_password(
    current_user: User = Depends(get_current_user),
    service: BackupService = Depends(_get_backup_service),
):
    password = await service.get_decrypted_password(current_user.id)
    return {"password": password, "configured": password is not None}


@router.put("/password")
async def set_user_backup_password(
    data: BackupPasswordSet,
    current_user: User = Depends(get_current_user),
    service: BackupService = Depends(_get_backup_service),
):
    await service.set_password(current_user.id, data.password)
    return {"message": "Password updated"}


@router.get("/download")
async def download_user_backup(
    current_user: User = Depends(get_current_user),
    service: BackupService = Depends(_get_backup_service),
):
    try:
        zip_bytes, filename = await service.generate_user_backup_zip(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    import io
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/google-drive/auth-url")
async def get_google_drive_auth_url(
    current_user: User = Depends(get_current_user),
):
    cfg = get_settings()
    if not cfg.google_client_id or not cfg.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Drive integration not configured",
        )
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/drive.file"],
        redirect_uri=cfg.google_redirect_uri,
    )
    state_data = json.dumps({"user_id": current_user.id, "type": "user"})
    state = base64.b64encode(state_data.encode()).decode()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        state=state,
    )
    return {"auth_url": auth_url}


@router.get("/google-drive/callback")
async def google_drive_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    frontend_base = get_settings().frontend_url
    if error:
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

    try:
        state_data = json.loads(base64.b64decode(state or "e30=").decode())
    except Exception:
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

    backup_type = state_data.get("type", "user")

    cfg = get_settings()
    if not cfg.google_client_id or not cfg.google_client_secret:
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

    from google_auth_oauthlib.flow import Flow

    redirect_uri = cfg.google_redirect_uri
    if backup_type == "household":
        redirect_uri = redirect_uri.replace("/callback", "/household-callback")

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/drive.file"],
        redirect_uri=redirect_uri,
    )
    try:
        flow.fetch_token(code=code)
        refresh_token = flow.credentials.refresh_token
        if not refresh_token:
            return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

        service = BackupService(db)
        user_id = state_data["user_id"]
        await service.store_google_drive_token(user_id, refresh_token)
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_connected=1")
    except Exception as e:
        logger.error(f"Google Drive callback error: {e}", exc_info=True)
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")


@router.delete("/google-drive/disconnect", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_google_drive(
    current_user: User = Depends(get_current_user),
    service: BackupService = Depends(_get_backup_service),
):
    await service.disconnect_google_drive(current_user.id)
    return None


# =============================================================================
# Household backup endpoints (manager-only)
# =============================================================================

@router.get("/household/{household_id}/settings", response_model=HouseholdBackupSettingsResponse)
async def get_household_backup_settings(
    household_id: int,
    current_user: User = Depends(get_current_user),
    service: HouseholdBackupService = Depends(_get_household_backup_service),
) -> HouseholdBackupSettingsResponse:
    try:
        settings = await service.get_settings(household_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return HouseholdBackupSettingsResponse.from_orm_with_password_flag(settings)


@router.put("/household/{household_id}/settings/schedule", response_model=HouseholdBackupSettingsResponse)
async def update_household_backup_schedule(
    household_id: int,
    data: BackupScheduleUpdate,
    current_user: User = Depends(get_current_user),
    service: HouseholdBackupService = Depends(_get_household_backup_service),
) -> HouseholdBackupSettingsResponse:
    try:
        settings = await service.update_schedule(
            household_id=household_id,
            user_id=current_user.id,
            auto_backup_enabled=data.auto_backup_enabled,
            frequency=data.frequency,
            hour=data.hour,
            minute=data.minute,
            day_of_week=data.day_of_week,
            day_of_month=data.day_of_month,
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return HouseholdBackupSettingsResponse.from_orm_with_password_flag(settings)


@router.get("/household/{household_id}/password")
async def get_household_backup_password(
    household_id: int,
    current_user: User = Depends(get_current_user),
    service: HouseholdBackupService = Depends(_get_household_backup_service),
):
    try:
        password = await service.get_decrypted_password(household_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return {"password": password, "configured": password is not None}


@router.put("/household/{household_id}/password")
async def set_household_backup_password(
    household_id: int,
    data: BackupPasswordSet,
    current_user: User = Depends(get_current_user),
    service: HouseholdBackupService = Depends(_get_household_backup_service),
):
    try:
        await service.set_password(household_id, current_user.id, data.password)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return {"message": "Password updated"}


@router.get("/household/{household_id}/download")
async def download_household_backup(
    household_id: int,
    current_user: User = Depends(get_current_user),
    service: HouseholdBackupService = Depends(_get_household_backup_service),
):
    try:
        zip_bytes, filename = await service.generate_household_backup_zip(
            household_id, current_user.id
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    import io
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/household/{household_id}/google-drive/auth-url")
async def get_household_google_drive_auth_url(
    household_id: int,
    current_user: User = Depends(get_current_user),
    service: HouseholdBackupService = Depends(_get_household_backup_service),
):
    # Verify manager access (service will check via get_settings which calls _assert_manager)
    try:
        await service.get_settings(household_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    cfg = get_settings()
    if not cfg.google_client_id or not cfg.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Drive integration not configured",
        )
    from google_auth_oauthlib.flow import Flow

    redirect_uri = cfg.google_redirect_uri.replace("/callback", "/household-callback")
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/drive.file"],
        redirect_uri=redirect_uri,
    )
    state_data = json.dumps({
        "user_id": current_user.id,
        "household_id": household_id,
        "type": "household",
    })
    state = base64.b64encode(state_data.encode()).decode()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        state=state,
    )
    return {"auth_url": auth_url}


@router.get("/google-drive/household-callback")
async def google_drive_household_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    frontend_base = get_settings().frontend_url
    if error:
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

    try:
        state_data = json.loads(base64.b64decode(state or "e30=").decode())
    except Exception:
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

    cfg = get_settings()
    if not cfg.google_client_id or not cfg.google_client_secret:
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

    from google_auth_oauthlib.flow import Flow

    redirect_uri = cfg.google_redirect_uri.replace("/callback", "/household-callback")
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/drive.file"],
        redirect_uri=redirect_uri,
    )
    try:
        flow.fetch_token(code=code)
        refresh_token = flow.credentials.refresh_token
        if not refresh_token:
            return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")

        household_id = state_data["household_id"]
        user_id = state_data["user_id"]
        service = HouseholdBackupService(db)
        await service.store_google_drive_token(household_id, user_id, refresh_token)
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_connected=1")
    except Exception as e:
        logger.error(f"Google Drive household callback error: {e}", exc_info=True)
        return RedirectResponse(url=f"{frontend_base}/settings?backup_drive_error=1")


@router.delete("/household/{household_id}/google-drive/disconnect", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_household_google_drive(
    household_id: int,
    current_user: User = Depends(get_current_user),
    service: HouseholdBackupService = Depends(_get_household_backup_service),
):
    try:
        await service.disconnect_google_drive(household_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return None
