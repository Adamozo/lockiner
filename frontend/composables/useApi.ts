/**
 * API client composable
 * Provides a configured $fetch instance for backend API calls
 * Includes automatic JWT authentication and token refresh
 */

import { useAuthStore } from '~/stores/auth'

// Token storage key (must match auth store)
const ACCESS_TOKEN_KEY = 'scrooge_access_token'

/**
 * Get access token from localStorage (client-side only)
 */
const getStoredToken = (): string | null => {
  if (import.meta.client) {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  }
  return null
}

/**
 * Create API client with base configuration and auth support
 */
export const useApi = () => {
  // Track if we're currently refreshing to avoid infinite loops
  let isRefreshing = false

  const apiFetch = $fetch.create({
    // Use relative URLs to leverage Nuxt's proxy (nuxt.config.ts -> nitro.devProxy)
    // Browser calls localhost:3000/api/v1/* -> Nuxt proxies to backend:8000/api/v1/*
    baseURL: "",

    // Request interceptor - add auth headers
    onRequest({ options }) {
      const headers: Record<string, string> = {}

      // Don't set Content-Type for FormData (let browser set it with boundary)
      if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json"
      }

      // Add Authorization header if token exists
      const token = getStoredToken()
      if (token) {
        headers["Authorization"] = `Bearer ${token}`
      }

      // Merge with existing headers
      options.headers = new Headers({
        ...(options.headers as HeadersInit),
        ...headers,
      })
    },

    // Response interceptor
    onResponse({ response }) {
      // Log successful responses in development
      if (process.dev) {
        console.log("[API Response]", response.status, response._data)
      }
    },

    // Error interceptor
    async onResponseError({ response, request, options }) {
      console.error("[API Error]", {
        url: response.url,
        status: response.status,
        statusText: response.statusText,
        data: response._data,
      })

      // Handle specific error codes
      if (response.status === 401) {
        console.error("Unauthorized - authentication required")

        // Try to refresh token (only on client side and if not already refreshing)
        if (import.meta.client && !isRefreshing) {
          isRefreshing = true

          try {
            const authStore = useAuthStore()
            const refreshed = await authStore.refreshAccessToken()

            if (refreshed) {
              isRefreshing = false
              // Retry the original request with new token
              const newToken = getStoredToken()
              if (newToken) {
                const newHeaders = new Headers(options.headers as HeadersInit)
                newHeaders.set("Authorization", `Bearer ${newToken}`)
                options.headers = newHeaders
                // Note: The retry happens automatically by re-throwing
              }
            } else {
              // Refresh failed, show notification and redirect to login
              isRefreshing = false
              const toast = useToast()
              toast.add({
                title: 'Session Expired',
                description: 'Your session has expired. Please log in again.',
                color: 'orange',
              })
              authStore.clearTokens()
              await navigateTo('/login')
            }
          } catch {
            isRefreshing = false
            // Refresh failed, show notification and redirect to login
            const authStore = useAuthStore()
            const toast = useToast()
            toast.add({
              title: 'Session Expired',
              description: 'Your session has expired. Please log in again.',
              color: 'orange',
            })
            authStore.clearTokens()
            await navigateTo('/login')
          }
        }
      } else if (response.status === 403) {
        console.error("Forbidden - insufficient permissions")

        // Parse error message for specific permission errors
        const detail = response._data?.detail?.toLowerCase() || ''

        if (import.meta.client) {
          const toast = useToast()

          if (detail.includes('blocked')) {
            toast.add({
              title: 'Access Blocked',
              description: 'Your access to this household has been blocked',
              color: 'red',
            })
          } else if (detail.includes('manager')) {
            toast.add({
              title: 'Manager Access Required',
              description: 'Only household managers can perform this action',
              color: 'red',
            })
          } else if (detail.includes('member')) {
            toast.add({
              title: 'Access Denied',
              description: 'You are not a member of this household',
              color: 'red',
            })
          } else {
            toast.add({
              title: 'Access Denied',
              description: response._data?.detail || 'You do not have permission to perform this action',
              color: 'red',
            })
          }
        }
      } else if (response.status === 404) {
        console.error("Not found")
      } else if (response.status === 410) {
        // Gone - typically for expired/revoked invitations
        console.error("Resource expired or no longer available")

        if (import.meta.client) {
          const toast = useToast()
          toast.add({
            title: 'Resource Unavailable',
            description: response._data?.detail || 'This resource has expired or been removed',
            color: 'yellow',
          })
        }
      } else if (response.status >= 500) {
        console.error("Server error")

        if (import.meta.client) {
          const toast = useToast()
          toast.add({
            title: 'Server Error',
            description: 'Something went wrong. Please try again later.',
            color: 'red',
          })
        }
      }
    },
  })

  return apiFetch
}

/**
 * Helper to build query string with optional household_id
 */
export const buildQueryParams = (
  params: Record<string, string | number | boolean | null | undefined>,
  householdId?: string | null
): string => {
  const queryParams = new URLSearchParams()

  // Add household_id if provided
  if (householdId) {
    queryParams.set('household_id', householdId)
  }

  // Add other params
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined) {
      queryParams.set(key, String(value))
    }
  }

  const queryString = queryParams.toString()
  return queryString ? `?${queryString}` : ''
}
