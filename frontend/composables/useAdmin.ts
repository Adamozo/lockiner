/**
 * Admin composable
 * API calls for admin panel (vouchers, users, notifications)
 */

import type { VoucherAdmin, UserAdmin } from '~/types/api'

export const useAdmin = () => {
  const api = useApi()

  // ========================================================================
  // Vouchers
  // ========================================================================

  const fetchVouchers = async (): Promise<VoucherAdmin[]> => {
    return await api<VoucherAdmin[]>('/api/v1/admin/vouchers')
  }

  const generateVouchers = async (count: number): Promise<{ vouchers: VoucherAdmin[]; count: number }> => {
    return await api('/api/v1/admin/vouchers/generate', {
      method: 'POST',
      body: { count },
    })
  }

  const blockVoucher = async (id: number): Promise<VoucherAdmin> => {
    return await api<VoucherAdmin>(`/api/v1/admin/vouchers/${id}/block`, { method: 'PUT' })
  }

  const unblockVoucher = async (id: number): Promise<VoucherAdmin> => {
    return await api<VoucherAdmin>(`/api/v1/admin/vouchers/${id}/unblock`, { method: 'PUT' })
  }

  // ========================================================================
  // Users
  // ========================================================================

  const fetchUsers = async (): Promise<UserAdmin[]> => {
    return await api<UserAdmin[]>('/api/v1/admin/users')
  }

  const blockUser = async (id: number): Promise<UserAdmin> => {
    return await api<UserAdmin>(`/api/v1/admin/users/${id}/block`, { method: 'PUT' })
  }

  const unblockUser = async (id: number): Promise<UserAdmin> => {
    return await api<UserAdmin>(`/api/v1/admin/users/${id}/unblock`, { method: 'PUT' })
  }

  const setUserRole = async (id: number, role: 'user' | 'admin'): Promise<UserAdmin> => {
    return await api<UserAdmin>(`/api/v1/admin/users/${id}/set-role`, {
      method: 'PUT',
      body: { role },
    })
  }

  // ========================================================================
  // Notifications (send)
  // ========================================================================

  const sendNotification = async (data: {
    title: string
    body: string
    notification_type?: string
    target: 'all' | 'selected'
    user_ids?: number[]
  }) => {
    return await api('/api/v1/notifications/send', {
      method: 'POST',
      body: data,
    })
  }

  return {
    // Vouchers
    fetchVouchers,
    generateVouchers,
    blockVoucher,
    unblockVoucher,
    // Users
    fetchUsers,
    blockUser,
    unblockUser,
    setUserRole,
    // Notifications
    sendNotification,
  }
}
