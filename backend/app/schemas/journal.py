"""Journal module schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


JOURNAL_CATEGORIES = ["accomplished", "grateful", "proud", "annoyed", "learned"]


# --- Journal Item ---

class JournalItemCreate(BaseModel):
    """Schema for creating a journal item."""
    category: str = Field(..., pattern=r"^(accomplished|grateful|proud|annoyed|learned)$")
    position: int = Field(..., ge=0)
    content: str = Field(..., min_length=1)


class JournalItemResponse(JournalItemCreate):
    """Schema for journal item response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Journal Entry ---

class JournalEntryCreate(BaseModel):
    """Schema for creating a journal entry."""
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    items: List[JournalItemCreate] = []


class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    items: Optional[List[JournalItemCreate]] = None


class JournalEntryResponse(BaseModel):
    """Schema for journal entry response."""
    id: int
    date: str
    mood_score: Optional[int] = None
    notes: Optional[str] = None
    items: List[JournalItemResponse] = []
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Journal Stats ---

class JournalStatsResponse(BaseModel):
    """Dashboard statistics for journal module."""
    total_entries: int
    entries_this_week: int
    entries_this_month: int
    current_streak: int
    longest_streak: int
    avg_mood: Optional[float] = None


# --- Journal Report ---

class ReportGenerateRequest(BaseModel):
    """Request to generate/refresh a report."""
    report_type: str = Field(..., pattern=r"^(monthly|yearly)$")
    period: str = Field(..., pattern=r"^\d{4}(-\d{2})?$")  # YYYY-MM or YYYY


class CategoryReportData(BaseModel):
    """Per-category data in a report."""
    count: int
    items: List[str]


class ReportData(BaseModel):
    """Structure of report JSON data."""
    categories: Dict[str, CategoryReportData]
    avg_mood: Optional[float] = None
    entry_count: int
    current_streak: int
    longest_streak: int


class JournalReportResponse(BaseModel):
    """Schema for journal report response."""
    id: int
    report_type: str
    period: str
    data: ReportData
    entry_count: int
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
