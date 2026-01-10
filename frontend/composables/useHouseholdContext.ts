/**
 * Household Context Composable
 *
 * Manages the current household context for the application.
 * Stores the selected household in localStorage and provides
 * reactive access to the current household ID.
 */

const HOUSEHOLD_CONTEXT_KEY = 'scrooge_household_context'

// Global state (shared across all instances)
const currentHouseholdId = ref<string | null>(null)
const initialized = ref(false)

export const useHouseholdContext = () => {
  /**
   * Initialize the household context from localStorage
   */
  const initialize = () => {
    if (import.meta.client && !initialized.value) {
      const stored = localStorage.getItem(HOUSEHOLD_CONTEXT_KEY)
      currentHouseholdId.value = stored || null
      initialized.value = true
    }
  }

  /**
   * Set the current household context
   * @param householdId - Household UID or null for personal context
   */
  const setHouseholdContext = (householdId: string | null) => {
    currentHouseholdId.value = householdId

    if (import.meta.client) {
      if (householdId) {
        localStorage.setItem(HOUSEHOLD_CONTEXT_KEY, householdId)
      } else {
        localStorage.removeItem(HOUSEHOLD_CONTEXT_KEY)
      }
    }
  }

  /**
   * Clear the household context (switch to personal)
   */
  const clearHouseholdContext = () => {
    setHouseholdContext(null)
  }

  /**
   * Check if we're in a household context
   */
  const isHouseholdContext = computed(() => !!currentHouseholdId.value)

  /**
   * Check if we're in personal context
   */
  const isPersonalContext = computed(() => !currentHouseholdId.value)

  /**
   * Get the current household ID for API calls
   * Returns undefined if in personal context (for optional params)
   */
  const householdIdForApi = computed(() => currentHouseholdId.value || undefined)

  // Initialize on first use
  if (import.meta.client) {
    initialize()
  }

  return {
    // State
    currentHouseholdId: readonly(currentHouseholdId),
    initialized: readonly(initialized),

    // Computed
    isHouseholdContext,
    isPersonalContext,
    householdIdForApi,

    // Actions
    initialize,
    setHouseholdContext,
    clearHouseholdContext,
  }
}
