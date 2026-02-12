/**
 * Composable for managing notification reminder schedules.
 */

export type Frequency = 'daily' | 'weekly' | 'monthly'

export interface NotificationSchedule {
  id: number
  reminder_type: string
  enabled: boolean
  frequency: Frequency
  hour: number
  minute: number
  day_of_week: number | null
  day_of_month: number | null
  custom_name: string | null
  custom_icon: string | null
  custom_title: string | null
  custom_body: string | null
  created_at: string
  updated_at: string | null
}

export interface NotificationScheduleUpdate {
  enabled?: boolean
  frequency?: Frequency
  hour?: number
  minute?: number
  day_of_week?: number | null
  day_of_month?: number | null
}

export interface CustomReminderCreatePayload {
  custom_name: string
  custom_icon: string
  custom_title: string
  custom_body: string
  enabled?: boolean
  frequency?: Frequency
  hour?: number
  minute?: number
  day_of_week?: number | null
  day_of_month?: number | null
}

interface ScheduleListResponse {
  schedules: NotificationSchedule[]
}

export function useNotificationSchedules() {
  const api = useApi()
  const schedules = ref<NotificationSchedule[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchSchedules = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const data = await api<ScheduleListResponse>('/api/v1/settings/notification-schedules')
      schedules.value = data.schedules
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch schedules'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateSchedule = async (
    reminderType: string,
    update: NotificationScheduleUpdate,
  ): Promise<NotificationSchedule> => {
    const data = await api<NotificationSchedule>(
      `/api/v1/settings/notification-schedules/${reminderType}`,
      { method: 'PUT', body: update },
    )
    // Update local state
    const idx = schedules.value.findIndex(s => s.reminder_type === reminderType)
    if (idx !== -1) {
      schedules.value[idx] = data
    }
    return data
  }

  const bulkUpdateSchedules = async (
    updates: Array<{
      reminder_type: string
      enabled: boolean
      frequency: Frequency
      hour: number
      minute: number
      day_of_week?: number | null
      day_of_month?: number | null
      custom_name?: string | null
      custom_icon?: string | null
      custom_title?: string | null
      custom_body?: string | null
    }>,
  ): Promise<void> => {
    const data = await api<ScheduleListResponse>(
      '/api/v1/settings/notification-schedules',
      { method: 'PUT', body: { schedules: updates } },
    )
    schedules.value = data.schedules
  }

  const createCustomReminder = async (
    payload: CustomReminderCreatePayload,
  ): Promise<NotificationSchedule> => {
    const data = await api<NotificationSchedule>(
      '/api/v1/settings/notification-schedules/custom',
      { method: 'POST', body: payload },
    )
    return data
  }

  const deleteCustomReminder = async (reminderType: string): Promise<void> => {
    await api(
      `/api/v1/settings/notification-schedules/${reminderType}`,
      { method: 'DELETE' },
    )
  }

  return {
    schedules,
    loading,
    error,
    fetchSchedules,
    updateSchedule,
    bulkUpdateSchedules,
    createCustomReminder,
    deleteCustomReminder,
  }
}
