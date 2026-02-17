"""Medicine/Supplement module router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.medicine import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse,
    MedicineScheduleCreate,
    MedicineScheduleUpdate,
    MedicineScheduleResponse,
    MedicineLogResponse,
    MedicineLogMarkTaken,
    TodayDoseResponse,
    MedicineStatsResponse,
)
from ..services.medicine import (
    MedicineService,
    MedicineNotFoundError,
    MedicineScheduleNotFoundError,
    MedicineLogNotFoundError,
    MedicineAccessDeniedError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/fitness/medicines", tags=["medicines"])

# ---------------------------------------


async def get_medicine_service(db: AsyncSession = Depends(get_db)) -> MedicineService:
    return MedicineService(db)


# ---------------------------------------
# Static paths MUST come before /{medicine_id} to avoid route shadowing
# ---------------------------------------


@router.get("", response_model=List[MedicineResponse])
async def list_medicines(
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Get all medicines for the current user."""
    return await service.list_medicines(user_id=current_user.id)


@router.post("", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine: MedicineCreate,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Create a new medicine with optional inline schedules."""
    return await service.create_medicine(medicine, user_id=current_user.id)


@router.get("/today", response_model=List[TodayDoseResponse])
async def get_today_doses(
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Get today's doses with taken status."""
    return await service.get_today_doses(user_id=current_user.id)


@router.get("/stats", response_model=MedicineStatsResponse)
async def get_medicine_stats(
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Get medicine statistics for dashboard."""
    return await service.get_medicine_stats(user_id=current_user.id)


# --- Schedules (static prefix, before /{medicine_id}) ---


@router.put("/schedules/{schedule_id}", response_model=MedicineScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: MedicineScheduleUpdate,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Update a schedule."""
    try:
        return await service.update_schedule(schedule_id, schedule_update, user_id=current_user.id)
    except MedicineScheduleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Delete a schedule."""
    try:
        await service.delete_schedule(schedule_id, user_id=current_user.id)
    except MedicineScheduleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# --- Logs (static prefix, before /{medicine_id}) ---


@router.patch("/logs/{log_id}", response_model=MedicineLogResponse)
async def mark_dose(
    log_id: int,
    data: MedicineLogMarkTaken,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Mark a dose as taken or not taken."""
    try:
        return await service.mark_dose(log_id, data, user_id=current_user.id)
    except MedicineLogNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------
# Dynamic /{medicine_id} routes
# ---------------------------------------


@router.get("/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(
    medicine_id: int,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Get a specific medicine by ID."""
    try:
        return await service.get_medicine(medicine_id, user_id=current_user.id)
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
    medicine_id: int,
    medicine_update: MedicineUpdate,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Update a medicine."""
    try:
        return await service.update_medicine(medicine_id, medicine_update, user_id=current_user.id)
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicine(
    medicine_id: int,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Delete a medicine."""
    try:
        await service.delete_medicine(medicine_id, user_id=current_user.id)
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{medicine_id}/schedules", response_model=MedicineScheduleResponse, status_code=status.HTTP_201_CREATED)
async def add_schedule(
    medicine_id: int,
    schedule: MedicineScheduleCreate,
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Add a schedule to a medicine."""
    try:
        return await service.add_schedule(medicine_id, schedule, user_id=current_user.id)
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{medicine_id}/logs", response_model=List[MedicineLogResponse])
async def get_medicine_logs(
    medicine_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    service: MedicineService = Depends(get_medicine_service),
):
    """Get log history for a specific medicine."""
    try:
        medicine = await service.get_medicine(medicine_id, user_id=current_user.id)
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MedicineAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return await service.log_repo.get_logs_by_medicine(medicine.id, skip=skip, limit=limit)
