import type {
  JournalEntry,
  JournalEntryCreate,
  JournalEntryUpdate,
  JournalStats,
  JournalReport,
  ReportGenerateRequest,
} from '~/types/journal'
import { buildQueryParams } from './useApi'

interface EntryFilters {
  start_date?: string
  end_date?: string
  skip?: number
  limit?: number
}

export function useJournal() {
  const api = useApi()
  const entries = ref<JournalEntry[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchEntries = async (filters?: EntryFilters): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const queryString = buildQueryParams({
        start_date: filters?.start_date,
        end_date: filters?.end_date,
        skip: filters?.skip,
        limit: filters?.limit,
      })
      const data = await api<JournalEntry[]>(`/api/v1/journal/entries${queryString}`)
      entries.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch entries'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchEntryByDate = async (date: string): Promise<JournalEntry> => {
    const data = await api<JournalEntry>(`/api/v1/journal/entries/date/${date}`)
    return data
  }

  const fetchEntry = async (id: number): Promise<JournalEntry> => {
    const data = await api<JournalEntry>(`/api/v1/journal/entries/${id}`)
    return data
  }

  const createEntry = async (entry: JournalEntryCreate): Promise<JournalEntry> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<JournalEntry>('/api/v1/journal/entries', {
        method: 'POST',
        body: entry,
      })
      entries.value.unshift(data)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateEntry = async (id: number, updates: JournalEntryUpdate): Promise<JournalEntry> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<JournalEntry>(`/api/v1/journal/entries/${id}`, {
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

  const deleteEntry = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await api(`/api/v1/journal/entries/${id}`, { method: 'DELETE' })
      entries.value = entries.value.filter(e => e.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete entry'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchStats = async (): Promise<JournalStats> => {
    return await api<JournalStats>('/api/v1/journal/stats')
  }

  const generateReport = async (request: ReportGenerateRequest): Promise<JournalReport> => {
    return await api<JournalReport>('/api/v1/journal/reports/generate', {
      method: 'POST',
      body: request,
    })
  }

  const fetchReport = async (reportType: string, period: string): Promise<JournalReport> => {
    return await api<JournalReport>(`/api/v1/journal/reports/${reportType}/${period}`)
  }

  const fetchReports = async (reportType: string): Promise<JournalReport[]> => {
    return await api<JournalReport[]>(`/api/v1/journal/reports/${reportType}`)
  }

  const recentEntries = computed(() => {
    return [...entries.value]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 5)
  })

  return {
    entries,
    loading,
    error,
    recentEntries,
    fetchEntries,
    fetchEntry,
    fetchEntryByDate,
    createEntry,
    updateEntry,
    deleteEntry,
    fetchStats,
    generateReport,
    fetchReport,
    fetchReports,
  }
}
