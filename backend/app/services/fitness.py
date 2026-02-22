from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from ..models import Workout, Exercise, ExerciseSet, WeightEntry, UserBodyProfile, BodyMeasurementEntry, utc_now
from ..schemas import (
    WorkoutCreate,
    WorkoutUpdate,
    WeightEntryCreate,
    WeightEntryUpdate,
    FitnessStatsResponse,
    UserBodyProfileUpdate,
    BodyMeasurementEntryCreate,
    BodyMeasurementEntryUpdate,
)
from ..repositories.fitness import (
    WorkoutRepository,
    ExerciseRepository,
    WeightEntryRepository,
    UserBodyProfileRepository,
    BodyMeasurementRepository,
)

# ---------------------------------------


class WorkoutNotFoundError(Exception):
    def __init__(self, workout_id: int):
        self.workout_id = workout_id
        super().__init__(f"Workout {workout_id} not found")


class WeightEntryNotFoundError(Exception):
    def __init__(self, entry_id: int):
        self.entry_id = entry_id
        super().__init__(f"Weight entry {entry_id} not found")


class FitnessAccessDeniedError(Exception):
    def __init__(self, resource_type: str, resource_id: int):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"Access denied to {resource_type} {resource_id}")


class BodyMeasurementNotFoundError(Exception):
    def __init__(self, entry_id: int):
        self.entry_id = entry_id
        super().__init__(f"Body measurement entry {entry_id} not found")


class WorkoutTimerError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


# ---------------------------------------


class FitnessService:
    def __init__(self, db: AsyncSession):
        self.workout_repository = WorkoutRepository(db)
        self.exercise_repository = ExerciseRepository(db)
        self.weight_repository = WeightEntryRepository(db)
        self.body_profile_repository = UserBodyProfileRepository(db)
        self.body_measurement_repository = BodyMeasurementRepository(db)
        self.db = db

    # --- Workouts ---

    async def list_workouts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Workout]:
        return await self.workout_repository.get_all(
            user_id=user_id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_workout(self, workout_id: int, user_id: int) -> Workout:
        workout = await self.workout_repository.get_by_id(workout_id)
        if workout is None:
            raise WorkoutNotFoundError(workout_id)

        if workout.user_id != user_id:
            raise FitnessAccessDeniedError("workout", workout_id)

        return workout

    async def create_workout(self, data: WorkoutCreate, user_id: int) -> Workout:
        workout = Workout(
            user_id=user_id,
            date=data.date,
            name=data.name,
            duration_minutes=data.duration_minutes,
            notes=data.notes,
            completed=data.completed if data.completed is not None else True,
        )

        # Add exercises
        for exercise_data in data.exercises:
            exercise = self._build_exercise(exercise_data)
            workout.exercises.append(exercise)

        return await self.workout_repository.create(workout)

    @staticmethod
    def _build_exercise(exercise_data) -> Exercise:
        """Build an Exercise (with optional sets_detail) from schema data."""
        sets_val = exercise_data.sets
        reps_val = exercise_data.reps
        weight_val = exercise_data.weight_kg

        exercise = Exercise(
            name=exercise_data.name,
            sets=sets_val,
            reps=reps_val,
            weight_kg=weight_val,
            rest_seconds=exercise_data.rest_seconds,
            notes=exercise_data.notes,
        )

        if exercise_data.sets_detail:
            for set_data in exercise_data.sets_detail:
                exercise.sets_detail.append(
                    ExerciseSet(
                        set_number=set_data.set_number,
                        reps=set_data.reps,
                        weight_kg=set_data.weight_kg,
                        completed=set_data.completed,
                    )
                )
            # Auto-compute summary fields from sets_detail
            exercise.sets = len(exercise_data.sets_detail)
            exercise.reps = max(s.reps for s in exercise_data.sets_detail)
            exercise.weight_kg = max(s.weight_kg for s in exercise_data.sets_detail)

        return exercise

    async def update_workout(
        self, workout_id: int, data: WorkoutUpdate, user_id: int
    ) -> Workout:
        workout = await self.workout_repository.get_by_id(workout_id)
        if workout is None:
            raise WorkoutNotFoundError(workout_id)

        if workout.user_id != user_id:
            raise FitnessAccessDeniedError("workout", workout_id)

        update_data = data.model_dump(exclude_unset=True, exclude={"exercises"})
        for field, value in update_data.items():
            setattr(workout, field, value)

        workout.updated_at = utc_now().isoformat()

        # Update exercises if provided
        if data.exercises is not None:
            # Delete existing exercises (cascade deletes their sets_detail)
            await self.exercise_repository.delete_by_workout_id(workout_id)

            # Add new exercises
            workout.exercises = []
            for exercise_data in data.exercises:
                exercise = self._build_exercise(exercise_data)
                exercise.workout_id = workout_id
                workout.exercises.append(exercise)

        return await self.workout_repository.update(workout)

    async def delete_workout(self, workout_id: int, user_id: int) -> None:
        workout = await self.workout_repository.get_by_id(workout_id)
        if workout is None:
            raise WorkoutNotFoundError(workout_id)

        if workout.user_id != user_id:
            raise FitnessAccessDeniedError("workout", workout_id)

        await self.workout_repository.delete(workout)

    # --- Weight Entries ---

    async def list_weight_entries(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[WeightEntry]:
        return await self.weight_repository.get_all(
            user_id=user_id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_weight_entry(self, entry_id: int, user_id: int) -> WeightEntry:
        entry = await self.weight_repository.get_by_id(entry_id)
        if entry is None:
            raise WeightEntryNotFoundError(entry_id)

        if entry.user_id != user_id:
            raise FitnessAccessDeniedError("weight_entry", entry_id)

        return entry

    async def create_weight_entry(
        self, data: WeightEntryCreate, user_id: int
    ) -> WeightEntry:
        entry = WeightEntry(
            user_id=user_id,
            date=data.date,
            weight_kg=data.weight_kg,
            body_fat_percentage=data.body_fat_percentage,
            notes=data.notes,
        )
        return await self.weight_repository.create(entry)

    async def update_weight_entry(
        self, entry_id: int, data: WeightEntryUpdate, user_id: int
    ) -> WeightEntry:
        entry = await self.weight_repository.get_by_id(entry_id)
        if entry is None:
            raise WeightEntryNotFoundError(entry_id)

        if entry.user_id != user_id:
            raise FitnessAccessDeniedError("weight_entry", entry_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)

        return await self.weight_repository.update(entry)

    async def delete_weight_entry(self, entry_id: int, user_id: int) -> None:
        entry = await self.weight_repository.get_by_id(entry_id)
        if entry is None:
            raise WeightEntryNotFoundError(entry_id)

        if entry.user_id != user_id:
            raise FitnessAccessDeniedError("weight_entry", entry_id)

        await self.weight_repository.delete(entry)

    # --- Stats ---

    async def get_fitness_stats(self, user_id: int) -> FitnessStatsResponse:
        # Get current date info
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")

        # Calculate week start (Monday)
        week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")

        # Calculate month start
        month_start = now.strftime("%Y-%m-01")

        # Get workout counts
        total_workouts = await self.workout_repository.count_by_user(user_id)
        workouts_this_week = await self.workout_repository.count_by_user_and_date_range(
            user_id, week_start, today
        )
        workouts_this_month = await self.workout_repository.count_by_user_and_date_range(
            user_id, month_start, today
        )

        # Get total weight lifted
        total_weight_lifted = await self.exercise_repository.get_total_weight_lifted(user_id)

        # Get weight info
        latest_weight = await self.weight_repository.get_latest(user_id)
        oldest_weight = await self.weight_repository.get_oldest(user_id)

        current_weight_kg = latest_weight.weight_kg if latest_weight else None
        weight_change_kg = None

        if latest_weight and oldest_weight and latest_weight.id != oldest_weight.id:
            weight_change_kg = latest_weight.weight_kg - oldest_weight.weight_kg

        return FitnessStatsResponse(
            total_workouts=total_workouts,
            workouts_this_week=workouts_this_week,
            workouts_this_month=workouts_this_month,
            total_weight_lifted_kg=total_weight_lifted,
            current_weight_kg=current_weight_kg,
            weight_change_kg=weight_change_kg,
        )

    # --- Body Profile ---

    async def get_body_profile(self, user_id: int) -> Optional[UserBodyProfile]:
        return await self.body_profile_repository.get_by_user_id(user_id)

    async def upsert_body_profile(self, user_id: int, data: UserBodyProfileUpdate) -> UserBodyProfile:
        return await self.body_profile_repository.upsert(user_id, data.height_cm)

    # --- Body Measurements ---

    async def list_body_measurements(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[BodyMeasurementEntry]:
        return await self.body_measurement_repository.get_all(
            user_id=user_id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_body_measurement(self, entry_id: int, user_id: int) -> BodyMeasurementEntry:
        entry = await self.body_measurement_repository.get_by_id(entry_id)
        if entry is None:
            raise BodyMeasurementNotFoundError(entry_id)
        if entry.user_id != user_id:
            raise FitnessAccessDeniedError("body_measurement", entry_id)
        return entry

    async def create_body_measurement(
        self, data: BodyMeasurementEntryCreate, user_id: int
    ) -> BodyMeasurementEntry:
        entry = BodyMeasurementEntry(
            user_id=user_id,
            date=data.date,
            bicep_cm=data.bicep_cm,
            waist_cm=data.waist_cm,
            thigh_cm=data.thigh_cm,
            calf_cm=data.calf_cm,
            chest_cm=data.chest_cm,
            notes=data.notes,
        )
        return await self.body_measurement_repository.create(entry)

    async def update_body_measurement(
        self, entry_id: int, data: BodyMeasurementEntryUpdate, user_id: int
    ) -> BodyMeasurementEntry:
        entry = await self.body_measurement_repository.get_by_id(entry_id)
        if entry is None:
            raise BodyMeasurementNotFoundError(entry_id)
        if entry.user_id != user_id:
            raise FitnessAccessDeniedError("body_measurement", entry_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)

        return await self.body_measurement_repository.update(entry)

    async def delete_body_measurement(self, entry_id: int, user_id: int) -> None:
        entry = await self.body_measurement_repository.get_by_id(entry_id)
        if entry is None:
            raise BodyMeasurementNotFoundError(entry_id)
        if entry.user_id != user_id:
            raise FitnessAccessDeniedError("body_measurement", entry_id)
        await self.body_measurement_repository.delete(entry)

    # --- Workout Timer ---

    @staticmethod
    def _parse_iso(s: str) -> datetime:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))

    async def _get_timer_workout(self, workout_id: int, user_id: int) -> Workout:
        workout = await self.workout_repository.get_by_id(workout_id)
        if workout is None:
            raise WorkoutNotFoundError(workout_id)
        if workout.user_id != user_id:
            raise FitnessAccessDeniedError("workout", workout_id)
        if workout.completed:
            raise WorkoutTimerError("Cannot modify timer for a completed workout")
        return workout

    async def start_workout_timer(self, workout_id: int, user_id: int) -> Workout:
        workout = await self._get_timer_workout(workout_id, user_id)
        now = utc_now()
        workout.timer_started_at = now.isoformat()
        workout.timer_paused_at = None
        workout.timer_ended_at = None
        workout.total_paused_seconds = 0
        return await self.workout_repository.update(workout)

    async def pause_workout_timer(self, workout_id: int, user_id: int) -> Workout:
        workout = await self._get_timer_workout(workout_id, user_id)
        if workout.timer_started_at is None:
            raise WorkoutTimerError("Timer has not been started")
        if workout.timer_paused_at is not None:
            raise WorkoutTimerError("Timer is already paused")
        workout.timer_paused_at = utc_now().isoformat()
        return await self.workout_repository.update(workout)

    async def resume_workout_timer(self, workout_id: int, user_id: int) -> Workout:
        workout = await self._get_timer_workout(workout_id, user_id)
        if workout.timer_paused_at is None:
            raise WorkoutTimerError("Timer is not paused")
        paused_at = self._parse_iso(workout.timer_paused_at)
        paused_duration = int((utc_now() - paused_at).total_seconds())
        workout.total_paused_seconds = (workout.total_paused_seconds or 0) + paused_duration
        workout.timer_paused_at = None
        return await self.workout_repository.update(workout)

    async def stop_workout_timer(self, workout_id: int, user_id: int) -> Workout:
        workout = await self._get_timer_workout(workout_id, user_id)
        if workout.timer_started_at is None:
            raise WorkoutTimerError("Timer has not been started")
        now = utc_now()
        if workout.timer_paused_at is not None:
            paused_at = self._parse_iso(workout.timer_paused_at)
            paused_duration = int((now - paused_at).total_seconds())
            workout.total_paused_seconds = (workout.total_paused_seconds or 0) + paused_duration
            workout.timer_paused_at = None
        workout.timer_ended_at = now.isoformat()
        started = self._parse_iso(workout.timer_started_at)
        total_seconds = int((now - started).total_seconds())
        active_seconds = max(0, total_seconds - (workout.total_paused_seconds or 0))
        workout.duration_minutes = max(1, round(active_seconds / 60))
        return await self.workout_repository.update(workout)
