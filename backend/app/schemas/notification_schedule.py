"""Notification schedule schemas for reminder configuration."""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Literal


class NotificationScheduleBase(BaseModel):
    """Base schema with auto-cleaning of frequency-irrelevant fields."""
    reminder_type: str = Field(max_length=50)
    enabled: bool = False
    frequency: Literal["daily", "weekly", "monthly"] = "daily"
    hour: int = Field(default=9, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    custom_name: Optional[str] = Field(default=None, max_length=100)
    custom_icon: Optional[str] = Field(default=None, max_length=100)
    custom_title: Optional[str] = Field(default=None, max_length=200)
    custom_body: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def clean_frequency_fields(self):
        """Nullify fields irrelevant to the chosen frequency."""
        if self.frequency == "daily":
            self.day_of_week = None
            self.day_of_month = None
        elif self.frequency == "weekly":
            self.day_of_month = None
            if self.day_of_week is None:
                self.day_of_week = 0  # default Monday
        elif self.frequency == "monthly":
            self.day_of_week = None
            if self.day_of_month is None:
                self.day_of_month = 1  # default 1st
        return self


class NotificationScheduleUpdate(BaseModel):
    """Schema for updating a single schedule."""
    enabled: Optional[bool] = None
    frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    hour: Optional[int] = Field(default=None, ge=0, le=23)
    minute: Optional[int] = Field(default=None, ge=0, le=59)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)


class NotificationScheduleResponse(BaseModel):
    """Response schema for a single schedule."""
    id: int
    reminder_type: str
    enabled: bool
    frequency: str
    hour: int
    minute: int
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    custom_name: Optional[str] = None
    custom_icon: Optional[str] = None
    custom_title: Optional[str] = None
    custom_body: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationScheduleBulkUpdate(BaseModel):
    """Schema for bulk updating all schedules."""
    schedules: List[NotificationScheduleBase]


class NotificationScheduleListResponse(BaseModel):
    """Response schema for list of schedules."""
    schedules: List[NotificationScheduleResponse]


class CustomReminderCreate(BaseModel):
    """Schema for creating a custom reminder."""
    custom_name: str = Field(max_length=100)
    custom_icon: str = Field(max_length=100)
    custom_title: str = Field(max_length=200)
    custom_body: str = Field(max_length=500)
    enabled: bool = True
    frequency: Literal["daily", "weekly", "monthly"] = "daily"
    hour: int = Field(default=9, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)

    @model_validator(mode="after")
    def clean_frequency_fields(self):
        if self.frequency == "daily":
            self.day_of_week = None
            self.day_of_month = None
        elif self.frequency == "weekly":
            self.day_of_month = None
            if self.day_of_week is None:
                self.day_of_week = 0
        elif self.frequency == "monthly":
            self.day_of_week = None
            if self.day_of_month is None:
                self.day_of_month = 1
        return self
