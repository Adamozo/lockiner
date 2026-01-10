// Learning Log composable with mock data
import type { LearningLogEntry, LogEntryCreate } from '~/types/skills'
import { mockLogEntries } from './useSkillsMockData'

export function useLearningLog() {
  const entries = ref<LearningLogEntry[]>([...mockLogEntries])
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
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch log entries'
    } finally {
      loading.value = false
    }
  }

  // Add entry
  const addEntry = async (entry: LogEntryCreate, journeyName: string) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const newEntry: LearningLogEntry = {
        id: nextId.value,
        journey_name: journeyName,
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

  // Recent entries (last 5)
  const recentEntries = computed(() => sortedEntries.value.slice(0, 5))

  // Get entries for a specific journey
  const getEntriesForJourney = (journeyId: number) => {
    return entries.value
      .filter(e => e.journey_id === journeyId)
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  // Total hours this week
  const hoursThisWeek = computed(() => {
    const now = new Date()
    const startOfWeek = new Date(now)
    startOfWeek.setDate(now.getDate() - now.getDay())
    startOfWeek.setHours(0, 0, 0, 0)

    const weekEntries = entries.value.filter(e => new Date(e.date) >= startOfWeek)
    return weekEntries.reduce((sum, e) => sum + e.duration_minutes, 0) / 60
  })

  // Total hours logged
  const totalHours = computed(() => {
    return entries.value.reduce((sum, e) => sum + e.duration_minutes, 0) / 60
  })

  return {
    entries,
    loading,
    error,
    sortedEntries,
    recentEntries,
    hoursThisWeek,
    totalHours,
    fetchEntries,
    addEntry,
    deleteEntry,
    getEntriesForJourney,
  }
}
