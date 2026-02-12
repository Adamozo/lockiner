from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class Notification(Base):
    """Global notification created by admin."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="general")  # general | system | alert
    created_at = Column(String, default=lambda: utc_now().isoformat())
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    user_notifications = relationship("UserNotification", back_populates="notification", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Notification(id={self.id}, title={self.title[:30]})>"


class UserNotification(Base):
    """M2M junction: user <-> notification. DELETE = remove junction, not notification."""
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="unread")  # unread | read
    read_at = Column(String, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    notification = relationship("Notification", back_populates="user_notifications")

    def __repr__(self):
        return f"<UserNotification(id={self.id}, user_id={self.user_id}, status={self.status})>"


class PushSubscription(Base):
    """Web Push subscription for a user's browser/device."""
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    endpoint = Column(Text, nullable=False)
    p256dh_key = Column(String, nullable=False)
    auth_key = Column(String, nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    def __repr__(self):
        return f"<PushSubscription(id={self.id}, user_id={self.user_id})>"


class NotificationSchedule(Base):
    """Per-user reminder schedule configuration."""
    __tablename__ = "notification_schedules"
    __table_args__ = (
        UniqueConstraint("user_id", "reminder_type", name="uq_user_reminder_type"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reminder_type = Column(String(50), nullable=False)  # workout | weight | receipt | finance | custom_*
    enabled = Column(Boolean, nullable=False, default=False)
    frequency = Column(String(20), nullable=False, default="daily")  # daily | weekly | monthly
    hour = Column(Integer, nullable=False, default=9)
    minute = Column(Integer, nullable=False, default=0)
    day_of_week = Column(Integer, nullable=True)  # 0=Mon..6=Sun (weekly only)
    day_of_month = Column(Integer, nullable=True)  # 1-31 (monthly only)
    custom_name = Column(String(100), nullable=True)
    custom_icon = Column(String(100), nullable=True)
    custom_title = Column(String(200), nullable=True)
    custom_body = Column(String(500), nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    def __repr__(self):
        return f"<NotificationSchedule(id={self.id}, user_id={self.user_id}, type={self.reminder_type})>"
