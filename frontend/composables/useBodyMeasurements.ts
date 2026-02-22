import type { UserBodyProfile, BodyMeasurementEntry, BodyMeasurementEntryCreate, BodyMeasurementEntryUpdate } from '~/types/fitness'
import { buildQueryParams } from './useApi'

interface MeasurementFilters {
  start_date?: string
  end_date?: string
  skip?: number
  limit?: number
}

export function useBodyMeasurements() {
  const api = useApi()
  const measurements = ref<BodyMeasurementEntry[]>([])
  const bodyProfile = ref<UserBodyProfile | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Fetch measurements
  const fetchMeasurements = async (filters?: MeasurementFilters): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const queryString = buildQueryParams({
        start_date: filters?.start_date,
        end_date: filters?.end_date,
        skip: filters?.skip,
        limit: filters?.limit,
      })
      const data = await api<BodyMeasurementEntry[]>(`/api/v1/fitness/body-measurements${queryString}`)
      measurements.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch measurements'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Add measurement
  const addMeasurement = async (entry: BodyMeasurementEntryCreate): Promise<BodyMeasurementEntry> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<BodyMeasurementEntry>('/api/v1/fitness/body-measurements', {
        method: 'POST',
        body: entry,
      })
      measurements.value.unshift(data)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add measurement'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Update measurement
  const updateMeasurement = async (id: number, updates: BodyMeasurementEntryUpdate): Promise<BodyMeasurementEntry> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<BodyMeasurementEntry>(`/api/v1/fitness/body-measurements/${id}`, {
        method: 'PUT',
        body: updates,
      })
      const index = measurements.value.findIndex(m => m.id === id)
      if (index !== -1) {
        measurements.value[index] = data
      }
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update measurement'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Delete measurement
  const deleteMeasurement = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await api(`/api/v1/fitness/body-measurements/${id}`, { method: 'DELETE' })
      measurements.value = measurements.value.filter(m => m.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete measurement'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Fetch body profile
  const fetchBodyProfile = async (): Promise<void> => {
    try {
      const data = await api<UserBodyProfile | null>('/api/v1/fitness/body-profile')
      bodyProfile.value = data
    } catch (e) {
      // profile may not exist yet
      bodyProfile.value = null
    }
  }

  // Update body profile
  const updateBodyProfile = async (height_cm: number): Promise<void> => {
    try {
      const data = await api<UserBodyProfile>('/api/v1/fitness/body-profile', {
        method: 'PUT',
        body: { height_cm },
      })
      bodyProfile.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update profile'
      throw e
    }
  }

  // Computed: sorted measurements (newest first)
  const sortedMeasurements = computed(() => {
    return [...measurements.value].sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    )
  })

  // Computed: latest value for each measurement field
  const latestMeasurements = computed(() => {
    const latest: Partial<BodyMeasurementEntry> = {}
    const fields = ['bicep_cm', 'waist_cm', 'thigh_cm', 'calf_cm', 'chest_cm'] as const
    const sorted = sortedMeasurements.value

    for (const field of fields) {
      const entry = sorted.find(m => m[field] != null)
      if (entry) {
        latest[field] = entry[field]
      }
    }

    return latest
  })

  return {
    measurements,
    bodyProfile,
    loading,
    error,
    sortedMeasurements,
    latestMeasurements,
    fetchMeasurements,
    addMeasurement,
    updateMeasurement,
    deleteMeasurement,
    fetchBodyProfile,
    updateBodyProfile,
  }
}
