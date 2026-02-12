import type { ExerciseDefinition, Workout } from '~/types/fitness'

const exerciseLibrary: ExerciseDefinition[] = [
  // Push
  { name: 'Bench Press', category: 'push' },
  { name: 'Incline Bench Press', category: 'push' },
  { name: 'Dumbbell Press', category: 'push' },
  { name: 'Push-ups', category: 'push' },
  { name: 'Shoulder Press', category: 'push' },
  { name: 'Lateral Raise', category: 'push' },
  { name: 'Tricep Pushdown', category: 'push' },
  { name: 'Tricep Dips', category: 'push' },
  // Pull
  { name: 'Barbell Row', category: 'pull' },
  { name: 'Pull-ups', category: 'pull' },
  { name: 'Lat Pulldown', category: 'pull' },
  { name: 'Face Pull', category: 'pull' },
  { name: 'Bicep Curl', category: 'pull' },
  { name: 'Hammer Curl', category: 'pull' },
  { name: 'Cable Row', category: 'pull' },
  { name: 'Dumbbell Row', category: 'pull' },
  // Legs
  { name: 'Squat', category: 'legs' },
  { name: 'Leg Press', category: 'legs' },
  { name: 'Lunges', category: 'legs' },
  { name: 'Leg Extension', category: 'legs' },
  { name: 'Leg Curl', category: 'legs' },
  { name: 'Deadlift', category: 'legs' },
  { name: 'Romanian Deadlift', category: 'legs' },
  { name: 'Calf Raise', category: 'legs' },
  { name: 'Hip Thrust', category: 'legs' },
  // Core
  { name: 'Plank', category: 'core' },
  { name: 'Crunches', category: 'core' },
  { name: 'Russian Twist', category: 'core' },
  { name: 'Hanging Leg Raise', category: 'core' },
  { name: 'Ab Wheel Rollout', category: 'core' },
  // Other
  { name: 'Cardio', category: 'other' },
  { name: 'Stretching', category: 'other' },
]

const categories = ['push', 'pull', 'legs', 'core', 'other'] as const
const categoryLabels: Record<string, string> = {
  push: 'Push',
  pull: 'Pull',
  legs: 'Legs',
  core: 'Core',
  other: 'Other',
}

export function useExerciseLibrary(workouts?: Ref<Workout[]>) {
  const recentExercises = computed(() => {
    if (!workouts?.value?.length) return [] as string[]
    const names = new Set<string>()
    // Get from most recent workouts
    const sorted = [...workouts.value].sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    )
    for (const workout of sorted) {
      for (const exercise of workout.exercises) {
        names.add(exercise.name)
        if (names.size >= 10) break
      }
      if (names.size >= 10) break
    }
    return Array.from(names)
  })

  const search = (query: string) => {
    const q = query.toLowerCase().trim()
    if (!q) {
      // Return grouped by category with recent first
      return {
        recent: recentExercises.value,
        grouped: categories.map(cat => ({
          category: cat,
          label: categoryLabels[cat],
          exercises: exerciseLibrary.filter(e => e.category === cat).map(e => e.name),
        })),
      }
    }

    const matches = exerciseLibrary
      .filter(e => e.name.toLowerCase().includes(q))

    return {
      recent: [] as string[],
      grouped: categories
        .map(cat => ({
          category: cat,
          label: categoryLabels[cat],
          exercises: matches.filter(e => e.category === cat).map(e => e.name),
        }))
        .filter(g => g.exercises.length > 0),
    }
  }

  const allExercises = exerciseLibrary.map(e => e.name)

  return {
    exerciseLibrary,
    categories,
    categoryLabels,
    recentExercises,
    allExercises,
    search,
  }
}
