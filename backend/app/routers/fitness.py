from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import (
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse,
    WeightEntryCreate,
    WeightEntryUpdate,
    WeightEntryResponse,
    FitnessStatsResponse,
    UserBodyProfileResponse,
    UserBodyProfileUpdate,
    BodyMeasurementEntryCreate,
    BodyMeasurementEntryUpdate,
    BodyMeasurementEntryResponse,
    WorkoutTemplateCreate,
    WorkoutTemplateUpdate,
    WorkoutTemplateResponse,
)
from ..services.fitness import (
    FitnessService,
    WorkoutNotFoundError,
    WeightEntryNotFoundError,
    BodyMeasurementNotFoundError,
    FitnessAccessDeniedError,
    WorkoutTimerError,
    WorkoutTemplateNotFoundError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/fitness", tags=["fitness"])

# ---------------------------------------


async def get_fitness_service(db: AsyncSession = Depends(get_db)) -> FitnessService:
    return FitnessService(db)


# ---------------------------------------
# Workouts
# ---------------------------------------


@router.get("/workouts", response_model=List[WorkoutResponse])
async def list_workouts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get all workouts for the current user."""
    return await service.list_workouts(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Create a new workout with exercises."""
    return await service.create_workout(workout, user_id=current_user.id)


@router.get("/workouts/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get a specific workout by ID."""
    try:
        return await service.get_workout(workout_id, user_id=current_user.id)

    except WorkoutNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/workouts/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_update: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Update a workout."""
    try:
        return await service.update_workout(
            workout_id, workout_update, user_id=current_user.id
        )

    except WorkoutNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Delete a workout."""
    try:
        await service.delete_workout(workout_id, user_id=current_user.id)

    except WorkoutNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ---------------------------------------
# Weight Entries
# ---------------------------------------


@router.get("/weight-entries", response_model=List[WeightEntryResponse])
async def list_weight_entries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get all weight entries for the current user."""
    return await service.list_weight_entries(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/weight-entries", response_model=WeightEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_weight_entry(
    entry: WeightEntryCreate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Create a new weight entry."""
    return await service.create_weight_entry(entry, user_id=current_user.id)


@router.get("/weight-entries/{entry_id}", response_model=WeightEntryResponse)
async def get_weight_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get a specific weight entry by ID."""
    try:
        return await service.get_weight_entry(entry_id, user_id=current_user.id)

    except WeightEntryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/weight-entries/{entry_id}", response_model=WeightEntryResponse)
async def update_weight_entry(
    entry_id: int,
    entry_update: WeightEntryUpdate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Update a weight entry."""
    try:
        return await service.update_weight_entry(
            entry_id, entry_update, user_id=current_user.id
        )

    except WeightEntryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/weight-entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weight_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Delete a weight entry."""
    try:
        await service.delete_weight_entry(entry_id, user_id=current_user.id)

    except WeightEntryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ---------------------------------------
# Stats
# ---------------------------------------


@router.get("/stats", response_model=FitnessStatsResponse)
async def get_fitness_stats(
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get fitness statistics for the current user."""
    return await service.get_fitness_stats(user_id=current_user.id)


# ---------------------------------------
# Body Profile
# ---------------------------------------


@router.get("/body-profile", response_model=Optional[UserBodyProfileResponse])
async def get_body_profile(
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get the current user's body profile (height)."""
    return await service.get_body_profile(user_id=current_user.id)


@router.put("/body-profile", response_model=UserBodyProfileResponse)
async def upsert_body_profile(
    profile_update: UserBodyProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Create or update the current user's body profile (height)."""
    return await service.upsert_body_profile(user_id=current_user.id, data=profile_update)


# ---------------------------------------
# Body Measurements
# ---------------------------------------


@router.get("/body-measurements", response_model=List[BodyMeasurementEntryResponse])
async def list_body_measurements(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get all body measurement entries for the current user."""
    return await service.list_body_measurements(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/body-measurements", response_model=BodyMeasurementEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_body_measurement(
    entry: BodyMeasurementEntryCreate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Create a new body measurement entry."""
    return await service.create_body_measurement(entry, user_id=current_user.id)


@router.put("/body-measurements/{entry_id}", response_model=BodyMeasurementEntryResponse)
async def update_body_measurement(
    entry_id: int,
    entry_update: BodyMeasurementEntryUpdate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Update a body measurement entry."""
    try:
        return await service.update_body_measurement(
            entry_id, entry_update, user_id=current_user.id
        )

    except BodyMeasurementNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/body-measurements/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_body_measurement(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Delete a body measurement entry."""
    try:
        await service.delete_body_measurement(entry_id, user_id=current_user.id)

    except BodyMeasurementNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except FitnessAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ---------------------------------------
# Workout Timer
# ---------------------------------------


def _handle_timer_errors(e: Exception):
    if isinstance(e, WorkoutNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, FitnessAccessDeniedError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    if isinstance(e, WorkoutTimerError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    raise e


@router.post("/workouts/{workout_id}/timer/start", response_model=WorkoutResponse)
async def start_workout_timer(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Start the workout timer."""
    try:
        return await service.start_workout_timer(workout_id, user_id=current_user.id)
    except Exception as e:
        _handle_timer_errors(e)


@router.post("/workouts/{workout_id}/timer/pause", response_model=WorkoutResponse)
async def pause_workout_timer(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Pause the workout timer."""
    try:
        return await service.pause_workout_timer(workout_id, user_id=current_user.id)
    except Exception as e:
        _handle_timer_errors(e)


@router.post("/workouts/{workout_id}/timer/resume", response_model=WorkoutResponse)
async def resume_workout_timer(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Resume a paused workout timer."""
    try:
        return await service.resume_workout_timer(workout_id, user_id=current_user.id)
    except Exception as e:
        _handle_timer_errors(e)


@router.post("/workouts/{workout_id}/timer/stop", response_model=WorkoutResponse)
async def stop_workout_timer(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Stop the workout timer and auto-compute duration."""
    try:
        return await service.stop_workout_timer(workout_id, user_id=current_user.id)
    except Exception as e:
        _handle_timer_errors(e)


# ---------------------------------------
# Workout Templates
# ---------------------------------------


@router.get("/workout-templates", response_model=List[WorkoutTemplateResponse])
async def list_workout_templates(
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get all workout templates for the current user."""
    return await service.list_templates(user_id=current_user.id)


@router.post("/workout-templates", response_model=WorkoutTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_template(
    template: WorkoutTemplateCreate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Create a new workout template."""
    return await service.create_template(template, user_id=current_user.id)


@router.get("/workout-templates/{template_id}", response_model=WorkoutTemplateResponse)
async def get_workout_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Get a specific workout template by ID."""
    try:
        return await service.get_template(template_id, user_id=current_user.id)
    except WorkoutTemplateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FitnessAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/workout-templates/{template_id}", response_model=WorkoutTemplateResponse)
async def update_workout_template(
    template_id: int,
    template_update: WorkoutTemplateUpdate,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Update a workout template."""
    try:
        return await service.update_template(template_id, template_update, user_id=current_user.id)
    except WorkoutTemplateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FitnessAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/workout-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    service: FitnessService = Depends(get_fitness_service),
):
    """Delete a workout template."""
    try:
        await service.delete_template(template_id, user_id=current_user.id)
    except WorkoutTemplateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FitnessAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
