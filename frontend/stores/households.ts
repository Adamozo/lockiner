/**
 * Households Pinia Store
 * Global state management for households and members
 */

import { defineStore } from 'pinia'
import type {
  Household,
  HouseholdCreate,
  HouseholdUpdate,
  HouseholdResponse,
  HouseholdDetailResponse,
  HouseholdMember,
  HouseholdMemberUpdate,
  MemberRole,
} from '~/types/api'

export const useHouseholdsStore = defineStore('households', () => {
  // API client
  const api = useApi()

  // State
  const households = ref<HouseholdResponse[]>([])
  const currentHousehold = ref<HouseholdDetailResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetched = ref<Date | null>(null)

  // Cache duration (5 minutes)
  const CACHE_DURATION = 5 * 60 * 1000

  // Getters
  const householdCount = computed(() => households.value.length)

  const hasHouseholds = computed(() => households.value.length > 0)

  const isCacheValid = computed(() => {
    if (!lastFetched.value) return false
    const now = new Date()
    return now.getTime() - lastFetched.value.getTime() < CACHE_DURATION
  })

  const currentMembers = computed(() => currentHousehold.value?.members || [])

  const currentUserRole = computed((): MemberRole | null => {
    // This would need to be determined by comparing with current user ID
    // For now, return null and let components handle this
    return null
  })

  const isManager = (userId: number): boolean => {
    const member = currentMembers.value.find(m => m.user_id === userId)
    return member?.role === 'manager'
  }

  const isMember = (userId: number): boolean => {
    return currentMembers.value.some(m => m.user_id === userId)
  }

  const getHouseholdByUid = (uid: string): HouseholdResponse | undefined => {
    return households.value.find(h => h.uid === uid)
  }

  // Actions
  const fetchHouseholds = async (force = false): Promise<void> => {
    // Use cache if valid and not forced
    if (!force && isCacheValid.value && households.value.length > 0) {
      return
    }

    loading.value = true
    error.value = null

    try {
      const data = await api<HouseholdResponse[]>('/api/v1/households/')
      households.value = data
      lastFetched.value = new Date()
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to fetch households'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchHousehold = async (uid: string): Promise<HouseholdDetailResponse> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<HouseholdDetailResponse>(`/api/v1/households/${uid}`)
      currentHousehold.value = data
      return data
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to fetch household'
      throw e
    } finally {
      loading.value = false
    }
  }

  const createHousehold = async (household: HouseholdCreate): Promise<HouseholdResponse> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<HouseholdResponse>('/api/v1/households/', {
        method: 'POST',
        body: household,
      })

      households.value.push(data)
      return data
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to create household'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateHousehold = async (
    uid: string,
    updates: HouseholdUpdate
  ): Promise<HouseholdResponse> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<HouseholdResponse>(`/api/v1/households/${uid}`, {
        method: 'PUT',
        body: updates,
      })

      // Update in households list
      const index = households.value.findIndex(h => h.uid === uid)
      if (index !== -1) {
        households.value[index] = data
      }

      // Update current household if it's the same
      if (currentHousehold.value?.uid === uid) {
        currentHousehold.value = { ...currentHousehold.value, ...data }
      }

      return data
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to update household'
      throw e
    } finally {
      loading.value = false
    }
  }

  const deleteHousehold = async (uid: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api(`/api/v1/households/${uid}`, {
        method: 'DELETE',
      })

      households.value = households.value.filter(h => h.uid !== uid)

      if (currentHousehold.value?.uid === uid) {
        currentHousehold.value = null
      }
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to delete household'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Member management
  const fetchMembers = async (uid: string): Promise<HouseholdMember[]> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<HouseholdMember[]>(`/api/v1/households/${uid}/members`)
      if (currentHousehold.value?.uid === uid) {
        currentHousehold.value.members = data
      }
      return data
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to fetch members'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateMember = async (
    uid: string,
    userId: number,
    updates: HouseholdMemberUpdate
  ): Promise<HouseholdMember> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<HouseholdMember>(
        `/api/v1/households/${uid}/members/${userId}`,
        {
          method: 'PUT',
          body: updates,
        }
      )

      // Update in current household members
      if (currentHousehold.value?.uid === uid) {
        const index = currentHousehold.value.members.findIndex(m => m.user_id === userId)
        if (index !== -1) {
          currentHousehold.value.members[index] = data
        }
      }

      return data
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to update member'
      throw e
    } finally {
      loading.value = false
    }
  }

  const removeMember = async (uid: string, userId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api(`/api/v1/households/${uid}/members/${userId}`, {
        method: 'DELETE',
      })

      // Remove from current household members
      if (currentHousehold.value?.uid === uid) {
        currentHousehold.value.members = currentHousehold.value.members.filter(
          m => m.user_id !== userId
        )
      }
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to remove member'
      throw e
    } finally {
      loading.value = false
    }
  }

  const leaveHousehold = async (uid: string): Promise<void> => {
    // This is essentially removing yourself
    // The backend handles this via DELETE /households/{uid}/members/{user_id}
    // where user_id is the current user's ID
    loading.value = true
    error.value = null

    try {
      // We need to get current user ID - this would need to come from auth store
      // For now, we'll rely on a special endpoint or the component to pass user ID
      throw new Error('leaveHousehold requires current user ID')
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string }, message?: string }
      error.value = err.data?.detail || err.message || 'Failed to leave household'
      throw e
    } finally {
      loading.value = false
    }
  }

  const invalidateCache = () => {
    lastFetched.value = null
  }

  const clearCurrentHousehold = () => {
    currentHousehold.value = null
  }

  return {
    // State
    households,
    currentHousehold,
    loading,
    error,

    // Getters
    householdCount,
    hasHouseholds,
    isCacheValid,
    currentMembers,
    currentUserRole,

    // Helper functions
    isManager,
    isMember,
    getHouseholdByUid,

    // Actions
    fetchHouseholds,
    fetchHousehold,
    createHousehold,
    updateHousehold,
    deleteHousehold,
    fetchMembers,
    updateMember,
    removeMember,
    leaveHousehold,
    invalidateCache,
    clearCurrentHousehold,
  }
})
