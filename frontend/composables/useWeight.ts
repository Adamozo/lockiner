import type { WeightEntry, WeightEntryCreate, WeightEntryUpdate } from '~/types/fitness'
import { buildQueryParams } from './useApi'

interface WeightFilters {
  start_date?: string
  end_date?: string
  skip?: number
  limit?: number
}

export function useWeight() {
  const api = useApi()
  const entries = ref<WeightEntry[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Fetch entries
  const fetchEntries = async (filters?: WeightFilters): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const queryString = buildQueryParams({
        start_date: filters?.start_date,
        end_date: filters?.end_date,
        skip: filters?.skip,
        limit: filters?.limit,
      })
      const data = await api<WeightEntry[]>(`/api/v1/fitness/weight-entries${queryString}`)
      entries.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch weight entries'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Add entry
  const addEntry = async (entry: WeightEntryCreate): Promise<WeightEntry> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<WeightEntry>('/api/v1/fitness/weight-entries', {
        method: 'POST',
        body: entry,
      })
      entries.value.unshift(data)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Update entry
  const updateEntry = async (id: number, updates: WeightEntryUpdate): Promise<WeightEntry> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<WeightEntry>(`/api/v1/fitness/weight-entries/${id}`, {
        method: 'PUT',
        body: updates,
      })
      const index = entries.value.findIndex(e => e.id === id)
      if (index !== -1) {
        entries.value[index] = data
      }
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Delete entry
  const deleteEntry = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await api(`/api/v1/fitness/weight-entries/${id}`, { method: 'DELETE' })
      entries.value = entries.value.filter(e => e.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Computed properties
  const sortedEntries = computed(() => {
    return [...entries.value].sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    )
  })

  const currentWeight = computed(() => {
    if (sortedEntries.value.length === 0) return null
    return sortedEntries.value[0].weight_kg
  })

  const weightChange = computed(() => {
    if (sortedEntries.value.length < 2) return null
    const oldest = sortedEntries.value[sortedEntries.value.length - 1]
    const newest = sortedEntries.value[0]
    return newest.weight_kg - oldest.weight_kg
  })

  const chartData = computed(() => {
    const sorted = [...entries.value].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    )
    return {
      labels: sorted.map(e => e.date),
      weights: sorted.map(e => e.weight_kg),
      bodyFat: sorted.map(e => e.body_fat_percentage || null),
    }
  })

  return {
    entries,
    loading,
    error,
    sortedEntries,
    currentWeight,
    weightChange,
    chartData,
    fetchEntries,
    addEntry,
    updateEntry,
    deleteEntry,
  }
}
