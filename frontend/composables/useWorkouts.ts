import type { Workout, WorkoutCreate, WorkoutUpdate, FitnessStats } from '~/types/fitness'
import { buildQueryParams } from './useApi'

interface WorkoutFilters {
  start_date?: string
  end_date?: string
  skip?: number
  limit?: number
}

export function useWorkouts() {
  const api = useApi()
  const workouts = ref<Workout[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Fetch workouts
  const fetchWorkouts = async (filters?: WorkoutFilters): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const queryString = buildQueryParams({
        start_date: filters?.start_date,
        end_date: filters?.end_date,
        skip: filters?.skip,
        limit: filters?.limit,
      })
      const data = await api<Workout[]>(`/api/v1/fitness/workouts${queryString}`)
      workouts.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch workouts'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Create workout
  const createWorkout = async (workout: WorkoutCreate): Promise<Workout> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<Workout>('/api/v1/fitness/workouts', {
        method: 'POST',
        body: workout,
      })
      workouts.value.unshift(data)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create workout'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Update workout
  const updateWorkout = async (id: number, updates: WorkoutUpdate): Promise<Workout> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<Workout>(`/api/v1/fitness/workouts/${id}`, {
        method: 'PUT',
        body: updates,
      })
      const index = workouts.value.findIndex(w => w.id === id)
      if (index !== -1) {
        workouts.value[index] = data
      }
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update workout'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Delete workout
  const deleteWorkout = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await api(`/api/v1/fitness/workouts/${id}`, { method: 'DELETE' })
      workouts.value = workouts.value.filter(w => w.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete workout'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Fetch stats from API
  const fetchStats = async (): Promise<FitnessStats> => {
    const data = await api<FitnessStats>('/api/v1/fitness/stats')
    return data
  }

  // Fetch single workout
  const fetchWorkout = async (id: number): Promise<Workout> => {
    const data = await api<Workout>(`/api/v1/fitness/workouts/${id}`)
    return data
  }

  // Timer actions
  const timerStart = async (id: number): Promise<Workout> => {
    const data = await api<Workout>(`/api/v1/fitness/workouts/${id}/timer/start`, { method: 'POST' })
    const index = workouts.value.findIndex(w => w.id === id)
    if (index !== -1) workouts.value[index] = data
    return data
  }

  const timerPause = async (id: number): Promise<Workout> => {
    const data = await api<Workout>(`/api/v1/fitness/workouts/${id}/timer/pause`, { method: 'POST' })
    const index = workouts.value.findIndex(w => w.id === id)
    if (index !== -1) workouts.value[index] = data
    return data
  }

  const timerResume = async (id: number): Promise<Workout> => {
    const data = await api<Workout>(`/api/v1/fitness/workouts/${id}/timer/resume`, { method: 'POST' })
    const index = workouts.value.findIndex(w => w.id === id)
    if (index !== -1) workouts.value[index] = data
    return data
  }

  const timerStop = async (id: number): Promise<Workout> => {
    const data = await api<Workout>(`/api/v1/fitness/workouts/${id}/timer/stop`, { method: 'POST' })
    const index = workouts.value.findIndex(w => w.id === id)
    if (index !== -1) workouts.value[index] = data
    return data
  }

  // Computed: recent workouts (sorted by date)
  const recentWorkouts = computed(() => {
    return [...workouts.value]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 5)
  })

  // Computed: draft (incomplete) workouts
  const draftWorkouts = computed(() => {
    return workouts.value.filter(w => !w.completed)
  })

  // Computed: completed workouts
  const completedWorkouts = computed(() => {
    return workouts.value.filter(w => w.completed)
  })

  return {
    workouts,
    loading,
    error,
    recentWorkouts,
    draftWorkouts,
    completedWorkouts,
    fetchWorkouts,
    fetchWorkout,
    createWorkout,
    updateWorkout,
    deleteWorkout,
    fetchStats,
    timerStart,
    timerPause,
    timerResume,
    timerStop,
  }
}
