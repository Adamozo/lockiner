"""Background scheduler for sending reminder notifications."""

import json
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..database import AsyncSessionLocal
from ..repositories.notification_schedule import NotificationScheduleRepository
from ..repositories.notification import NotificationRepository
from ..config import get_settings

logger = logging.getLogger(__name__)

REMINDER_MESSAGES = {
    "workout": {
        "title": "Workout Reminder",
        "body": "Time to get moving! Log your workout today.",
    },
    "weight": {
        "title": "Weight Reminder",
        "body": "Don't forget to log your weight today.",
    },
    "receipt": {
        "title": "Receipt Reminder",
        "body": "Have any receipts to upload? Keep your finances in check.",
    },
    "finance": {
        "title": "Finance Reminder",
        "body": "Take a moment to review your financial summary.",
    },
}

scheduler = AsyncIOScheduler()


async def check_and_send_reminders():
    """Check all 3 frequency types and send push notifications for due schedules."""
    try:
        await _check_and_send_reminders_inner()
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)


async def _check_and_send_reminders_inner():
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    current_minute = now.minute
    current_dow = now.weekday()  # 0=Mon..6=Sun
    current_dom = now.day

    logger.debug(
        f"Scheduler tick: {now.isoformat()} (h={current_hour}, m={current_minute}, dow={current_dow}, dom={current_dom})"
    )

    async with AsyncSessionLocal() as db:
        schedule_repo = NotificationScheduleRepository(db)
        notification_repo = NotificationRepository(db)
        settings = get_settings()

        due_schedules = []

        # Daily schedules
        daily = await schedule_repo.get_due_schedules(
            frequency="daily", hour=current_hour, minute=current_minute
        )
        due_schedules.extend(daily)

        # Weekly schedules
        weekly = await schedule_repo.get_due_schedules(
            frequency="weekly", hour=current_hour, minute=current_minute,
            day_of_week=current_dow,
        )
        due_schedules.extend(weekly)

        # Monthly schedules
        monthly = await schedule_repo.get_due_schedules(
            frequency="monthly", hour=current_hour, minute=current_minute,
            day_of_month=current_dom,
        )
        due_schedules.extend(monthly)

        if not due_schedules:
            return

        logger.info(f"Found {len(due_schedules)} due reminder(s) to send")

        if not settings.vapid_private_key:
            logger.warning("VAPID private key not configured, skipping push")
            return

        try:
            from pywebpush import webpush, WebPushException
        except ImportError:
            logger.warning("pywebpush not installed, skipping push notifications")
            return

        for schedule in due_schedules:
            # Custom reminders use their own title/body; built-ins use REMINDER_MESSAGES
            if schedule.reminder_type.startswith("custom_"):
                if not schedule.custom_title or not schedule.custom_body:
                    continue
                title = schedule.custom_title
                body = schedule.custom_body
            else:
                msg = REMINDER_MESSAGES.get(schedule.reminder_type)
                if not msg:
                    continue
                title = msg["title"]
                body = msg["body"]

            subscriptions = await notification_repo.get_push_subscriptions([schedule.user_id])
            if not subscriptions:
                continue

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
                    logger.info(
                        f"Sent {schedule.reminder_type} reminder to user {schedule.user_id}"
                    )
                except WebPushException as e:
                    if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
                        await notification_repo.delete_push_subscription_by_endpoint(sub.endpoint)
                        logger.info(f"Removed stale push subscription: {sub.endpoint[:50]}")
                    else:
                        logger.warning(f"Push failed for user {schedule.user_id}: {e}")
                except Exception as e:
                    logger.warning(f"Push error for user {schedule.user_id}: {e}")


def start_scheduler():
    """Start the background scheduler with a per-minute cron job."""
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(minute="*"),
        id="reminder_check",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Notification scheduler started (checking every minute)")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Notification scheduler stopped")
