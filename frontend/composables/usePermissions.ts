/**
 * Permissions Composable
 * Centralized permission checking for role-based access control
 */

import { useAuthStore } from '~/stores/auth'
import { useHouseholdsStore } from '~/stores/households'
import type { MemberRole, MemberStatus, HouseholdMember } from '~/types/api'

/**
 * Permission error types matching backend
 */
export type PermissionErrorType =
  | 'not_authenticated'
  | 'not_household_member'
  | 'household_access_blocked'
  | 'not_household_manager'
  | 'household_not_found'

export interface PermissionError {
  type: PermissionErrorType
  message: string
}

export const usePermissions = () => {
  const authStore = useAuthStore()
  const householdsStore = useHouseholdsStore()

  /**
   * Current user's ID
   */
  const currentUserId = computed(() => authStore.user?.id || null)

  /**
   * Check if user is authenticated
   */
  const isAuthenticated = computed(() => authStore.isAuthenticated)

  /**
   * Get member info for current user in a specific household
   */
  const getMemberInfo = (householdUid?: string): HouseholdMember | null => {
    if (!currentUserId.value) return null

    // Use current household if no UID provided
    const household = householdUid
      ? householdsStore.getHouseholdByUid(householdUid)
      : householdsStore.currentHousehold

    if (!household) return null

    // For currentHousehold, we have members array
    const members = householdsStore.currentMembers
    return members.find(m => m.user_id === currentUserId.value) || null
  }

  /**
   * Get current user's role in a household
   */
  const getUserRole = (householdUid?: string): MemberRole | null => {
    const member = getMemberInfo(householdUid)
    return member?.role || null
  }

  /**
   * Get current user's status in a household
   */
  const getUserStatus = (householdUid?: string): MemberStatus | null => {
    const member = getMemberInfo(householdUid)
    return member?.status || null
  }

  /**
   * Check if current user is a member of the current household
   */
  const isMember = computed((): boolean => {
    if (!currentUserId.value || !householdsStore.currentHousehold) return false
    return householdsStore.isMember(currentUserId.value)
  })

  /**
   * Check if current user is a manager of the current household
   */
  const isManager = computed((): boolean => {
    if (!currentUserId.value || !householdsStore.currentHousehold) return false
    return householdsStore.isManager(currentUserId.value)
  })

  /**
   * Check if current user is blocked in the current household
   */
  const isBlocked = computed((): boolean => {
    const member = getMemberInfo()
    return member?.status === 'blocked'
  })

  /**
   * Check if current user is active (member and not blocked)
   */
  const isActive = computed((): boolean => {
    return isMember.value && !isBlocked.value
  })

  // ============================================
  // Permission Checking Methods
  // ============================================

  /**
   * Check if user can manage household (edit, delete, manage members)
   */
  const canManageHousehold = (householdUid?: string): boolean => {
    if (!isAuthenticated.value) return false
    const role = getUserRole(householdUid)
    const status = getUserStatus(householdUid)
    return role === 'manager' && status === 'active'
  }

  /**
   * Check if user can invite members
   */
  const canInviteMembers = (householdUid?: string): boolean => {
    return canManageHousehold(householdUid)
  }

  /**
   * Check if user can edit a specific member
   */
  const canEditMember = (householdUid?: string, memberId?: number): boolean => {
    if (!canManageHousehold(householdUid)) return false
    // Can't edit yourself as manager (to prevent demoting yourself)
    if (memberId === currentUserId.value) return false
    return true
  }

  /**
   * Check if user can remove a specific member
   */
  const canRemoveMember = (householdUid?: string, memberId?: number): boolean => {
    // Users can always remove themselves (leave)
    if (memberId === currentUserId.value) return true
    // Otherwise only managers can remove members
    return canManageHousehold(householdUid)
  }

  /**
   * Check if user can delete household
   */
  const canDeleteHousehold = (householdUid?: string): boolean => {
    return canManageHousehold(householdUid)
  }

  /**
   * Check if user can view household content (transactions, receipts, analytics)
   */
  const canViewContent = (householdUid?: string): boolean => {
    if (!isAuthenticated.value) return false
    const status = getUserStatus(householdUid)
    return status === 'active'
  }

  /**
   * Check if user can add content (transactions, receipts)
   */
  const canAddContent = (householdUid?: string): boolean => {
    return canViewContent(householdUid)
  }

  /**
   * Check if user can view analytics
   */
  const canViewAnalytics = (householdUid?: string): boolean => {
    return canViewContent(householdUid)
  }

  // ============================================
  // Error Parsing
  // ============================================

  /**
   * Parse API error to determine permission error type
   */
  const parsePermissionError = (
    error: { status?: number; data?: { detail?: string } }
  ): PermissionError | null => {
    const detail = error.data?.detail?.toLowerCase() || ''
    const status = error.status

    if (status === 401) {
      return {
        type: 'not_authenticated',
        message: 'You must be logged in to access this resource',
      }
    }

    if (status === 403) {
      if (detail.includes('blocked')) {
        return {
          type: 'household_access_blocked',
          message: 'Your access to this household has been blocked',
        }
      }
      if (detail.includes('manager')) {
        return {
          type: 'not_household_manager',
          message: 'Only household managers can perform this action',
        }
      }
      if (detail.includes('member')) {
        return {
          type: 'not_household_member',
          message: 'You are not a member of this household',
        }
      }
      // Generic 403
      return {
        type: 'not_household_member',
        message: error.data?.detail || 'Access denied',
      }
    }

    if (status === 404 && detail.includes('household')) {
      return {
        type: 'household_not_found',
        message: 'Household not found',
      }
    }

    return null
  }

  /**
   * Check if error is a permission error
   */
  const isPermissionError = (error: unknown): boolean => {
    const err = error as { status?: number }
    return err?.status === 401 || err?.status === 403
  }

  // ============================================
  // Computed shortcuts for current household
  // ============================================

  /**
   * Can current user manage the current household
   */
  const canManageCurrentHousehold = computed(() => canManageHousehold())

  /**
   * Can current user invite to the current household
   */
  const canInviteToCurrentHousehold = computed(() => canInviteMembers())

  /**
   * Can current user delete the current household
   */
  const canDeleteCurrentHousehold = computed(() => canDeleteHousehold())

  /**
   * Can current user view current household content
   */
  const canViewCurrentHouseholdContent = computed(() => canViewContent())

  /**
   * Can current user add to current household
   */
  const canAddToCurrentHousehold = computed(() => canAddContent())

  return {
    // State
    currentUserId,
    isAuthenticated,

    // Current household permissions (computed)
    isMember,
    isManager,
    isBlocked,
    isActive,

    // Permission checkers (functions for specific household)
    canManageHousehold,
    canInviteMembers,
    canEditMember,
    canRemoveMember,
    canDeleteHousehold,
    canViewContent,
    canAddContent,
    canViewAnalytics,

    // Computed shortcuts for current household
    canManageCurrentHousehold,
    canInviteToCurrentHousehold,
    canDeleteCurrentHousehold,
    canViewCurrentHouseholdContent,
    canAddToCurrentHousehold,

    // Utilities
    getMemberInfo,
    getUserRole,
    getUserStatus,
    parsePermissionError,
    isPermissionError,
  }
}
