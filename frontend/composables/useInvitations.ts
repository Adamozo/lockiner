/**
 * Invitations Composable
 * Handles household invitation management
 */

import type {
  InvitationCreate,
  InvitationResponse,
  InvitationPreview,
  InvitationJoinResponse,
} from '~/types/api'

export const useInvitations = () => {
  const api = useApi()

  const invitations = ref<InvitationResponse[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Create a new invitation for a household
   * @param householdUid - Household UUID
   * @param options - Invitation options (expires_in_days, max_uses)
   */
  const createInvitation = async (
    householdUid: string,
    options?: InvitationCreate
  ): Promise<InvitationResponse> => {
    loading.value = true
    error.value = null

    try {
      const response = await api<InvitationResponse>(
        `/api/v1/households/${householdUid}/invitations`,
        {
          method: 'POST',
          body: options || {},
        }
      )

      invitations.value.push(response)
      return response
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to create invitation'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * List active invitations for a household
   * @param householdUid - Household UUID
   */
  const listInvitations = async (householdUid: string): Promise<InvitationResponse[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await api<InvitationResponse[]>(
        `/api/v1/households/${householdUid}/invitations`
      )

      invitations.value = response
      return response
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to list invitations'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Revoke an invitation
   * @param householdUid - Household UUID
   * @param invitationId - Invitation ID
   */
  const revokeInvitation = async (
    householdUid: string,
    invitationId: number
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api(`/api/v1/households/${householdUid}/invitations/${invitationId}`, {
        method: 'DELETE',
      })

      invitations.value = invitations.value.filter(inv => inv.id !== invitationId)
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to revoke invitation'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Get invitation preview (public, no auth required)
   * @param token - Invitation token
   */
  const getInvitationPreview = async (token: string): Promise<InvitationPreview> => {
    loading.value = true
    error.value = null

    try {
      // Note: This endpoint doesn't require authentication
      const response = await $fetch<InvitationPreview>(`/api/v1/invitations/${token}`)
      return response
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string }, statusCode?: number }

      if (err.statusCode === 410) {
        error.value = 'This invitation has expired or been revoked'
      } else if (err.statusCode === 404) {
        error.value = 'Invitation not found'
      } else {
        error.value = err.data?.detail || 'Failed to load invitation'
      }
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Join a household using an invitation token
   * @param token - Invitation token
   */
  const joinHousehold = async (token: string): Promise<InvitationJoinResponse> => {
    loading.value = true
    error.value = null

    try {
      const response = await api<InvitationJoinResponse>(
        `/api/v1/invitations/${token}/join`,
        {
          method: 'POST',
        }
      )

      return response
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string }, statusCode?: number }

      if (err.statusCode === 410) {
        error.value = 'This invitation has expired or been revoked'
      } else if (err.statusCode === 409) {
        error.value = 'You are already a member of this household'
      } else {
        error.value = err.data?.detail || 'Failed to join household'
      }
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Generate a shareable invitation link
   * @param token - Invitation token
   */
  const getInvitationLink = (token: string): string => {
    if (import.meta.client) {
      return `${window.location.origin}/join/${token}`
    }
    return `/join/${token}`
  }

  /**
   * Copy invitation link to clipboard
   * @param token - Invitation token
   */
  const copyInvitationLink = async (token: string): Promise<boolean> => {
    const link = getInvitationLink(token)

    if (import.meta.client && navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(link)
        return true
      } catch {
        return false
      }
    }

    return false
  }

  return {
    // State
    invitations,
    loading,
    error,

    // Actions
    createInvitation,
    listInvitations,
    revokeInvitation,
    getInvitationPreview,
    joinHousehold,
    getInvitationLink,
    copyInvitationLink,
  }
}
