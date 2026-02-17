"""Medicine/Supplement module schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


# --- Medicine Schedule ---

class MedicineScheduleCreate(BaseModel):
    """Schema for creating a medicine schedule."""
    frequency_type: str = Field(..., pattern=r"^(daily|every_n_days|weekly|monthly)$")
    frequency_value: Optional[int] = Field(None, ge=2, description="N for every_n_days frequency")
    time_of_day: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM format")
    days_of_week: Optional[str] = Field(None, pattern=r"^[0-6](,[0-6])*$", description="CSV weekdays 0=Mon..6=Sun")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    notifications_enabled: bool = True


class MedicineScheduleUpdate(BaseModel):
    """Schema for updating a medicine schedule."""
    frequency_type: Optional[str] = Field(None, pattern=r"^(daily|every_n_days|weekly|monthly)$")
    frequency_value: Optional[int] = Field(None, ge=2)
    time_of_day: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    days_of_week: Optional[str] = Field(None, pattern=r"^[0-6](,[0-6])*$")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    notifications_enabled: Optional[bool] = None
    active: Optional[bool] = None


class MedicineScheduleResponse(BaseModel):
    """Schema for medicine schedule response."""
    id: int
    medicine_id: int
    frequency_type: str
    frequency_value: Optional[int] = None
    time_of_day: str
    days_of_week: Optional[str] = None
    day_of_month: Optional[int] = None
    notifications_enabled: bool
    active: bool
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Medicine ---

class MedicineCreate(BaseModel):
    """Schema for creating a medicine with optional inline schedules."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    dosage: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7, description="Hex color e.g. #FF5733")
    icon: Optional[str] = Field(None, max_length=100)
    schedules: Optional[List[MedicineScheduleCreate]] = None


class MedicineUpdate(BaseModel):
    """Schema for updating a medicine."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    dosage: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=100)
    active: Optional[bool] = None


class MedicineResponse(BaseModel):
    """Schema for medicine response with nested schedules."""
    id: int
    name: str
    description: Optional[str] = None
    dosage: Optional[str] = None
    unit: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    active: bool
    schedules: List[MedicineScheduleResponse] = []
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Medicine Log ---

class MedicineLogResponse(BaseModel):
    """Schema for medicine log response."""
    id: int
    medicine_id: int
    schedule_id: int
    scheduled_date: str
    scheduled_time: str
    taken: bool
    taken_at: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class MedicineLogMarkTaken(BaseModel):
    """Schema for marking a dose as taken or not taken."""
    taken: bool


# --- Today Dose ---

class TodayDoseResponse(BaseModel):
    """Flattened dose for today's view."""
    log_id: int
    medicine_id: int
    medicine_name: str
    medicine_color: Optional[str] = None
    medicine_icon: Optional[str] = None
    dosage: Optional[str] = None
    unit: Optional[str] = None
    scheduled_time: str
    taken: bool
    taken_at: Optional[str] = None


# --- Stats ---

class MedicineStatsResponse(BaseModel):
    """Medicine statistics for dashboard."""
    today_total: int
    today_taken: int
    weekly_adherence_pct: float
    current_streak_days: int
