/**
 * Household Context Composable
 *
 * Manages the current household context for the application.
 * Uses cookies for SSR-safe state (fixes hydration mismatch).
 */

export const useHouseholdContext = () => {
  // SSR-safe storage using cookies
  const householdCookie = useCookie<string | null>('scrooge_household_context', {
    default: () => null,
    watch: true,
  })

  /**
   * The current household ID (reactive)
   */
  const currentHouseholdId = computed(() => householdCookie.value)

  /**
   * Set the current household context
   * @param householdId - Household UID or null for personal context
   */
  const setHouseholdContext = (householdId: string | null) => {
    householdCookie.value = householdId
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
  const isHouseholdContext = computed(() => !!householdCookie.value)

  /**
   * Check if we're in personal context
   */
  const isPersonalContext = computed(() => !householdCookie.value)

  /**
   * Get the current household ID for API calls
   * Returns undefined if in personal context (for optional params)
   */
  const householdIdForApi = computed(() => householdCookie.value || undefined)

  return {
    // State
    currentHouseholdId,

    // Computed
    isHouseholdContext,
    isPersonalContext,
    householdIdForApi,

    // Actions
    setHouseholdContext,
    clearHouseholdContext,
  }
}
