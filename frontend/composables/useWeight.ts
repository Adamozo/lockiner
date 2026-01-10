// Weight tracking composable with mock data
import type { WeightEntry, WeightEntryCreate } from '~/types/fitness'
import { mockWeightEntries } from './useFitnessMockData'

export function useWeight() {
  const entries = ref<WeightEntry[]>([...mockWeightEntries])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Generate next ID
  const nextId = computed(() => {
    const maxId = Math.max(...entries.value.map(e => e.id), 0)
    return maxId + 1
  })

  // Fetch entries (simulated)
  const fetchEntries = async () => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))
      // Data is already loaded from mock
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch weight entries'
    } finally {
      loading.value = false
    }
  }

  // Add entry
  const addEntry = async (entry: WeightEntryCreate) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const newEntry: WeightEntry = {
        id: nextId.value,
        ...entry,
      }
      entries.value.unshift(newEntry)
      return newEntry
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Update entry
  const updateEntry = async (id: number, updates: Partial<WeightEntryCreate>) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const index = entries.value.findIndex(e => e.id === id)
      if (index === -1) throw new Error('Entry not found')

      entries.value[index] = {
        ...entries.value[index],
        ...updates,
      }
      return entries.value[index]
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Delete entry
  const deleteEntry = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const index = entries.value.findIndex(e => e.id === id)
      if (index === -1) throw new Error('Entry not found')

      entries.value.splice(index, 1)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Sorted entries by date (newest first)
  const sortedEntries = computed(() => {
    return [...entries.value].sort((a, b) =>
      new Date(b.date).getTime() - new Date(a.date).getTime()
    )
  })

  // Current weight (latest entry)
  const currentWeight = computed(() => {
    if (sortedEntries.value.length === 0) return null
    return sortedEntries.value[0].weight_kg
  })

  // Weight change (from oldest to newest in dataset)
  const weightChange = computed(() => {
    if (sortedEntries.value.length < 2) return null
    const oldest = sortedEntries.value[sortedEntries.value.length - 1]
    const newest = sortedEntries.value[0]
    return newest.weight_kg - oldest.weight_kg
  })

  // Chart data for weight over time
  const chartData = computed(() => {
    const sorted = [...entries.value].sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
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
