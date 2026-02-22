import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalStatsResponse,
    ReportGenerateRequest,
    JournalReportResponse,
    ReportData,
    MeditationSessionCreate,
    MeditationSessionUpdate,
    MeditationSessionResponse,
    MeditationStatsResponse,
)
from ..services.journal import (
    JournalService,
    JournalEntryNotFoundError,
    JournalEntryDateNotFoundError,
    JournalEntryConflictError,
    JournalAccessDeniedError,
    JournalReportNotFoundError,
    MeditationSessionNotFoundError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/journal", tags=["journal"])

# ---------------------------------------


async def get_journal_service(db: AsyncSession = Depends(get_db)) -> JournalService:
    return JournalService(db)


# ---------------------------------------
# Entries
# ---------------------------------------


@router.get("/entries", response_model=List[JournalEntryResponse])
async def list_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get all journal entries for the current user."""
    return await service.list_entries(
        user_id=current_user.id, skip=skip, limit=limit,
        start_date=start_date, end_date=end_date,
    )


@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    entry: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Create a new journal entry. Returns 409 if date already exists."""
    try:
        return await service.create_entry(entry, user_id=current_user.id)
    except JournalEntryConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/entries/date/{date}", response_model=JournalEntryResponse)
async def get_entry_by_date(
    date: str,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get a journal entry by date."""
    try:
        return await service.get_entry_by_date(date, user_id=current_user.id)
    except JournalEntryDateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get a specific journal entry by ID."""
    try:
        return await service.get_entry(entry_id, user_id=current_user.id)
    except JournalEntryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JournalAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_entry(
    entry_id: int,
    entry_update: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Update a journal entry (replaces items if provided)."""
    try:
        return await service.update_entry(entry_id, entry_update, user_id=current_user.id)
    except JournalEntryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JournalAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Delete a journal entry."""
    try:
        await service.delete_entry(entry_id, user_id=current_user.id)
    except JournalEntryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JournalAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------
# Stats
# ---------------------------------------


@router.get("/stats", response_model=JournalStatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get journal statistics for the current user."""
    return await service.get_stats(user_id=current_user.id)


# ---------------------------------------
# Reports
# ---------------------------------------


@router.post("/reports/generate", response_model=JournalReportResponse)
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Generate or refresh a report for a given period."""
    report = await service.generate_report(request, user_id=current_user.id)
    return _report_to_response(report)


@router.get("/reports/{report_type}/{period}", response_model=JournalReportResponse)
async def get_report(
    report_type: str,
    period: str,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get a specific report."""
    try:
        report = await service.get_report(current_user.id, report_type, period)
        return _report_to_response(report)
    except JournalReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/reports/{report_type}", response_model=List[JournalReportResponse])
async def list_reports(
    report_type: str,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """List all reports of a given type."""
    reports = await service.list_reports(current_user.id, report_type)
    return [_report_to_response(r) for r in reports]


def _report_to_response(report) -> dict:
    """Convert a JournalReport model to response dict, parsing JSON data."""
    data = json.loads(report.data) if isinstance(report.data, str) else report.data
    return {
        "id": report.id,
        "report_type": report.report_type,
        "period": report.period,
        "data": data,
        "entry_count": report.entry_count,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


# ---------------------------------------
# Meditation
# ---------------------------------------


@router.get("/meditation", response_model=List[MeditationSessionResponse])
async def list_meditation_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get all meditation sessions for the current user."""
    return await service.list_meditation_sessions(user_id=current_user.id, skip=skip, limit=limit)


@router.get("/meditation/active", response_model=Optional[MeditationSessionResponse])
async def get_active_meditation(
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get the current in-progress meditation session, if any."""
    return await service.get_active_meditation(user_id=current_user.id)


@router.get("/meditation/stats", response_model=MeditationStatsResponse)
async def get_meditation_stats(
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Get meditation statistics for the current user."""
    return await service.get_meditation_stats(user_id=current_user.id)


@router.post("/meditation", response_model=MeditationSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_meditation(
    session_data: MeditationSessionCreate,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Start a new meditation session (creates a draft)."""
    return await service.start_meditation(session_data, user_id=current_user.id)


@router.put("/meditation/{session_id}", response_model=MeditationSessionResponse)
async def update_meditation(
    session_id: int,
    session_update: MeditationSessionUpdate,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Update a meditation session (save duration, complete it)."""
    try:
        return await service.update_meditation(session_id, session_update, user_id=current_user.id)
    except MeditationSessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JournalAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/meditation/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meditation(
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    """Delete a meditation session."""
    try:
        await service.delete_meditation(session_id, user_id=current_user.id)
    except MeditationSessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JournalAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
