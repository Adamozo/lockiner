/**
 * Households Composable
 * Wrapper around households store with additional utilities
 */

import { useHouseholdsStore } from '~/stores/households'
import { useAuthStore } from '~/stores/auth'
import type {
  HouseholdCreate,
  HouseholdUpdate,
  HouseholdMemberUpdate,
} from '~/types/api'

export const useHouseholds = () => {
  const store = useHouseholdsStore()
  const authStore = useAuthStore()
  const router = useRouter()

  // Re-export store state and getters
  const households = computed(() => store.households)
  const currentHousehold = computed(() => store.currentHousehold)
  const currentMembers = computed(() => store.currentMembers)
  const loading = computed(() => store.loading)
  const error = computed(() => store.error)
  const hasHouseholds = computed(() => store.hasHouseholds)

  /**
   * Check if current user is a manager of the current household
   */
  const isCurrentUserManager = computed(() => {
    if (!authStore.user || !store.currentHousehold) return false
    return store.isManager(authStore.user.id)
  })

  /**
   * Check if current user is a member of the current household
   */
  const isCurrentUserMember = computed(() => {
    if (!authStore.user || !store.currentHousehold) return false
    return store.isMember(authStore.user.id)
  })

  /**
   * Get current user's member info in the current household
   */
  const currentUserMemberInfo = computed(() => {
    if (!authStore.user || !store.currentHousehold) return null
    return store.currentMembers.find(m => m.user_id === authStore.user!.id) || null
  })

  /**
   * Fetch all user's households
   */
  const fetchHouseholds = async (force = false) => {
    return await store.fetchHouseholds(force)
  }

  /**
   * Fetch single household with members
   */
  const fetchHousehold = async (uid: string) => {
    return await store.fetchHousehold(uid)
  }

  /**
   * Create a new household
   */
  const createHousehold = async (data: HouseholdCreate) => {
    return await store.createHousehold(data)
  }

  /**
   * Update household
   */
  const updateHousehold = async (uid: string, data: HouseholdUpdate) => {
    return await store.updateHousehold(uid, data)
  }

  /**
   * Delete household
   */
  const deleteHousehold = async (uid: string, redirectTo = '/households') => {
    await store.deleteHousehold(uid)
    await router.push(redirectTo)
  }

  /**
   * Update a member's role or status
   */
  const updateMember = async (
    householdUid: string,
    userId: number,
    updates: HouseholdMemberUpdate
  ) => {
    return await store.updateMember(householdUid, userId, updates)
  }

  /**
   * Remove a member from household
   */
  const removeMember = async (householdUid: string, userId: number) => {
    return await store.removeMember(householdUid, userId)
  }

  /**
   * Leave the current household (remove self)
   */
  const leaveHousehold = async (householdUid: string, redirectTo = '/households') => {
    if (!authStore.user) {
      throw new Error('Must be logged in to leave household')
    }

    await store.removeMember(householdUid, authStore.user.id)

    // Remove from local households list
    store.households = store.households.filter(h => h.uid !== householdUid)

    await router.push(redirectTo)
  }

  /**
   * Refresh members list
   */
  const refreshMembers = async (householdUid: string) => {
    return await store.fetchMembers(householdUid)
  }

  /**
   * Get household by UID from cached list
   */
  const getHouseholdByUid = (uid: string) => {
    return store.getHouseholdByUid(uid)
  }

  /**
   * Clear current household (when navigating away)
   */
  const clearCurrentHousehold = () => {
    store.clearCurrentHousehold()
  }

  /**
   * Invalidate cache to force refresh
   */
  const invalidateCache = () => {
    store.invalidateCache()
  }

  return {
    // State
    households,
    currentHousehold,
    currentMembers,
    loading,
    error,
    hasHouseholds,

    // Computed
    isCurrentUserManager,
    isCurrentUserMember,
    currentUserMemberInfo,

    // Actions
    fetchHouseholds,
    fetchHousehold,
    createHousehold,
    updateHousehold,
    deleteHousehold,
    updateMember,
    removeMember,
    leaveHousehold,
    refreshMembers,
    getHouseholdByUid,
    clearCurrentHousehold,
    invalidateCache,
  }
}
