"""Medicine/Supplement Module Models."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class Medicine(Base):
    """A medicine or supplement that a user takes."""
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    dosage = Column(String, nullable=True)  # e.g., "500mg", "1 tablet"
    unit = Column(String, nullable=True)  # e.g., "mg", "ml", "tablet"
    color = Column(String, nullable=True)  # hex color for UI
    icon = Column(String, nullable=True)  # icon identifier
    active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")
    schedules = relationship("MedicineSchedule", back_populates="medicine", cascade="all, delete-orphan", order_by="MedicineSchedule.time_of_day")
    logs = relationship("MedicineLog", back_populates="medicine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Medicine(id={self.id}, name={self.name})>"


class MedicineSchedule(Base):
    """When a medicine should be taken."""
    __tablename__ = "medicine_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    frequency_type = Column(String, nullable=False)  # daily, every_n_days, weekly, monthly
    frequency_value = Column(Integer, nullable=True)  # N for every_n_days
    time_of_day = Column(String, nullable=False)  # "HH:MM"
    days_of_week = Column(String, nullable=True)  # CSV "0,2,4" (Mon=0..Sun=6)
    day_of_month = Column(Integer, nullable=True)  # 1-31
    notifications_enabled = Column(Boolean, default=True)
    active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    medicine = relationship("Medicine", back_populates="schedules")
    logs = relationship("MedicineLog", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MedicineSchedule(id={self.id}, frequency={self.frequency_type}, time={self.time_of_day})>"


class MedicineLog(Base):
    """Record of whether a scheduled dose was taken."""
    __tablename__ = "medicine_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("medicine_schedules.id", ondelete="CASCADE"), nullable=False)
    scheduled_date = Column(String, nullable=False)  # ISO 8601: YYYY-MM-DD
    scheduled_time = Column(String, nullable=False)  # "HH:MM"
    taken = Column(Boolean, default=False)
    taken_at = Column(String, nullable=True)  # ISO 8601 timestamp
    created_at = Column(String, default=lambda: utc_now().isoformat())

    __table_args__ = (
        UniqueConstraint("schedule_id", "scheduled_date", name="uq_medicine_logs_schedule_date"),
    )

    # Relationships
    medicine = relationship("Medicine", back_populates="logs")
    schedule = relationship("MedicineSchedule", back_populates="logs")

    def __repr__(self):
        return f"<MedicineLog(id={self.id}, date={self.scheduled_date}, taken={self.taken})>"
