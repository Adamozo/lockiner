/**
 * API client composable
 * Provides a configured $fetch instance for backend API calls
 * Includes automatic JWT authentication and token refresh
 */

import { useAuthStore } from '~/stores/auth'

// Shared state for refresh token handling (outside composable for singleton behavior)
let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

/**
 * Get access token from cookie (SSR-safe)
 */
const getStoredToken = (): string | null => {
  const tokenCookie = useCookie<string | null>('scrooge_access_token')
  return tokenCookie.value
}

/**
 * Handle 401 error - refresh token or redirect to login
 * Returns true if token was refreshed successfully, false otherwise
 */
const handle401Error = async (): Promise<boolean> => {
  if (!import.meta.client) {
    return false
  }

  // If already refreshing, wait for the existing refresh to complete
  if (isRefreshing && refreshPromise) {
    return refreshPromise
  }

  isRefreshing = true

  refreshPromise = (async () => {
    try {
      const authStore = useAuthStore()
      const refreshed = await authStore.refreshAccessToken()

      if (refreshed) {
        return true
      }

      // Refresh failed, redirect to login
      const toast = useToast()
      toast.add({
        title: 'Session Expired',
        description: 'Your session has expired. Please log in again.',
        color: 'orange',
      })
      authStore.clearTokens()
      await navigateTo('/login')
      return false
    } catch {
      // Refresh failed, redirect to login
      const authStore = useAuthStore()
      const toast = useToast()
      toast.add({
        title: 'Session Expired',
        description: 'Your session has expired. Please log in again.',
        color: 'orange',
      })
      authStore.clearTokens()
      await navigateTo('/login')
      return false
    } finally {
      isRefreshing = false
      refreshPromise = null
    }
  })()

  return refreshPromise
}

/**
 * Create API client with base configuration and auth support
 */
export const useApi = () => {

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

        // Try to refresh token and handle redirect
        await handle401Error()
      } else if (response.status === 403) {
        console.error("Forbidden - insufficient permissions")

        // Parse error message for specific permission errors
        const detail = response._data?.detail?.toLowerCase() || ''

        // Handle 403 with "not authenticated" as an auth error (backend bug workaround)
        if (detail.includes('not authenticated') || detail.includes('authentication')) {
          console.error("403 with auth error - treating as 401")
          await handle401Error()
        } else if (import.meta.client) {
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
