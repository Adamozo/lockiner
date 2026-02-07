"""Notification repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Optional

from ..models.notification import Notification, UserNotification, PushSubscription
from ..models.base import utc_now


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # Notification CRUD
    # ========================================================================

    async def create_notification(
        self, title: str, body: str, notification_type: str, created_by_user_id: Optional[int] = None
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            title=title,
            body=body,
            notification_type=notification_type,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def create_user_notifications(self, notification_id: int, user_ids: List[int]) -> int:
        """Bulk create user_notifications for a list of user IDs. Returns count."""
        for user_id in user_ids:
            un = UserNotification(
                user_id=user_id,
                notification_id=notification_id,
            )
            self.db.add(un)
        await self.db.commit()
        return len(user_ids)

    # ========================================================================
    # User Notification Queries
    # ========================================================================

    async def get_user_notifications(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> List[dict]:
        """Get user's notifications (joined with notification details)."""
        stmt = (
            select(
                UserNotification.id,
                UserNotification.notification_id,
                Notification.title,
                Notification.body,
                Notification.notification_type,
                UserNotification.status,
                UserNotification.read_at,
                UserNotification.created_at,
            )
            .join(Notification, UserNotification.notification_id == Notification.id)
            .filter(UserNotification.user_id == user_id)
            .order_by(UserNotification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "id": row.id,
                "notification_id": row.notification_id,
                "title": row.title,
                "body": row.body,
                "notification_type": row.notification_type,
                "status": row.status,
                "read_at": row.read_at,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        result = await self.db.execute(
            select(func.count(UserNotification.id))
            .filter(
                UserNotification.user_id == user_id,
                UserNotification.status == "unread",
            )
        )
        return result.scalar() or 0

    async def get_user_notification(self, user_id: int, notification_id: int) -> Optional[UserNotification]:
        """Get a specific user notification by its ID."""
        result = await self.db.execute(
            select(UserNotification).filter(
                UserNotification.id == notification_id,
                UserNotification.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def mark_as_read(self, user_id: int, notification_id: int) -> Optional[UserNotification]:
        """Mark a user notification as read."""
        un = await self.get_user_notification(user_id, notification_id)
        if un is None:
            return None
        un.status = "read"
        un.read_at = utc_now().isoformat()
        await self.db.commit()
        await self.db.refresh(un)
        return un

    async def mark_as_unread(self, user_id: int, notification_id: int) -> Optional[UserNotification]:
        """Mark a user notification as unread."""
        un = await self.get_user_notification(user_id, notification_id)
        if un is None:
            return None
        un.status = "unread"
        un.read_at = None
        await self.db.commit()
        await self.db.refresh(un)
        return un

    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all user notifications as read. Returns count updated."""
        result = await self.db.execute(
            select(UserNotification).filter(
                UserNotification.user_id == user_id,
                UserNotification.status == "unread",
            )
        )
        notifications = list(result.scalars().all())
        now = utc_now().isoformat()
        for un in notifications:
            un.status = "read"
            un.read_at = now
        await self.db.commit()
        return len(notifications)

    async def delete_user_notification(self, user_id: int, notification_id: int) -> bool:
        """Delete a user notification junction (not the notification itself)."""
        result = await self.db.execute(
            delete(UserNotification).filter(
                UserNotification.id == notification_id,
                UserNotification.user_id == user_id,
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    # ========================================================================
    # Push Subscription
    # ========================================================================

    async def get_push_subscriptions(self, user_ids: List[int]) -> List[PushSubscription]:
        """Get push subscriptions for given users."""
        result = await self.db.execute(
            select(PushSubscription).filter(PushSubscription.user_id.in_(user_ids))
        )
        return list(result.scalars().all())

    async def save_push_subscription(
        self, user_id: int, endpoint: str, p256dh: str, auth: str
    ) -> PushSubscription:
        """Save or update a push subscription."""
        # Check if this endpoint already exists for this user
        result = await self.db.execute(
            select(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == endpoint,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.p256dh_key = p256dh
            existing.auth_key = auth
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        sub = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh,
            auth_key=auth,
        )
        self.db.add(sub)
        await self.db.commit()
        await self.db.refresh(sub)
        return sub

    async def delete_push_subscription(self, user_id: int, endpoint: str) -> bool:
        """Delete a push subscription."""
        result = await self.db.execute(
            delete(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == endpoint,
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def delete_push_subscription_by_endpoint(self, endpoint: str) -> None:
        """Delete a stale push subscription by endpoint."""
        await self.db.execute(
            delete(PushSubscription).filter(PushSubscription.endpoint == endpoint)
        )
        await self.db.commit()
