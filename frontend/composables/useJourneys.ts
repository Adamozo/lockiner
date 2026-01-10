// Learning Journeys composable with mock data
import type { LearningJourney, JourneyCreate, SkillsStats } from '~/types/skills'
import { mockJourneys } from './useSkillsMockData'

export function useJourneys() {
  const journeys = ref<LearningJourney[]>([...mockJourneys])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Generate next ID
  const nextId = computed(() => {
    const maxId = Math.max(...journeys.value.map(j => j.id), 0)
    return maxId + 1
  })

  // Fetch journeys (simulated)
  const fetchJourneys = async () => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))
      // Data is already loaded from mock
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch journeys'
    } finally {
      loading.value = false
    }
  }

  // Create journey
  const createJourney = async (journey: JourneyCreate) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const newJourney: LearningJourney = {
        id: nextId.value,
        name: journey.name,
        description: journey.description,
        category: journey.category,
        status: 'active',
        started_at: new Date().toISOString().split('T')[0],
        target_hours: journey.target_hours,
        logged_hours: 0,
        milestones: (journey.milestones || []).map((title, i) => ({
          id: Date.now() + i,
          title,
          completed: false,
        })),
        icon: getCategoryIcon(journey.category),
        color: getCategoryColor(journey.category),
      }
      journeys.value.unshift(newJourney)
      return newJourney
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create journey'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Update journey
  const updateJourney = async (id: number, updates: Partial<LearningJourney>) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const index = journeys.value.findIndex(j => j.id === id)
      if (index === -1) throw new Error('Journey not found')

      journeys.value[index] = {
        ...journeys.value[index],
        ...updates,
      }
      return journeys.value[index]
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update journey'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Toggle milestone
  const toggleMilestone = async (journeyId: number, milestoneId: number) => {
    const journey = journeys.value.find(j => j.id === journeyId)
    if (!journey) return

    const milestone = journey.milestones.find(m => m.id === milestoneId)
    if (!milestone) return

    milestone.completed = !milestone.completed
    milestone.completed_at = milestone.completed ? new Date().toISOString().split('T')[0] : undefined

    // Check if all milestones completed
    if (journey.milestones.every(m => m.completed)) {
      journey.status = 'completed'
    }
  }

  // Delete journey
  const deleteJourney = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const index = journeys.value.findIndex(j => j.id === id)
      if (index === -1) throw new Error('Journey not found')

      journeys.value.splice(index, 1)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete journey'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Add hours to journey
  const addHours = (journeyId: number, hours: number) => {
    const journey = journeys.value.find(j => j.id === journeyId)
    if (journey) {
      journey.logged_hours += hours
    }
  }

  // Get stats
  const stats = computed<SkillsStats>(() => {
    const totalHours = journeys.value.reduce((sum, j) => sum + j.logged_hours, 0)
    const completedMilestones = journeys.value.reduce(
      (sum, j) => sum + j.milestones.filter(m => m.completed).length,
      0
    )

    return {
      total_journeys: journeys.value.length,
      active_journeys: journeys.value.filter(j => j.status === 'active').length,
      completed_journeys: journeys.value.filter(j => j.status === 'completed').length,
      total_hours_logged: totalHours,
      hours_this_week: 0, // Would calculate from log entries
      completed_milestones: completedMilestones,
    }
  })

  // Active journeys
  const activeJourneys = computed(() =>
    journeys.value.filter(j => j.status === 'active')
  )

  // Get single journey by ID
  const getJourney = (id: number) => {
    return journeys.value.find(j => j.id === id)
  }

  return {
    journeys,
    loading,
    error,
    stats,
    activeJourneys,
    fetchJourneys,
    createJourney,
    updateJourney,
    deleteJourney,
    toggleMilestone,
    addHours,
    getJourney,
  }
}

function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    programming: 'i-heroicons-code-bracket',
    language: 'i-heroicons-language',
    cooking: 'i-heroicons-fire',
    music: 'i-heroicons-musical-note',
    other: 'i-heroicons-academic-cap',
  }
  return icons[category] || icons.other
}

function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    programming: 'cyber-blue',
    language: 'electric-green',
    cooking: 'warning-orange',
    music: 'danger-red',
    other: 'pure-white',
  }
  return colors[category] || colors.other
}
