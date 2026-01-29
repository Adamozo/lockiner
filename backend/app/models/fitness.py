"""Fitness Module Models."""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class Workout(Base):
    """Workout session containing multiple exercises."""
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(String, nullable=False, index=True)  # ISO 8601: YYYY-MM-DD
    name = Column(String, nullable=False)  # e.g., "Push Day", "Leg Day"
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    completed = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    user = relationship("User")
    exercises = relationship("Exercise", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workout(id={self.id}, name={self.name}, date={self.date})>"


class Exercise(Base):
    """Individual exercise within a workout."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    rest_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    workout = relationship("Workout", back_populates="exercises")

    def __repr__(self):
        return f"<Exercise(id={self.id}, name={self.name}, sets={self.sets}x{self.reps})>"


class WeightEntry(Base):
    """Body weight measurement entry."""
    __tablename__ = "weight_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(String, nullable=False, index=True)  # ISO 8601: YYYY-MM-DD
    weight_kg = Column(Float, nullable=False)
    body_fat_percentage = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<WeightEntry(id={self.id}, date={self.date}, weight_kg={self.weight_kg})>"
