"""Notification service - handles CRUD and Web Push delivery."""

import json
import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.notification import NotificationRepository
from ..repositories.user import UserRepository
from ..config import get_settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)

    async def send_notification(
        self,
        title: str,
        body: str,
        notification_type: str,
        target: str,
        user_ids: List[int],
        created_by_user_id: Optional[int] = None,
    ) -> dict:
        """
        Create notification, assign to users, send web push.
        Returns stats dict.
        """
        # 1. Create the notification record
        notification = await self.repo.create_notification(
            title=title,
            body=body,
            notification_type=notification_type,
            created_by_user_id=created_by_user_id,
        )

        # 2. Determine target user IDs
        if target == "all":
            target_user_ids = await self.user_repo.get_all_active_ids()
        else:
            target_user_ids = user_ids

        # 3. Create user_notifications
        recipients_count = await self.repo.create_user_notifications(
            notification.id, target_user_ids
        )

        # 4. Send web push to all target users
        push_sent = 0
        push_failed = 0
        subscriptions = await self.repo.get_push_subscriptions(target_user_ids)

        # Log users without push subscriptions
        subscribed_user_ids = {sub.user_id for sub in subscriptions}
        skipped_user_ids = set(target_user_ids) - subscribed_user_ids
        if skipped_user_ids:
            logger.info(
                f"Users without push subscriptions (skipped for web push): {sorted(skipped_user_ids)}"
            )

        settings = get_settings()
        if settings.vapid_private_key and subscriptions:
            try:
                from pywebpush import webpush, WebPushException

                payload = json.dumps({"title": title, "body": body})

                for sub in subscriptions:
                    try:
                        webpush(
                            subscription_info={
                                "endpoint": sub.endpoint,
                                "keys": {
                                    "p256dh": sub.p256dh_key,
                                    "auth": sub.auth_key,
                                },
                            },
                            data=payload,
                            vapid_private_key=settings.vapid_private_key,
                            vapid_claims={
                                "sub": f"mailto:{settings.vapid_contact_email}",
                            },
                        )
                        push_sent += 1
                    except WebPushException as e:
                        push_failed += 1
                        # 410 Gone = subscription expired, clean up
                        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 410:
                            await self.repo.delete_push_subscription_by_endpoint(sub.endpoint)
                            logger.info(f"Removed stale push subscription: {sub.endpoint[:50]}")
                        else:
                            logger.warning(f"Push failed for {sub.endpoint[:50]}: {e}")
                    except Exception as e:
                        push_failed += 1
                        logger.warning(f"Push error: {e}")
            except ImportError:
                logger.warning("pywebpush not installed, skipping push notifications")

        return {
            "notification_id": notification.id,
            "recipients_count": recipients_count,
            "push_sent": push_sent,
            "push_failed": push_failed,
        }

    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 20) -> List[dict]:
        return await self.repo.get_user_notifications(user_id, skip, limit)

    async def get_unread_count(self, user_id: int) -> int:
        return await self.repo.get_unread_count(user_id)

    async def mark_as_read(self, user_id: int, notification_id: int):
        return await self.repo.mark_as_read(user_id, notification_id)

    async def mark_as_unread(self, user_id: int, notification_id: int):
        return await self.repo.mark_as_unread(user_id, notification_id)

    async def mark_all_as_read(self, user_id: int) -> int:
        return await self.repo.mark_all_as_read(user_id)

    async def delete_user_notification(self, user_id: int, notification_id: int) -> bool:
        return await self.repo.delete_user_notification(user_id, notification_id)

    async def subscribe_push(self, user_id: int, endpoint: str, p256dh: str, auth: str):
        return await self.repo.save_push_subscription(user_id, endpoint, p256dh, auth)

    async def unsubscribe_push(self, user_id: int, endpoint: str) -> bool:
        return await self.repo.delete_push_subscription(user_id, endpoint)
