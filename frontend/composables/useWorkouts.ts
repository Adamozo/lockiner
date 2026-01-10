// Workouts composable with mock data
import type { Workout, WorkoutCreate, FitnessStats } from '~/types/fitness'
import { mockWorkouts } from './useFitnessMockData'

export function useWorkouts() {
  const workouts = ref<Workout[]>([...mockWorkouts])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Generate next ID
  const nextId = computed(() => {
    const maxId = Math.max(...workouts.value.map(w => w.id), 0)
    return maxId + 1
  })

  // Fetch workouts (simulated)
  const fetchWorkouts = async () => {
    loading.value = true
    error.value = null
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300))
      // Data is already loaded from mock
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch workouts'
    } finally {
      loading.value = false
    }
  }

  // Create workout
  const createWorkout = async (workout: WorkoutCreate) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const newWorkout: Workout = {
        id: nextId.value,
        ...workout,
        exercises: workout.exercises.map((e, i) => ({ ...e, id: Date.now() + i })),
        completed: true,
      }
      workouts.value.unshift(newWorkout)
      return newWorkout
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create workout'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Update workout
  const updateWorkout = async (id: number, updates: Partial<WorkoutCreate>) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const index = workouts.value.findIndex(w => w.id === id)
      if (index === -1) throw new Error('Workout not found')

      workouts.value[index] = {
        ...workouts.value[index],
        ...updates,
        exercises: updates.exercises
          ? updates.exercises.map((e, i) => ({ ...e, id: Date.now() + i }))
          : workouts.value[index].exercises,
      }
      return workouts.value[index]
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update workout'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Delete workout
  const deleteWorkout = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const index = workouts.value.findIndex(w => w.id === id)
      if (index === -1) throw new Error('Workout not found')

      workouts.value.splice(index, 1)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete workout'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Get stats
  const stats = computed<FitnessStats>(() => {
    const now = new Date()
    const startOfWeek = new Date(now)
    startOfWeek.setDate(now.getDate() - now.getDay())
    startOfWeek.setHours(0, 0, 0, 0)

    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)

    const workoutsThisWeek = workouts.value.filter(w => new Date(w.date) >= startOfWeek).length
    const workoutsThisMonth = workouts.value.filter(w => new Date(w.date) >= startOfMonth).length

    const totalWeightLifted = workouts.value.reduce((total, workout) => {
      return total + workout.exercises.reduce((sum, ex) => {
        return sum + (ex.weight_kg * ex.sets * ex.reps)
      }, 0)
    }, 0)

    return {
      total_workouts: workouts.value.length,
      workouts_this_week: workoutsThisWeek,
      workouts_this_month: workoutsThisMonth,
      total_weight_lifted_kg: totalWeightLifted,
      current_weight_kg: null,
      weight_change_kg: null,
    }
  })

  // Get recent workouts
  const recentWorkouts = computed(() => {
    return [...workouts.value]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 5)
  })

  return {
    workouts,
    loading,
    error,
    stats,
    recentWorkouts,
    fetchWorkouts,
    createWorkout,
    updateWorkout,
    deleteWorkout,
  }
}
