from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class Household(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uid = Column(String, unique=True, nullable=False, index=True)  # UUID string
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    members = relationship("HouseholdMember", back_populates="household", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Household(id={self.id}, uid={self.uid}, name={self.name})>"


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default="member")  # manager, member
    status = Column(String, nullable=False, default="active")  # active, blocked
    joined_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household", back_populates="members")
    user = relationship("User", back_populates="household_memberships")

    def __repr__(self):
        return f"<HouseholdMember(id={self.id}, household_id={self.household_id}, user_id={self.user_id}, role={self.role})>"


class HouseholdInvitation(Base):
    __tablename__ = "household_invitations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)  # UUID string
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(String, nullable=True)  # ISO 8601 datetime, null = never expires
    max_uses = Column(Integer, nullable=True)  # null = unlimited
    uses_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household", backref="invitations")
    creator = relationship("User")

    def __repr__(self):
        return f"<HouseholdInvitation(id={self.id}, household_id={self.household_id}, token={self.token[:8]}...)>"
