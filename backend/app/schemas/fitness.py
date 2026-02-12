"""Fitness module schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# --- Exercise Set ---

class ExerciseSetCreate(BaseModel):
    """Schema for creating an individual set."""
    set_number: int = Field(..., ge=1)
    reps: int = Field(..., ge=1)
    weight_kg: float = Field(..., ge=0)
    completed: bool = False


class ExerciseSetResponse(ExerciseSetCreate):
    """Schema for exercise set response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Exercise ---

class ExerciseBase(BaseModel):
    """Base schema for exercise data."""
    name: str = Field(..., min_length=1, max_length=255)
    sets: int = Field(..., ge=1)
    reps: int = Field(..., ge=1)
    weight_kg: float = Field(..., ge=0)
    rest_seconds: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    """Schema for creating an exercise."""
    sets_detail: Optional[List[ExerciseSetCreate]] = None


class ExerciseResponse(ExerciseBase):
    """Schema for exercise response."""
    id: int
    sets_detail: List[ExerciseSetResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Workout ---

class WorkoutBase(BaseModel):
    """Base schema for workout data."""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    name: str = Field(..., min_length=1, max_length=255)
    duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    """Schema for creating a workout with exercises."""
    exercises: List[ExerciseCreate] = []
    completed: Optional[bool] = True


class WorkoutUpdate(BaseModel):
    """Schema for updating a workout."""
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    completed: Optional[bool] = None
    exercises: Optional[List[ExerciseCreate]] = None


class WorkoutResponse(WorkoutBase):
    """Schema for workout response."""
    id: int
    completed: bool
    exercises: List[ExerciseResponse]
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Weight Entry ---

class WeightEntryBase(BaseModel):
    """Base schema for weight entry data."""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    weight_kg: float = Field(..., gt=0, le=500)
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class WeightEntryCreate(WeightEntryBase):
    """Schema for creating a weight entry."""
    pass


class WeightEntryUpdate(BaseModel):
    """Schema for updating a weight entry."""
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class WeightEntryResponse(WeightEntryBase):
    """Schema for weight entry response."""
    id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# --- Fitness Stats ---

class FitnessStatsResponse(BaseModel):
    """Schema for fitness statistics response."""
    total_workouts: int
    workouts_this_week: int
    workouts_this_month: int
    total_weight_lifted_kg: float
    current_weight_kg: Optional[float] = None
    weight_change_kg: Optional[float] = None
