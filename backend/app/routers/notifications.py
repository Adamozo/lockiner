"""Notifications router - user notification management + push subscription."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..dependencies import get_current_user, require_admin
from ..models import User
from ..schemas.notification import (
    NotificationItemResponse,
    UnreadCountResponse,
    SendNotificationRequest,
    SendNotificationResponse,
    PushSubscribeRequest,
)
from ..services.notification import NotificationService
from ..config import get_settings

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


async def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


# ============================================================================
# Push Subscription
# ============================================================================

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_push(
    data: PushSubscribeRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Save Web Push subscription for the current user."""
    await service.subscribe_push(current_user.id, data.endpoint, data.p256dh, data.auth)
    return {"status": "subscribed"}


@router.delete("/subscribe")
async def unsubscribe_push(
    data: PushSubscribeRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Remove Web Push subscription."""
    deleted = await service.unsubscribe_push(current_user.id, data.endpoint)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return {"status": "unsubscribed"}


# ============================================================================
# VAPID Public Key (needed by frontend to subscribe)
# ============================================================================

@router.get("/vapid-public-key")
async def get_vapid_public_key(
    current_user: User = Depends(get_current_user),
):
    """Get the VAPID public key for push subscription."""
    settings = get_settings()
    return {"public_key": settings.vapid_public_key}


# ============================================================================
# User Notifications
# ============================================================================

@router.get("", response_model=List[NotificationItemResponse])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Get current user's notifications."""
    return await service.get_user_notifications(current_user.id, skip, limit)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Get count of unread notifications."""
    count = await service.get_unread_count(current_user.id)
    return UnreadCountResponse(count=count)


@router.put("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark all notifications as read."""
    count = await service.mark_all_as_read(current_user.id)
    return {"marked_count": count}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a notification as read."""
    result = await service.mark_as_read(current_user.id, notification_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"status": "read"}


@router.put("/{notification_id}/unread")
async def mark_as_unread(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a notification as unread."""
    result = await service.mark_as_unread(current_user.id, notification_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"status": "unread"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Delete a notification (removes junction only, not the notification itself)."""
    deleted = await service.delete_user_notification(current_user.id, notification_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"status": "deleted"}


# ============================================================================
# Admin: Send Notification
# ============================================================================

@router.post("/send", response_model=SendNotificationResponse)
async def send_notification(
    data: SendNotificationRequest,
    admin: User = Depends(require_admin),
    service: NotificationService = Depends(get_notification_service),
):
    """Admin: Send notification to users (with optional push)."""
    if data.target == "selected" and not data.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_ids required when target is 'selected'",
        )

    result = await service.send_notification(
        title=data.title,
        body=data.body,
        notification_type=data.notification_type,
        target=data.target,
        user_ids=data.user_ids,
        created_by_user_id=admin.id,
    )
    return SendNotificationResponse(**result)
