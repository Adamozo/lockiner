import type { WorkoutTemplate, WorkoutTemplateCreate, WorkoutTemplateUpdate } from '~/types/fitness'

export function useWorkoutTemplates() {
  const api = useApi()
  const templates = ref<WorkoutTemplate[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchTemplates = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<WorkoutTemplate[]>('/api/v1/fitness/workout-templates')
      templates.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch templates'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchTemplate = async (id: number): Promise<WorkoutTemplate> => {
    const data = await api<WorkoutTemplate>(`/api/v1/fitness/workout-templates/${id}`)
    return data
  }

  const createTemplate = async (template: WorkoutTemplateCreate): Promise<WorkoutTemplate> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<WorkoutTemplate>('/api/v1/fitness/workout-templates', {
        method: 'POST',
        body: template,
      })
      templates.value.unshift(data)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create template'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateTemplate = async (id: number, updates: WorkoutTemplateUpdate): Promise<WorkoutTemplate> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<WorkoutTemplate>(`/api/v1/fitness/workout-templates/${id}`, {
        method: 'PUT',
        body: updates,
      })
      const index = templates.value.findIndex(t => t.id === id)
      if (index !== -1) {
        templates.value[index] = data
      }
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update template'
      throw e
    } finally {
      loading.value = false
    }
  }

  const deleteTemplate = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await api(`/api/v1/fitness/workout-templates/${id}`, { method: 'DELETE' })
      templates.value = templates.value.filter(t => t.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete template'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    templates,
    loading,
    error,
    fetchTemplates,
    fetchTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
  }
}
