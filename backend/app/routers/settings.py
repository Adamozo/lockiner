from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import (
    APIProviderConfigCreate,
    APIProviderConfigResponse,
    APIProviderListResponse,
    SetActiveProviderRequest,
    NotificationScheduleUpdate,
    NotificationScheduleResponse,
    NotificationScheduleBulkUpdate,
    NotificationScheduleListResponse,
    CustomReminderCreate,
)
from ..services.user_api_keys import UserAPIKeyService
from ..services.notification_schedule import NotificationScheduleService
from ..integrations.ocr_provider import OCRProvider

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


def get_api_key_service(db: AsyncSession = Depends(get_db)) -> UserAPIKeyService:
    return UserAPIKeyService(db)


def get_schedule_service(db: AsyncSession = Depends(get_db)) -> NotificationScheduleService:
    return NotificationScheduleService(db)


async def get_user_active_ocr_provider(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> tuple[OCRProvider | None, str | None]:
    service = UserAPIKeyService(db)
    return await service.get_active_provider(current_user)


@router.post("/api-providers", status_code=status.HTTP_201_CREATED)
async def add_api_provider(
    config: APIProviderConfigCreate,
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
) -> APIProviderConfigResponse:
    try:
        provider_type = OCRProvider(config.provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in OCRProvider])}",
        )

    result = await service.add_api_key(
        user=current_user,
        provider=provider_type,
        api_key=config.api_key,
        set_active=config.is_active or False,
    )

    return result


@router.get("/api-providers", response_model=APIProviderListResponse)
async def list_api_providers(
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
):
    return await service.list_providers(current_user)


@router.post("/active-provider", status_code=status.HTTP_200_OK)
async def set_active_provider(
    request: SetActiveProviderRequest,
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
):
    try:
        provider_type = OCRProvider(request.provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in OCRProvider])}",
        )

    success = await service.set_active_provider(current_user, provider_type)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {request.provider} not configured. Add API key first.",
        )

    return {"message": f"Active provider set to {request.provider}"}


@router.delete("/api-providers/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_provider(
    provider: str,
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
):
    try:
        provider_type = OCRProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in OCRProvider])}",
        )

    deleted = await service.delete_provider(current_user, provider_type)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    return None


# ========================================================================
# Notification Schedule Endpoints
# ========================================================================

VALID_REMINDER_TYPES = {"workout", "weight", "receipt", "finance"}


def _is_valid_reminder_type(reminder_type: str) -> bool:
    """Check if a reminder type is valid (built-in or custom)."""
    return reminder_type in VALID_REMINDER_TYPES or reminder_type.startswith("custom_")


@router.get("/notification-schedules", response_model=NotificationScheduleListResponse)
async def get_notification_schedules(
    current_user: User = Depends(get_current_user),
    service: NotificationScheduleService = Depends(get_schedule_service),
):
    """Get all notification schedules for the current user (auto-creates defaults)."""
    schedules = await service.get_user_schedules(current_user.id)
    return NotificationScheduleListResponse(schedules=schedules)


@router.put("/notification-schedules", response_model=NotificationScheduleListResponse)
async def bulk_update_notification_schedules(
    data: NotificationScheduleBulkUpdate,
    current_user: User = Depends(get_current_user),
    service: NotificationScheduleService = Depends(get_schedule_service),
):
    """Bulk update all notification schedules."""
    for s in data.schedules:
        if not _is_valid_reminder_type(s.reminder_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reminder_type: {s.reminder_type}",
            )
    schedules = await service.bulk_update_schedules(current_user.id, data.schedules)
    return NotificationScheduleListResponse(schedules=schedules)


@router.put("/notification-schedules/{reminder_type}", response_model=NotificationScheduleResponse)
async def update_notification_schedule(
    reminder_type: str,
    data: NotificationScheduleUpdate,
    current_user: User = Depends(get_current_user),
    service: NotificationScheduleService = Depends(get_schedule_service),
):
    """Update a single notification schedule by reminder type."""
    if not _is_valid_reminder_type(reminder_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reminder_type: {reminder_type}",
        )
    schedule = await service.update_schedule(
        user_id=current_user.id,
        reminder_type=reminder_type,
        enabled=data.enabled,
        frequency=data.frequency,
        hour=data.hour,
        minute=data.minute,
        day_of_week=data.day_of_week,
        day_of_month=data.day_of_month,
    )
    return schedule


@router.post("/notification-schedules/custom", response_model=NotificationScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_reminder(
    data: CustomReminderCreate,
    current_user: User = Depends(get_current_user),
    service: NotificationScheduleService = Depends(get_schedule_service),
):
    """Create a new custom reminder."""
    schedule = await service.create_custom_reminder(
        user_id=current_user.id,
        custom_name=data.custom_name,
        custom_icon=data.custom_icon,
        custom_title=data.custom_title,
        custom_body=data.custom_body,
        enabled=data.enabled,
        frequency=data.frequency,
        hour=data.hour,
        minute=data.minute,
        day_of_week=data.day_of_week,
        day_of_month=data.day_of_month,
    )
    return schedule


@router.delete("/notification-schedules/{reminder_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_schedule(
    reminder_type: str,
    current_user: User = Depends(get_current_user),
    service: NotificationScheduleService = Depends(get_schedule_service),
):
    """Delete a custom reminder. Built-in reminders cannot be deleted."""
    if not reminder_type.startswith("custom_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Built-in reminders cannot be deleted",
        )
    deleted = await service.delete_custom_reminder(current_user.id, reminder_type)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom reminder not found",
        )
    return None
