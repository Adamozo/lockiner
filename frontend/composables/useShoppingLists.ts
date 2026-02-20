import type {
  ShoppingList,
  ShoppingListSummary,
  ShoppingListCreate,
  ShoppingListUpdate,
  ShoppingListItem,
  ShoppingListItemCreate,
  ShoppingListItemUpdate,
  ShoppingItemStatus,
} from '~/types/shopping'

export function useShoppingLists() {
  const api = useApi()

  const lists = ref<ShoppingListSummary[]>([])
  const currentList = ref<ShoppingList | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const BASE = '/api/v1/shopping'

  // ----------------------------------------------------------
  // Lists
  // ----------------------------------------------------------

  const fetchLists = async (status?: string): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const params = status ? `?status=${status}` : ''
      lists.value = await api<ShoppingListSummary[]>(`${BASE}/lists${params}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch lists'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchList = async (listId: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      currentList.value = await api<ShoppingList>(`${BASE}/lists/${listId}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch list'
      throw e
    } finally {
      loading.value = false
    }
  }

  const createList = async (data: ShoppingListCreate): Promise<ShoppingList> => {
    return await api<ShoppingList>(`${BASE}/lists`, { method: 'POST', body: data })
  }

  const updateList = async (listId: number, data: ShoppingListUpdate): Promise<ShoppingList> => {
    const updated = await api<ShoppingList>(`${BASE}/lists/${listId}`, { method: 'PUT', body: data })
    if (currentList.value?.id === listId) currentList.value = updated
    return updated
  }

  const deleteList = async (listId: number): Promise<void> => {
    await api(`${BASE}/lists/${listId}`, { method: 'DELETE' })
    if (currentList.value?.id === listId) currentList.value = null
    lists.value = lists.value.filter(l => l.id !== listId)
  }

  const completeList = async (listId: number): Promise<ShoppingList> => {
    const updated = await api<ShoppingList>(`${BASE}/lists/${listId}/complete`, { method: 'POST' })
    if (currentList.value?.id === listId) currentList.value = updated
    return updated
  }

  // ----------------------------------------------------------
  // Items
  // ----------------------------------------------------------

  const addItem = async (listId: number, data: ShoppingListItemCreate): Promise<ShoppingListItem> => {
    const item = await api<ShoppingListItem>(`${BASE}/lists/${listId}/items`, { method: 'POST', body: data })
    if (currentList.value?.id === listId) {
      currentList.value.items.push(item)
    }
    return item
  }

  const updateItem = async (itemId: number, data: ShoppingListItemUpdate): Promise<ShoppingListItem> => {
    const updated = await api<ShoppingListItem>(`${BASE}/items/${itemId}`, { method: 'PUT', body: data })
    _replaceItem(updated)
    return updated
  }

  const updateItemStatus = async (itemId: number, status: ShoppingItemStatus): Promise<ShoppingListItem> => {
    const updated = await api<ShoppingListItem>(`${BASE}/items/${itemId}/status`, {
      method: 'PATCH',
      body: { status },
    })
    _replaceItem(updated)
    return updated
  }

  const deleteItem = async (itemId: number): Promise<void> => {
    await api(`${BASE}/items/${itemId}`, { method: 'DELETE' })
    if (currentList.value) {
      currentList.value.items = currentList.value.items.filter(i => i.id !== itemId)
    }
  }

  // ----------------------------------------------------------
  // Computed
  // ----------------------------------------------------------

  const pendingItems = computed(() => currentList.value?.items.filter(i => i.status === 'pending') ?? [])
  const inCartItems = computed(() => currentList.value?.items.filter(i => i.status === 'in_cart') ?? [])
  const purchasedItems = computed(() => currentList.value?.items.filter(i => i.status === 'purchased') ?? [])

  const itemsByCategory = computed(() => {
    const items = currentList.value?.items.filter(i => i.status !== 'purchased') ?? []
    const grouped: Record<string, typeof items> = {}
    for (const item of items) {
      const cat = item.category || 'Other'
      if (!grouped[cat]) grouped[cat] = []
      grouped[cat].push(item)
    }
    return grouped
  })

  const progressPercent = computed(() => {
    const total = currentList.value?.items.length ?? 0
    if (total === 0) return 0
    return Math.round((purchasedItems.value.length / total) * 100)
  })

  // ----------------------------------------------------------
  // Helpers
  // ----------------------------------------------------------

  function _replaceItem(updated: ShoppingListItem) {
    if (!currentList.value) return
    const idx = currentList.value.items.findIndex(i => i.id === updated.id)
    if (idx !== -1) currentList.value.items[idx] = updated
  }

  return {
    lists,
    currentList,
    loading,
    error,
    pendingItems,
    inCartItems,
    purchasedItems,
    itemsByCategory,
    progressPercent,
    fetchLists,
    fetchList,
    createList,
    updateList,
    deleteList,
    completeList,
    addItem,
    updateItem,
    updateItemStatus,
    deleteItem,
  }
}
