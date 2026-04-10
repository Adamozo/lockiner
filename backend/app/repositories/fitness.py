from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List

from ..models import Workout, Exercise, ExerciseSet, WeightEntry, UserBodyProfile, BodyMeasurementEntry, WorkoutTemplate, WorkoutTemplateExercise


class WorkoutRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Workout]:
        query = select(Workout).options(
            selectinload(Workout.exercises).selectinload(Exercise.sets_detail)
        ).filter(Workout.user_id == user_id)

        if start_date:
            query = query.filter(Workout.date >= start_date)

        if end_date:
            query = query.filter(Workout.date <= end_date)

        query = query.order_by(Workout.date.desc(), Workout.id.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, workout_id: int) -> Optional[Workout]:
        result = await self.db.execute(
            select(Workout)
            .options(selectinload(Workout.exercises).selectinload(Exercise.sets_detail))
            .filter(Workout.id == workout_id)
        )
        return result.scalar_one_or_none()

    async def create(self, workout: Workout) -> Workout:
        self.db.add(workout)
        await self.db.commit()
        await self.db.refresh(workout)
        # Re-fetch with exercises loaded to avoid lazy loading issues
        return await self.get_by_id(workout.id)

    async def update(self, workout: Workout) -> Workout:
        await self.db.commit()
        await self.db.refresh(workout)
        # Re-fetch with exercises loaded to avoid lazy loading issues
        return await self.get_by_id(workout.id)

    async def delete(self, workout: Workout) -> None:
        await self.db.delete(workout)
        await self.db.commit()

    async def count_by_user(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Workout.id)).filter(Workout.user_id == user_id)
        )
        return result.scalar() or 0

    async def count_by_user_and_date_range(
        self, user_id: int, start_date: str, end_date: str
    ) -> int:
        result = await self.db.execute(
            select(func.count(Workout.id)).filter(
                Workout.user_id == user_id,
                Workout.date >= start_date,
                Workout.date <= end_date,
            )
        )
        return result.scalar() or 0


class ExerciseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_workout_id(self, workout_id: int) -> List[Exercise]:
        result = await self.db.execute(
            select(Exercise).filter(Exercise.workout_id == workout_id)
        )
        return list(result.scalars().all())

    async def create(self, exercise: Exercise) -> Exercise:
        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def delete_by_workout_id(self, workout_id: int) -> None:
        exercises = await self.get_by_workout_id(workout_id)
        for exercise in exercises:
            await self.db.delete(exercise)
        await self.db.commit()

    async def get_total_weight_lifted(self, user_id: int) -> float:
        """Calculate total weight lifted across all exercises for a user.

        For exercises with per-set tracking, use sum(set.weight_kg * set.reps).
        For exercises without per-set tracking, use weight_kg * sets * reps.
        """
        has_sets = (
            select(ExerciseSet.id)
            .where(ExerciseSet.exercise_id == Exercise.id)
            .correlate(Exercise)
            .exists()
        )

        # Sum from per-set data
        sets_result = await self.db.execute(
            select(func.sum(ExerciseSet.weight_kg * ExerciseSet.reps))
            .join(Exercise, ExerciseSet.exercise_id == Exercise.id)
            .join(Workout, Exercise.workout_id == Workout.id)
            .filter(Workout.user_id == user_id)
        )
        sets_total = sets_result.scalar() or 0.0

        # Sum from summary fields (only for exercises WITHOUT sets_detail)
        summary_result = await self.db.execute(
            select(func.sum(Exercise.weight_kg * Exercise.sets * Exercise.reps))
            .join(Workout)
            .filter(Workout.user_id == user_id, ~has_sets)
        )
        summary_total = summary_result.scalar() or 0.0

        return sets_total + summary_total


class WeightEntryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[WeightEntry]:
        query = select(WeightEntry).filter(WeightEntry.user_id == user_id)

        if start_date:
            query = query.filter(WeightEntry.date >= start_date)

        if end_date:
            query = query.filter(WeightEntry.date <= end_date)

        query = query.order_by(WeightEntry.date.desc(), WeightEntry.id.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entry_id: int) -> Optional[WeightEntry]:
        result = await self.db.execute(
            select(WeightEntry).filter(WeightEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_latest(self, user_id: int) -> Optional[WeightEntry]:
        result = await self.db.execute(
            select(WeightEntry)
            .filter(WeightEntry.user_id == user_id)
            .order_by(WeightEntry.date.desc(), WeightEntry.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_oldest(self, user_id: int) -> Optional[WeightEntry]:
        result = await self.db.execute(
            select(WeightEntry)
            .filter(WeightEntry.user_id == user_id)
            .order_by(WeightEntry.date.asc(), WeightEntry.id.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, entry: WeightEntry) -> WeightEntry:
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def update(self, entry: WeightEntry) -> WeightEntry:
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def delete(self, entry: WeightEntry) -> None:
        await self.db.delete(entry)
        await self.db.commit()


class UserBodyProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> Optional[UserBodyProfile]:
        result = await self.db.execute(
            select(UserBodyProfile).filter(UserBodyProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: int, height_cm: Optional[float]) -> UserBodyProfile:
        profile = await self.get_by_user_id(user_id)
        if profile is None:
            profile = UserBodyProfile(user_id=user_id, height_cm=height_cm)
            self.db.add(profile)
        else:
            profile.height_cm = height_cm
        from ..models.base import utc_now
        profile.updated_at = utc_now().isoformat()
        await self.db.commit()
        await self.db.refresh(profile)
        return profile


class BodyMeasurementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[BodyMeasurementEntry]:
        query = select(BodyMeasurementEntry).filter(BodyMeasurementEntry.user_id == user_id)

        if start_date:
            query = query.filter(BodyMeasurementEntry.date >= start_date)

        if end_date:
            query = query.filter(BodyMeasurementEntry.date <= end_date)

        query = query.order_by(BodyMeasurementEntry.date.desc(), BodyMeasurementEntry.id.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, entry_id: int) -> Optional[BodyMeasurementEntry]:
        result = await self.db.execute(
            select(BodyMeasurementEntry).filter(BodyMeasurementEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_latest(self, user_id: int) -> Optional[BodyMeasurementEntry]:
        result = await self.db.execute(
            select(BodyMeasurementEntry)
            .filter(BodyMeasurementEntry.user_id == user_id)
            .order_by(BodyMeasurementEntry.date.desc(), BodyMeasurementEntry.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, entry: BodyMeasurementEntry) -> BodyMeasurementEntry:
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def update(self, entry: BodyMeasurementEntry) -> BodyMeasurementEntry:
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def delete(self, entry: BodyMeasurementEntry) -> None:
        await self.db.delete(entry)
        await self.db.commit()


class WorkoutTemplateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: int) -> List[WorkoutTemplate]:
        result = await self.db.execute(
            select(WorkoutTemplate)
            .options(selectinload(WorkoutTemplate.exercises))
            .filter(WorkoutTemplate.user_id == user_id)
            .order_by(WorkoutTemplate.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, template_id: int) -> Optional[WorkoutTemplate]:
        result = await self.db.execute(
            select(WorkoutTemplate)
            .options(selectinload(WorkoutTemplate.exercises))
            .filter(WorkoutTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def create(self, template: WorkoutTemplate) -> WorkoutTemplate:
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return await self.get_by_id(template.id)

    async def update(self, template: WorkoutTemplate) -> WorkoutTemplate:
        await self.db.commit()
        await self.db.refresh(template)
        return await self.get_by_id(template.id)

    async def delete(self, template: WorkoutTemplate) -> None:
        await self.db.delete(template)
        await self.db.commit()

    async def delete_exercises(self, template_id: int) -> None:
        result = await self.db.execute(
            select(WorkoutTemplateExercise).filter(WorkoutTemplateExercise.template_id == template_id)
        )
        for exercise in result.scalars().all():
            await self.db.delete(exercise)
        await self.db.commit()
