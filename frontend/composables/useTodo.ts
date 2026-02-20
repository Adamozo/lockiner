import type {
  TodoList,
  TodoListSummary,
  TodoListCreate,
  TodoListUpdate,
  TodoItem,
  TodoItemCreate,
  TodoItemUpdate,
  TodoPostponeRequest,
  TodoNotificationRule,
  TodoNotificationRuleCreate,
  TodoNotificationRuleUpdate,
  TodoStats,
} from '~/types/todo'

export function useTodo() {
  const api = useApi()

  const currentList = ref<TodoList | null>(null)
  const lists = ref<TodoListSummary[]>([])
  const notificationRules = ref<TodoNotificationRule[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const BASE = '/api/v1/todo'

  // ----------------------------------------------------------
  // Lists
  // ----------------------------------------------------------

  const fetchListsRange = async (dateFrom: string, dateTo: string): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      lists.value = await api<TodoListSummary[]>(`${BASE}/lists?date_from=${dateFrom}&date_to=${dateTo}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch lists'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchListByDate = async (date: string): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      currentList.value = await api<TodoList | null>(`${BASE}/lists/date/${date}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch list'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchList = async (listId: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      currentList.value = await api<TodoList>(`${BASE}/lists/${listId}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch list'
      throw e
    } finally {
      loading.value = false
    }
  }

  const createList = async (data: TodoListCreate): Promise<TodoList> => {
    loading.value = true
    error.value = null
    try {
      const created = await api<TodoList>(`${BASE}/lists`, { method: 'POST', body: data })
      currentList.value = created
      return created
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create list'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateList = async (listId: number, data: TodoListUpdate): Promise<TodoList> => {
    const updated = await api<TodoList>(`${BASE}/lists/${listId}`, { method: 'PUT', body: data })
    if (currentList.value?.id === listId) currentList.value = updated
    return updated
  }

  const deleteList = async (listId: number): Promise<void> => {
    await api(`${BASE}/lists/${listId}`, { method: 'DELETE' })
    if (currentList.value?.id === listId) currentList.value = null
    lists.value = lists.value.filter(l => l.id !== listId)
  }

  // ----------------------------------------------------------
  // Items
  // ----------------------------------------------------------

  const addItem = async (listId: number, data: TodoItemCreate): Promise<TodoItem> => {
    const item = await api<TodoItem>(`${BASE}/lists/${listId}/items`, { method: 'POST', body: data })
    if (currentList.value?.id === listId) {
      currentList.value.items.push(item)
    }
    return item
  }

  const updateItem = async (itemId: number, data: TodoItemUpdate): Promise<TodoItem> => {
    const updated = await api<TodoItem>(`${BASE}/items/${itemId}`, { method: 'PUT', body: data })
    _replaceItem(updated)
    return updated
  }

  const deleteItem = async (itemId: number): Promise<void> => {
    await api(`${BASE}/items/${itemId}`, { method: 'DELETE' })
    if (currentList.value) {
      currentList.value.items = currentList.value.items.filter(i => i.id !== itemId)
    }
  }

  const completeItem = async (itemId: number, completed: boolean): Promise<TodoItem> => {
    const updated = await api<TodoItem>(`${BASE}/items/${itemId}/complete?completed=${completed}`, {
      method: 'PATCH',
    })
    _replaceItem(updated)
    return updated
  }

  const postponeItem = async (itemId: number, data: TodoPostponeRequest): Promise<TodoItem> => {
    const updated = await api<TodoItem>(`${BASE}/items/${itemId}/postpone`, {
      method: 'POST',
      body: data,
    })
    // Remove from current list (moved to another day)
    if (currentList.value && data.to_date && data.to_date !== currentList.value.date) {
      currentList.value.items = currentList.value.items.filter(i => i.id !== itemId)
    } else {
      _replaceItem(updated)
    }
    return updated
  }

  // ----------------------------------------------------------
  // Notification rules
  // ----------------------------------------------------------

  const fetchNotificationRules = async (): Promise<void> => {
    notificationRules.value = await api<TodoNotificationRule[]>(`${BASE}/notification-rules`)
  }

  const createNotificationRule = async (data: TodoNotificationRuleCreate): Promise<TodoNotificationRule> => {
    const rule = await api<TodoNotificationRule>(`${BASE}/notification-rules`, {
      method: 'POST',
      body: data,
    })
    notificationRules.value.push(rule)
    return rule
  }

  const updateNotificationRule = async (ruleId: number, data: TodoNotificationRuleUpdate): Promise<TodoNotificationRule> => {
    const updated = await api<TodoNotificationRule>(`${BASE}/notification-rules/${ruleId}`, {
      method: 'PUT',
      body: data,
    })
    const idx = notificationRules.value.findIndex(r => r.id === ruleId)
    if (idx !== -1) notificationRules.value[idx] = updated
    return updated
  }

  const deleteNotificationRule = async (ruleId: number): Promise<void> => {
    await api(`${BASE}/notification-rules/${ruleId}`, { method: 'DELETE' })
    notificationRules.value = notificationRules.value.filter(r => r.id !== ruleId)
  }

  // ----------------------------------------------------------
  // Stats
  // ----------------------------------------------------------

  const fetchStats = async (days = 30): Promise<TodoStats> => {
    return await api<TodoStats>(`${BASE}/stats?days=${days}`)
  }

  // ----------------------------------------------------------
  // Computed
  // ----------------------------------------------------------

  const completedItems = computed(() => currentList.value?.items.filter(i => i.completed) ?? [])
  const pendingItems = computed(() => currentList.value?.items.filter(i => !i.completed) ?? [])

  const completionProgress = computed(() => {
    const total = currentList.value?.items.length ?? 0
    if (total === 0) return 100
    return Math.round((completedItems.value.length / total) * 100)
  })

  const estimatedMinutesRemaining = computed(() =>
    pendingItems.value.reduce((sum, i) => sum + (i.estimated_minutes ?? 0), 0)
  )

  // ----------------------------------------------------------
  // Helpers
  // ----------------------------------------------------------

  function _replaceItem(updated: TodoItem) {
    if (!currentList.value) return
    const idx = currentList.value.items.findIndex(i => i.id === updated.id)
    if (idx !== -1) currentList.value.items[idx] = updated
  }

  return {
    currentList,
    lists,
    notificationRules,
    loading,
    error,
    completedItems,
    pendingItems,
    completionProgress,
    estimatedMinutesRemaining,
    fetchListsRange,
    fetchListByDate,
    fetchList,
    createList,
    updateList,
    deleteList,
    addItem,
    updateItem,
    deleteItem,
    completeItem,
    postponeItem,
    fetchNotificationRules,
    createNotificationRule,
    updateNotificationRule,
    deleteNotificationRule,
    fetchStats,
  }
}
