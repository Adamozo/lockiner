/**
 * Food import composable
 * Handles pending imports from receipts
 */

import type {
  FoodPendingImport,
  FoodPendingImportItemAccept,
  FoodInventoryItem,
} from '~/types/food'
import { buildQueryParams } from './useApi'

export const useFoodImport = () => {
  const api = useApi()
  const pendingImports = ref<FoodPendingImport[]>([])
  const currentImport = ref<FoodPendingImport | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Fetch pending imports
   */
  const fetchPendingImports = async (
    householdId?: string | null,
    status?: string
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({ status }, householdId)
      const data = await api<FoodPendingImport[]>(`/api/v1/food/pending-imports${queryString}`)
      pendingImports.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch pending imports'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Get pending import by ID
   */
  const getPendingImport = async (
    importId: number,
    householdId?: string | null
  ): Promise<FoodPendingImport> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      const data = await api<FoodPendingImport>(`/api/v1/food/pending-imports/${importId}${queryString}`)
      currentImport.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch pending import'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Accept a pending import item
   */
  const acceptItem = async (
    importId: number,
    itemId: number,
    data: FoodPendingImportItemAccept,
    householdId?: string | null
  ): Promise<FoodInventoryItem> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      const inventoryItem = await api<FoodInventoryItem>(
        `/api/v1/food/pending-imports/${importId}/items/${itemId}/accept${queryString}`,
        {
          method: 'POST',
          body: data,
        }
      )

      // Update local state
      if (currentImport.value && currentImport.value.id === importId) {
        const item = currentImport.value.items.find((i) => i.id === itemId)
        if (item) {
          item.status = 'accepted'
          item.final_product_id = inventoryItem.product_id
          item.final_quantity = inventoryItem.quantity
          item.final_unit = inventoryItem.unit
          item.final_expiry_date = inventoryItem.expiry_date ?? null
        }
        // Update import status
        updateImportStatus(currentImport.value)
      }

      return inventoryItem
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to accept item'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Reject a pending import item
   */
  const rejectItem = async (
    importId: number,
    itemId: number,
    householdId?: string | null
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams({}, householdId)
      await api(`/api/v1/food/pending-imports/${importId}/items/${itemId}/reject${queryString}`, {
        method: 'POST',
      })

      // Update local state
      if (currentImport.value && currentImport.value.id === importId) {
        const item = currentImport.value.items.find((i) => i.id === itemId)
        if (item) {
          item.status = 'rejected'
        }
        // Update import status
        updateImportStatus(currentImport.value)
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to reject item'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Accept all matched items in a pending import
   */
  const acceptAllMatched = async (
    importId: number,
    householdId?: string | null
  ): Promise<FoodInventoryItem[]> => {
    if (!currentImport.value || currentImport.value.id !== importId) {
      await getPendingImport(importId, householdId)
    }

    const results: FoodInventoryItem[] = []

    for (const item of currentImport.value!.items) {
      if (item.status === 'pending' && item.matched_product_id) {
        try {
          const inventoryItem = await acceptItem(
            importId,
            item.id,
            {
              final_product_id: item.matched_product_id,
              final_expiry_date: item.suggested_expiry_date ?? undefined,
              final_quantity: item.quantity ?? 1,
            },
            householdId
          )
          results.push(inventoryItem)
        } catch (e) {
          console.error(`Failed to accept item ${item.id}:`, e)
        }
      }
    }

    return results
  }

  /**
   * Update import status based on items
   */
  const updateImportStatus = (pendingImport: FoodPendingImport): void => {
    const items = pendingImport.items
    if (!items.length) return

    const pendingCount = items.filter((i) => i.status === 'pending').length
    const acceptedCount = items.filter((i) => i.status === 'accepted').length
    const rejectedCount = items.filter((i) => i.status === 'rejected').length

    if (pendingCount === 0) {
      if (acceptedCount > 0 && rejectedCount > 0) {
        pendingImport.status = 'partially_accepted'
      } else if (acceptedCount > 0) {
        pendingImport.status = 'accepted'
      } else {
        pendingImport.status = 'rejected'
      }
    }
  }

  // -------------------------------------------------------------------------
  // Computed
  // -------------------------------------------------------------------------

  /**
   * Pending items count
   */
  const pendingItemsCount = computed(() => {
    if (!currentImport.value) return 0
    return currentImport.value.items.filter((i) => i.status === 'pending').length
  })

  /**
   * Matched items count (items with auto-matched products)
   */
  const matchedItemsCount = computed(() => {
    if (!currentImport.value) return 0
    return currentImport.value.items.filter(
      (i) => i.status === 'pending' && i.matched_product_id
    ).length
  })

  /**
   * Unmatched items count (items needing manual input)
   */
  const unmatchedItemsCount = computed(() => {
    if (!currentImport.value) return 0
    return currentImport.value.items.filter(
      (i) => i.status === 'pending' && !i.matched_product_id
    ).length
  })

  /**
   * Check if import is fully processed
   */
  const isFullyProcessed = computed(() => {
    if (!currentImport.value) return false
    return currentImport.value.items.every((i) => i.status !== 'pending')
  })

  return {
    // State
    pendingImports,
    currentImport,
    loading,
    error,
    // Methods
    fetchPendingImports,
    getPendingImport,
    acceptItem,
    rejectItem,
    acceptAllMatched,
    // Computed
    pendingItemsCount,
    matchedItemsCount,
    unmatchedItemsCount,
    isFullyProcessed,
  }
}
