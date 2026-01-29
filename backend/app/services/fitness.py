from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from ..models import Workout, Exercise, WeightEntry, utc_now
from ..schemas import (
    WorkoutCreate,
    WorkoutUpdate,
    WeightEntryCreate,
    WeightEntryUpdate,
    FitnessStatsResponse,
)
from ..repositories.fitness import (
    WorkoutRepository,
    ExerciseRepository,
    WeightEntryRepository,
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


# ---------------------------------------


class FitnessService:
    def __init__(self, db: AsyncSession):
        self.workout_repository = WorkoutRepository(db)
        self.exercise_repository = ExerciseRepository(db)
        self.weight_repository = WeightEntryRepository(db)
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
            completed=True,
        )

        # Add exercises
        for exercise_data in data.exercises:
            exercise = Exercise(
                name=exercise_data.name,
                sets=exercise_data.sets,
                reps=exercise_data.reps,
                weight_kg=exercise_data.weight_kg,
                rest_seconds=exercise_data.rest_seconds,
                notes=exercise_data.notes,
            )
            workout.exercises.append(exercise)

        return await self.workout_repository.create(workout)

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
            # Delete existing exercises
            await self.exercise_repository.delete_by_workout_id(workout_id)

            # Add new exercises
            workout.exercises = []
            for exercise_data in data.exercises:
                exercise = Exercise(
                    workout_id=workout_id,
                    name=exercise_data.name,
                    sets=exercise_data.sets,
                    reps=exercise_data.reps,
                    weight_kg=exercise_data.weight_kg,
                    rest_seconds=exercise_data.rest_seconds,
                    notes=exercise_data.notes,
                )
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
