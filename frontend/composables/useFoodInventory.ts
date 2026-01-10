/**
 * Food inventory composable
 * Handles inventory management and expiry reminders
 */

import type {
  FoodInventoryItem,
  FoodInventoryCreate,
  FoodInventoryUpdate,
  FoodInventoryConsumeRequest,
  FoodInventoryStatus,
  FoodInventoryLocation,
  FoodExpiryReminder,
  FoodReminderSettings,
  FoodReminderSettingsUpdate,
  FoodConsumptionLog,
} from '~/types/food'
import { buildQueryParams } from './useApi'

export const useFoodInventory = () => {
  const api = useApi()
  const inventory = ref<FoodInventoryItem[]>([])
  const expiringSoon = ref<FoodInventoryItem[]>([])
  const reminders = ref<FoodExpiryReminder[]>([])
  const reminderSettings = ref<FoodReminderSettings | null>(null)
  const consumptionLogs = ref<FoodConsumptionLog[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // -------------------------------------------------------------------------
  // Inventory
  // -------------------------------------------------------------------------

  /**
   * Fetch inventory with filters
   */
  const fetchInventory = async (
    householdId?: string | null,
    filters?: {
      status?: FoodInventoryStatus
      location?: FoodInventoryLocation
      category_id?: number
      expiring_days?: number
      skip?: number
      limit?: number
    }
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams(filters || {}, householdId)
      const data = await api<FoodInventoryItem[]>(`/api/v1/food/inventory${queryString}`)
      inventory.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch inventory'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch items expiring soon
   */
  const fetchExpiringSoon = async (
    householdId?: string | null,
    days: number = 3
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({ days }, householdId)
      const data = await api<FoodInventoryItem[]>(`/api/v1/food/inventory/expiring${queryString}`)
      expiringSoon.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch expiring items'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Get inventory item by ID
   */
  const getInventoryItem = async (
    itemId: number,
    householdId?: string | null
  ): Promise<FoodInventoryItem> => {
    try {
      const queryString = buildQueryParams({}, householdId)
      return await api<FoodInventoryItem>(`/api/v1/food/inventory/${itemId}${queryString}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch inventory item'
      throw e
    }
  }

  /**
   * Add item to inventory
   */
  const addToInventory = async (
    data: FoodInventoryCreate,
    householdId?: string | null
  ): Promise<FoodInventoryItem> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      const item = await api<FoodInventoryItem>(`/api/v1/food/inventory${queryString}`, {
        method: 'POST',
        body: data,
      })
      inventory.value.unshift(item)
      return item
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add to inventory'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Update inventory item
   */
  const updateInventoryItem = async (
    itemId: number,
    data: FoodInventoryUpdate,
    householdId?: string | null
  ): Promise<FoodInventoryItem> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      const item = await api<FoodInventoryItem>(`/api/v1/food/inventory/${itemId}${queryString}`, {
        method: 'PUT',
        body: data,
      })
      const index = inventory.value.findIndex((i) => i.id === itemId)
      if (index !== -1) {
        inventory.value[index] = item
      }
      return item
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update inventory item'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete inventory item
   */
  const deleteInventoryItem = async (
    itemId: number,
    householdId?: string | null
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      await api(`/api/v1/food/inventory/${itemId}${queryString}`, {
        method: 'DELETE',
      })
      inventory.value = inventory.value.filter((i) => i.id !== itemId)
      expiringSoon.value = expiringSoon.value.filter((i) => i.id !== itemId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete inventory item'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Consume inventory item
   */
  const consumeItem = async (
    itemId: number,
    data: FoodInventoryConsumeRequest,
    householdId?: string | null
  ): Promise<FoodInventoryItem> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      const item = await api<FoodInventoryItem>(
        `/api/v1/food/inventory/${itemId}/consume${queryString}`,
        {
          method: 'POST',
          body: data,
        }
      )
      const index = inventory.value.findIndex((i) => i.id === itemId)
      if (index !== -1) {
        inventory.value[index] = item
      }
      return item
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to consume item'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Mark item as opened
   */
  const openItem = async (
    itemId: number,
    householdId?: string | null
  ): Promise<FoodInventoryItem> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      const item = await api<FoodInventoryItem>(
        `/api/v1/food/inventory/${itemId}/open${queryString}`,
        {
          method: 'POST',
        }
      )
      const index = inventory.value.findIndex((i) => i.id === itemId)
      if (index !== -1) {
        inventory.value[index] = item
      }
      return item
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to open item'
      throw e
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // Reminders
  // -------------------------------------------------------------------------

  /**
   * Fetch pending reminders
   */
  const fetchReminders = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<FoodExpiryReminder[]>('/api/v1/food/reminders')
      reminders.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch reminders'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Dismiss a reminder
   */
  const dismissReminder = async (reminderId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api(`/api/v1/food/reminders/${reminderId}/dismiss`, {
        method: 'POST',
      })
      reminders.value = reminders.value.filter((r) => r.id !== reminderId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to dismiss reminder'
      throw e
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // Reminder Settings
  // -------------------------------------------------------------------------

  /**
   * Fetch reminder settings
   */
  const fetchReminderSettings = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<FoodReminderSettings>('/api/v1/food/settings/reminders')
      reminderSettings.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch reminder settings'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Update reminder settings
   */
  const updateReminderSettings = async (
    data: FoodReminderSettingsUpdate
  ): Promise<FoodReminderSettings> => {
    loading.value = true
    error.value = null

    try {
      const settings = await api<FoodReminderSettings>('/api/v1/food/settings/reminders', {
        method: 'PUT',
        body: data,
      })
      reminderSettings.value = settings
      return settings
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update reminder settings'
      throw e
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // Consumption Logs
  // -------------------------------------------------------------------------

  /**
   * Fetch consumption logs
   */
  const fetchConsumptionLogs = async (params?: {
    start_date?: string
    end_date?: string
    meal_type?: string
    skip?: number
    limit?: number
  }): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams(params || {})
      const data = await api<FoodConsumptionLog[]>(`/api/v1/food/consumption${queryString}`)
      consumptionLogs.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch consumption logs'
      throw e
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // Computed
  // -------------------------------------------------------------------------

  /**
   * Available items count
   */
  const availableCount = computed(() =>
    inventory.value.filter((i) => i.status === 'available' || i.status === 'opened').length
  )

  /**
   * Expiring soon count
   */
  const expiringCount = computed(() => expiringSoon.value.length)

  /**
   * Items by location
   */
  const itemsByLocation = computed(() => {
    const byLocation: Record<FoodInventoryLocation, FoodInventoryItem[]> = {
      fridge: [],
      freezer: [],
      pantry: [],
    }
    for (const item of inventory.value) {
      if (item.status === 'available' || item.status === 'opened') {
        byLocation[item.location].push(item)
      }
    }
    return byLocation
  })

  /**
   * Get days until expiry
   */
  const getDaysUntilExpiry = (item: FoodInventoryItem): number | null => {
    if (!item.expiry_date) return null
    const expiry = new Date(item.expiry_date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const diff = expiry.getTime() - today.getTime()
    return Math.ceil(diff / (1000 * 60 * 60 * 24))
  }

  /**
   * Get expiry status (for styling)
   */
  const getExpiryStatus = (item: FoodInventoryItem): 'ok' | 'warning' | 'danger' | 'expired' => {
    const days = getDaysUntilExpiry(item)
    if (days === null) return 'ok'
    if (days < 0) return 'expired'
    if (days <= 1) return 'danger'
    if (days <= 3) return 'warning'
    return 'ok'
  }

  return {
    // State
    inventory,
    expiringSoon,
    reminders,
    reminderSettings,
    consumptionLogs,
    loading,
    error,
    // Inventory methods
    fetchInventory,
    fetchExpiringSoon,
    getInventoryItem,
    addToInventory,
    updateInventoryItem,
    deleteInventoryItem,
    consumeItem,
    openItem,
    // Reminder methods
    fetchReminders,
    dismissReminder,
    // Settings methods
    fetchReminderSettings,
    updateReminderSettings,
    // Consumption logs
    fetchConsumptionLogs,
    // Computed
    availableCount,
    expiringCount,
    itemsByLocation,
    // Helpers
    getDaysUntilExpiry,
    getExpiryStatus,
  }
}
