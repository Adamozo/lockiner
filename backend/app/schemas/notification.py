"""Notification schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal


class NotificationItemResponse(BaseModel):
    """User's notification item (from user_notifications JOIN notifications)."""
    id: int  # user_notification.id
    notification_id: int
    title: str
    body: str
    notification_type: str
    status: str  # unread | read
    read_at: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class UnreadCountResponse(BaseModel):
    """Unread notification count."""
    count: int


class SendNotificationRequest(BaseModel):
    """Admin request to send a notification."""
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    notification_type: str = "general"
    target: Literal["all", "selected"]
    user_ids: List[int] = []  # required when target="selected"


class SendNotificationResponse(BaseModel):
    """Response after sending a notification."""
    notification_id: int
    recipients_count: int
    push_sent: int
    push_failed: int


class PushSubscribeRequest(BaseModel):
    """Web Push subscription data from the browser."""
    endpoint: str
    p256dh: str
    auth: str


class PushSubscriptionResponse(BaseModel):
    """Push subscription info returned to the user."""
    id: int
    endpoint: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)
