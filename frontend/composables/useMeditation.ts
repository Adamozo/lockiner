import type { MeditationSession, MeditationSessionCreate, MeditationSessionUpdate, MeditationStats } from '~/types/journal'

export function useMeditation() {
  const api = useApi()
  const sessions = ref<MeditationSession[]>([])
  const activeSession = ref<MeditationSession | null>(null)
  const stats = ref<MeditationStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchSessions = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<MeditationSession[]>('/api/v1/journal/meditation?limit=200')
      sessions.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch sessions'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchActiveSession = async (): Promise<void> => {
    try {
      const data = await api<MeditationSession | null>('/api/v1/journal/meditation/active')
      activeSession.value = data
    } catch {
      activeSession.value = null
    }
  }

  const fetchStats = async (): Promise<void> => {
    try {
      const data = await api<MeditationStats>('/api/v1/journal/meditation/stats')
      stats.value = data
    } catch {
      stats.value = null
    }
  }

  const startSession = async (data: MeditationSessionCreate): Promise<MeditationSession> => {
    loading.value = true
    error.value = null
    try {
      const session = await api<MeditationSession>('/api/v1/journal/meditation', {
        method: 'POST',
        body: data,
      })
      activeSession.value = session
      return session
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to start session'
      throw e
    } finally {
      loading.value = false
    }
  }

  const saveSession = async (id: number, updates: MeditationSessionUpdate): Promise<MeditationSession> => {
    loading.value = true
    error.value = null
    try {
      const session = await api<MeditationSession>(`/api/v1/journal/meditation/${id}`, {
        method: 'PUT',
        body: updates,
      })
      // Update in list
      const idx = sessions.value.findIndex(s => s.id === id)
      if (idx !== -1) sessions.value[idx] = session
      else sessions.value.unshift(session)
      // Clear active if completed
      if (session.completed) activeSession.value = null
      return session
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to save session'
      throw e
    } finally {
      loading.value = false
    }
  }

  const discardSession = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await api(`/api/v1/journal/meditation/${id}`, { method: 'DELETE' })
      sessions.value = sessions.value.filter(s => s.id !== id)
      if (activeSession.value?.id === id) activeSession.value = null
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to discard session'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Computed: only completed sessions for history
  const completedSessions = computed(() =>
    sessions.value.filter(s => s.completed).sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    )
  )

  return {
    sessions,
    activeSession,
    stats,
    loading,
    error,
    completedSessions,
    fetchSessions,
    fetchActiveSession,
    fetchStats,
    startSession,
    saveSession,
    discardSession,
  }
}
