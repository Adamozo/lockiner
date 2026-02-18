/**
 * Notifications composable
 * Handles notification API calls and push subscription
 */

import type { NotificationItem, UnreadCountResponse, DevicePushSubscription } from '~/types/api'

export const useNotifications = () => {
  const api = useApi()
  const unreadCount = useState<number>('notification-unread-count', () => 0)

  const fetchNotifications = async (skip = 0, limit = 20): Promise<NotificationItem[]> => {
    return await api<NotificationItem[]>(`/api/v1/notifications?skip=${skip}&limit=${limit}`)
  }

  const fetchUnreadCount = async (): Promise<number> => {
    const data = await api<UnreadCountResponse>('/api/v1/notifications/unread-count')
    unreadCount.value = data.count
    return data.count
  }

  const markAsRead = async (id: number): Promise<void> => {
    await api(`/api/v1/notifications/${id}/read`, { method: 'PUT' })
  }

  const markAsUnread = async (id: number): Promise<void> => {
    await api(`/api/v1/notifications/${id}/unread`, { method: 'PUT' })
  }

  const markAllAsRead = async (): Promise<void> => {
    await api('/api/v1/notifications/mark-all-read', { method: 'PUT' })
    unreadCount.value = 0
  }

  const deleteNotification = async (id: number): Promise<void> => {
    await api(`/api/v1/notifications/${id}`, { method: 'DELETE' })
  }

  const subscribeToPush = async (): Promise<boolean> => {
    try {
      // Get VAPID public key
      const { public_key } = await api<{ public_key: string }>('/api/v1/notifications/vapid-public-key')
      if (!public_key) return false

      // Request permission
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') return false

      // Get service worker registration
      const registration = await navigator.serviceWorker.ready

      // Subscribe to push
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(public_key),
      })

      const json = subscription.toJSON()

      // Send to backend
      await api('/api/v1/notifications/subscribe', {
        method: 'POST',
        body: {
          endpoint: json.endpoint,
          p256dh: json.keys?.p256dh,
          auth: json.keys?.auth,
        },
      })

      return true
    } catch (e) {
      console.error('Failed to subscribe to push:', e)
      return false
    }
  }

  const fetchSubscriptions = async (): Promise<DevicePushSubscription[]> => {
    return await api<DevicePushSubscription[]>('/api/v1/notifications/subscriptions')
  }

  const deleteSubscription = async (id: number): Promise<void> => {
    await api(`/api/v1/notifications/subscriptions/${id}`, { method: 'DELETE' })
  }

  const getCurrentEndpoint = async (): Promise<string | null> => {
    try {
      if (!('serviceWorker' in navigator)) return null
      const registration = await navigator.serviceWorker.ready
      const sub = await registration.pushManager.getSubscription()
      return sub?.endpoint ?? null
    } catch {
      return null
    }
  }

  return {
    unreadCount,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAsUnread,
    markAllAsRead,
    deleteNotification,
    subscribeToPush,
    fetchSubscriptions,
    deleteSubscription,
    getCurrentEndpoint,
  }
}

// Helper: convert base64 VAPID key to Uint8Array
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}
