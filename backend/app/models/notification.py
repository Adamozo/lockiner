from sqlalchemy import Column, Integer, String, Text, ForeignKey
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
