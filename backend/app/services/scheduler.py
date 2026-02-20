"""Background scheduler for sending reminder notifications."""

import json
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from ..database import AsyncSessionLocal
from ..repositories.notification_schedule import NotificationScheduleRepository
from ..repositories.notification import NotificationRepository
from ..repositories.medicine import MedicineScheduleRepository
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
    "backup": {
        "title": "Backup Reminder",
        "body": "Time to download your data backup and store it safely.",
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
    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone)
    now = datetime.now(tz)
    current_hour = now.hour
    current_minute = now.minute
    current_dow = now.weekday()  # 0=Mon..6=Sun
    current_dom = now.day

    logger.debug(
        f"Scheduler tick: {now.isoformat()} (h={current_hour}, m={current_minute}, dow={current_dow}, dom={current_dom})"
    )

    async with AsyncSessionLocal() as db:
        # Check medicine reminders
        await _check_medicine_reminders(db, now, current_hour, current_minute, settings)
        schedule_repo = NotificationScheduleRepository(db)
        notification_repo = NotificationRepository(db)

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

        # Try to import pywebpush once for all schedules
        webpush_available = False
        webpush_func = None
        WebPushException = None
        vapid_key = settings.vapid_private_key_raw
        if vapid_key:
            try:
                from pywebpush import webpush as _webpush, WebPushException as _WPE
                webpush_func = _webpush
                WebPushException = _WPE
                webpush_available = True
            except ImportError:
                logger.warning("pywebpush not installed, push notifications disabled")
        else:
            logger.warning("VAPID private key not configured, push notifications disabled")

        for schedule in due_schedules:
            # Custom reminders use their own title/body; built-ins use REMINDER_MESSAGES
            if schedule.reminder_type.startswith("custom_"):
                if not schedule.custom_title or not schedule.custom_body:
                    continue
                title = schedule.custom_title
                body = schedule.custom_body
                notif_type = "reminder"
            else:
                msg = REMINDER_MESSAGES.get(schedule.reminder_type)
                if not msg:
                    continue
                title = msg["title"]
                body = msg["body"]
                notif_type = "reminder"

            # 1. Create in-app notification record
            notification = await notification_repo.create_notification(
                title=title,
                body=body,
                notification_type=notif_type,
                created_by_user_id=None,
            )
            await notification_repo.create_user_notifications(
                notification.id, [schedule.user_id]
            )
            logger.info(
                f"Created in-app notification for {schedule.reminder_type} reminder, user {schedule.user_id}"
            )

            # 2. Send web push
            if not webpush_available:
                continue

            subscriptions = await notification_repo.get_push_subscriptions([schedule.user_id])
            if not subscriptions:
                logger.info(
                    f"User {schedule.user_id} has no push subscriptions, "
                    f"skipping web push for {schedule.reminder_type} reminder"
                )
                continue

            payload = json.dumps({"title": title, "body": body})

            for sub in subscriptions:
                try:
                    webpush_func(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {
                                "p256dh": sub.p256dh_key,
                                "auth": sub.auth_key,
                            },
                        },
                        data=payload,
                        vapid_private_key=vapid_key,
                        vapid_claims={
                            "sub": f"mailto:{settings.vapid_contact_email}",
                        },
                    )
                    logger.info(
                        f"Sent {schedule.reminder_type} push to user {schedule.user_id}"
                    )
                except WebPushException as e:
                    if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
                        await notification_repo.delete_push_subscription_by_endpoint(sub.endpoint)
                        logger.info(f"Removed stale push subscription: {sub.endpoint[:50]}")
                    else:
                        logger.warning(f"Push failed for user {schedule.user_id}: {e}")
                except Exception as e:
                    logger.warning(f"Push error for user {schedule.user_id}: {e}")


async def _check_medicine_reminders(db, now, current_hour, current_minute, settings):
    """Check medicine schedules and send reminders for doses due now."""
    from .medicine import MedicineService

    schedule_repo = MedicineScheduleRepository(db)
    notification_repo = NotificationRepository(db)

    active_schedules = await schedule_repo.get_active_with_notifications()
    if not active_schedules:
        return

    today = now.date()
    time_str = f"{current_hour:02d}:{current_minute:02d}"

    due_schedules = []
    for schedule in active_schedules:
        if schedule.time_of_day != time_str:
            continue
        if not MedicineService._is_schedule_due_on_date(schedule, today):
            continue
        due_schedules.append(schedule)

    if not due_schedules:
        return

    logger.info(f"Found {len(due_schedules)} medicine reminder(s) to send")

    # Try to import pywebpush once
    webpush_available = False
    webpush_func = None
    WebPushException = None
    vapid_key = settings.vapid_private_key_raw
    if vapid_key:
        try:
            from pywebpush import webpush as _webpush, WebPushException as _WPE
            webpush_func = _webpush
            WebPushException = _WPE
            webpush_available = True
        except ImportError:
            pass

    for schedule in due_schedules:
        medicine = schedule.medicine
        if not medicine or not medicine.active:
            continue

        user_id = medicine.user_id
        title = "Medicine Reminder"
        body = f"Time to take {medicine.name}"
        if medicine.dosage:
            body += f" ({medicine.dosage}{medicine.unit or ''})"

        # Create in-app notification
        notification = await notification_repo.create_notification(
            title=title,
            body=body,
            notification_type="reminder",
            created_by_user_id=None,
        )
        await notification_repo.create_user_notifications(notification.id, [user_id])
        logger.info(f"Created medicine reminder for '{medicine.name}', user {user_id}")

        # Send web push
        if not webpush_available:
            continue

        subscriptions = await notification_repo.get_push_subscriptions([user_id])
        if not subscriptions:
            continue

        payload = json.dumps({"title": title, "body": body})

        for sub in subscriptions:
            try:
                webpush_func(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
                    },
                    data=payload,
                    vapid_private_key=vapid_key,
                    vapid_claims={"sub": f"mailto:{settings.vapid_contact_email}"},
                )
                logger.info(f"Sent medicine push for '{medicine.name}' to user {user_id}")
            except WebPushException as e:
                if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
                    await notification_repo.delete_push_subscription_by_endpoint(sub.endpoint)
                    logger.info(f"Removed stale push subscription: {sub.endpoint[:50]}")
                else:
                    logger.warning(f"Medicine push failed for user {user_id}: {e}")
            except Exception as e:
                logger.warning(f"Medicine push error for user {user_id}: {e}")


async def check_todo_notifications():
    """Check todo notification rules and send due notifications."""
    try:
        await _check_todo_notifications_inner()
    except Exception as e:
        logger.error(f"Todo notification scheduler error: {e}", exc_info=True)


async def _check_todo_notifications_inner():
    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone)
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    # End of day reference: 23:59 local time
    end_of_day_minutes = 23 * 60 + 59
    now_minutes = now.hour * 60 + now.minute

    async with AsyncSessionLocal() as db:
        from ..repositories.todo import TodoNotificationRuleRepository, TodoListRepository, TodoItemRepository
        from ..repositories.notification import NotificationRepository

        rule_repo = TodoNotificationRuleRepository(db)
        list_repo = TodoListRepository(db)
        item_repo = TodoItemRepository(db)
        notification_repo = NotificationRepository(db)

        rules = await rule_repo.get_enabled_all_users()
        if not rules:
            return

        # Preload today's lists once
        today_lists = await list_repo.get_all_with_enabled_rules()
        lists_by_user: dict[int, list] = {}
        for lst in today_lists:
            lists_by_user.setdefault(lst.user_id, []).append(lst)

        # Setup pywebpush once
        webpush_available = False
        webpush_func = None
        WebPushException = None
        vapid_key = settings.vapid_private_key_raw
        if vapid_key:
            try:
                from pywebpush import webpush as _webpush, WebPushException as _WPE
                webpush_func = _webpush
                WebPushException = _WPE
                webpush_available = True
            except ImportError:
                pass

        for rule in rules:
            should_fire = False

            if rule.trigger_type == "fixed_time" and rule.fixed_time:
                # Fire at exact minute, once per day
                last_sent_date = rule.last_sent_at[:10] if rule.last_sent_at else None
                should_fire = (rule.fixed_time == time_str) and (last_sent_date != today_str)

            elif rule.trigger_type == "before_end_of_day" and rule.minutes_before_end is not None:
                target_minutes = end_of_day_minutes - rule.minutes_before_end
                target_h, target_m = divmod(target_minutes, 60)
                target_time = f"{target_h:02d}:{target_m:02d}"
                last_sent_date = rule.last_sent_at[:10] if rule.last_sent_at else None
                should_fire = (target_time == time_str) and (last_sent_date != today_str)

            elif rule.trigger_type == "interval" and rule.interval_minutes and rule.window_start and rule.window_end:
                start_h, start_m = map(int, rule.window_start.split(":"))
                end_h, end_m = map(int, rule.window_end.split(":"))
                window_start_min = start_h * 60 + start_m
                window_end_min = end_h * 60 + end_m
                in_window = window_start_min <= now_minutes <= window_end_min
                if in_window:
                    if rule.last_sent_at is None:
                        should_fire = True
                    else:
                        from datetime import datetime as dt, timezone as _tz
                        last = dt.fromisoformat(rule.last_sent_at)
                        # Normalise both to UTC before comparing to avoid DST issues
                        now_utc = now.astimezone(_tz.utc)
                        last_utc = last.astimezone(_tz.utc) if last.tzinfo else last.replace(tzinfo=_tz.utc)
                        elapsed_seconds = (now_utc - last_utc).total_seconds()
                        should_fire = elapsed_seconds >= rule.interval_minutes * 60

            if not should_fire:
                continue

            user_lists = lists_by_user.get(rule.user_id, [])
            if not user_lists:
                continue

            # Collect incomplete items from today's lists
            all_items = [item for lst in user_lists for item in lst.items]
            incomplete = [i for i in all_items if not i.completed]

            if rule.notify_only_if_incomplete and not incomplete:
                continue

            # Build notification body
            if incomplete:
                names = ", ".join(i.title for i in incomplete[:5])
                suffix = f" (+{len(incomplete) - 5} more)" if len(incomplete) > 5 else ""
                body = f"To do: {names}{suffix}"
            else:
                body = "All tasks for today completed!"

            label = rule.label or "Todo reminder"
            title = f"Todo – {label}"

            # Create in-app notification
            notification = await notification_repo.create_notification(
                title=title,
                body=body,
                notification_type="reminder",
                created_by_user_id=None,
            )
            await notification_repo.create_user_notifications(notification.id, [rule.user_id])
            logger.info(f"Sent todo notification (rule {rule.id}) to user {rule.user_id}")

            # Update last_sent_at
            rule.last_sent_at = now.isoformat()
            await db.commit()

            # Web push
            if not webpush_available:
                continue

            subscriptions = await notification_repo.get_push_subscriptions([rule.user_id])
            payload = json.dumps({"title": title, "body": body})
            for sub in subscriptions:
                try:
                    webpush_func(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
                        },
                        data=payload,
                        vapid_private_key=vapid_key,
                        vapid_claims={"sub": f"mailto:{settings.vapid_contact_email}"},
                    )
                except WebPushException as e:
                    if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
                        await notification_repo.delete_push_subscription_by_endpoint(sub.endpoint)
                    else:
                        logger.warning(f"Todo push failed for user {rule.user_id}: {e}")
                except Exception as e:
                    logger.warning(f"Todo push error for user {rule.user_id}: {e}")

        # Per-item reminders
        items_with_reminders = await item_repo.get_items_with_reminders_at(time_str, today_str)
        for item in items_with_reminders:
            title = "Task Reminder"
            body = item.title
            notification = await notification_repo.create_notification(
                title=title,
                body=body,
                notification_type="reminder",
                created_by_user_id=None,
            )
            await notification_repo.create_user_notifications(notification.id, [item.user_id])
            logger.info(f"Sent item reminder for todo item {item.id}, user {item.user_id}")

            if not webpush_available:
                continue
            subscriptions = await notification_repo.get_push_subscriptions([item.user_id])
            payload = json.dumps({"title": title, "body": body})
            for sub in subscriptions:
                try:
                    webpush_func(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
                        },
                        data=payload,
                        vapid_private_key=vapid_key,
                        vapid_claims={"sub": f"mailto:{settings.vapid_contact_email}"},
                    )
                except WebPushException as e:
                    if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
                        await notification_repo.delete_push_subscription_by_endpoint(sub.endpoint)
                    else:
                        logger.warning(f"Todo item push failed for user {item.user_id}: {e}")
                except Exception as e:
                    logger.warning(f"Todo item push error for user {item.user_id}: {e}")


async def check_auto_backups():
    """Check and run any due automatic backups."""
    try:
        await _check_auto_backups_inner()
    except Exception as e:
        logger.error(f"Auto-backup scheduler error: {e}", exc_info=True)


async def _check_auto_backups_inner():
    settings = get_settings()
    tz = ZoneInfo(settings.app_timezone)
    now = datetime.now(tz)

    async with AsyncSessionLocal() as db:
        from ..repositories.backup import BackupSettingsRepository, HouseholdBackupSettingsRepository
        from ..services.backup import BackupService, HouseholdBackupService

        user_repo = BackupSettingsRepository(db)
        for bs in await user_repo.get_all_enabled_auto_backup():
            if _is_backup_due(bs, now):
                await BackupService(db).run_user_auto_backup(bs.user_id, bs)

        hh_repo = HouseholdBackupSettingsRepository(db)
        for bs in await hh_repo.get_all_enabled_auto_backup():
            if _is_backup_due(bs, now):
                await HouseholdBackupService(db).run_household_auto_backup(bs.household_id, bs)


def _is_backup_due(bs, now) -> bool:
    """Return True if the backup schedule matches the current time."""
    if bs.frequency == "daily":
        return bs.hour == now.hour and bs.minute == now.minute
    elif bs.frequency == "weekly":
        return (
            bs.hour == now.hour
            and bs.minute == now.minute
            and bs.day_of_week == now.weekday()
        )
    elif bs.frequency == "monthly":
        return (
            bs.hour == now.hour
            and bs.minute == now.minute
            and bs.day_of_month == now.day
        )
    return False


def start_scheduler():
    """Start the background scheduler with a per-minute cron job."""
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(minute="*"),
        id="reminder_check",
        replace_existing=True,
    )
    scheduler.add_job(
        check_auto_backups,
        trigger=CronTrigger(minute="*"),
        id="auto_backup_check",
        replace_existing=True,
    )
    scheduler.add_job(
        check_todo_notifications,
        trigger=CronTrigger(minute="*"),
        id="todo_notification_check",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Notification scheduler started (checking every minute)")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Notification scheduler stopped")
