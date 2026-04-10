from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class Voucher(Base):
    """Registration voucher - required for account creation."""
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)  # UUID string
    status = Column(String(20), nullable=False, default="available")  # available | used | blocked
    used_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    used_at = Column(String, nullable=True)  # ISO 8601 datetime
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    used_by = relationship("User", back_populates="voucher")

    def __repr__(self):
        return f"<Voucher(id={self.id}, code={self.code[:8]}..., used={self.used_by_user_id is not None})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email_hash = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String(20), nullable=False, default="user")  # user | admin
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)
    totp_secret_encrypted = Column(Text, nullable=True)
    totp_enabled = Column(Boolean, default=False)
    recovery_codes_hash = Column(Text, nullable=True)
    language = Column(String(10), nullable=False, default="en")
    encrypted_dek = Column(Text, nullable=True)
    dek_salt = Column(String, nullable=True)

    household_memberships = relationship("HouseholdMember", back_populates="user")
    api_keys = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    voucher = relationship("Voucher", back_populates="used_by", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class UserAPIKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<UserAPIKey(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
