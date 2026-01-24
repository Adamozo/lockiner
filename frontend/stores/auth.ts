/**
 * Authentication Pinia Store
 * Global state management for user authentication
 *
 * Uses cookies instead of localStorage for SSR-safe token storage.
 */

import { defineStore } from 'pinia'
import type {
  User,
  UserCreate,
  UserUpdate,
  LoginRequest,
  TokenResponse,
  PasswordChangeRequest,
} from '~/types/api'

// Cookie keys
const ACCESS_TOKEN_KEY = 'scrooge_access_token'
const REFRESH_TOKEN_KEY = 'scrooge_refresh_token'

export const useAuthStore = defineStore('auth', () => {
  // SSR-safe token storage using cookies
  const accessTokenCookie = useCookie<string | null>(ACCESS_TOKEN_KEY, {
    default: () => null,
    watch: true,
  })
  const refreshTokenCookie = useCookie<string | null>(REFRESH_TOKEN_KEY, {
    default: () => null,
    watch: true,
  })

  // State
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const accessToken = computed(() => accessTokenCookie.value)
  const refreshToken = computed(() => refreshTokenCookie.value)
  const isAuthenticated = computed(() => !!accessTokenCookie.value && !!user.value)
  const isLoggedIn = computed(() => isAuthenticated.value)
  const currentUser = computed(() => user.value)
  const userName = computed(() => user.value?.name || '')
  const userEmail = computed(() => user.value?.email || '')

  // Helper: Get base API URL for direct fetch (before useApi is configured)
  const getApiUrl = (path: string) => {
    // In SSR/server context, we need to use the proxy
    return `/api/v1${path}`
  }

  // Helper: Make authenticated request
  const authFetch = async <T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (accessTokenCookie.value) {
      headers['Authorization'] = `Bearer ${accessTokenCookie.value}`
    }

    const response = await $fetch<T>(getApiUrl(path), {
      ...options,
      headers,
    })

    return response
  }

  // Save tokens to cookies
  const saveTokens = (access: string, refresh: string) => {
    accessTokenCookie.value = access
    refreshTokenCookie.value = refresh
  }

  // Clear tokens from cookies
  const clearTokens = () => {
    accessTokenCookie.value = null
    refreshTokenCookie.value = null
    user.value = null
  }

  // Actions
  const register = async (userData: UserCreate): Promise<User> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<User>(getApiUrl('/auth/register'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: userData,
      })

      return response
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Registration failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  const login = async (credentials: LoginRequest): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const tokens = await $fetch<TokenResponse>(getApiUrl('/auth/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: credentials,
      })

      saveTokens(tokens.access_token, tokens.refresh_token)

      // Fetch user data after successful login
      await fetchCurrentUser()
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Login failed'
      clearTokens()
      throw e
    } finally {
      loading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    loading.value = true

    try {
      if (accessTokenCookie.value) {
        await authFetch('/auth/logout', { method: 'POST' })
      }
    } catch {
      // Ignore errors during logout - we'll clear tokens anyway
    } finally {
      clearTokens()
      loading.value = false
    }
  }

  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshTokenCookie.value) {
      return false
    }

    try {
      const tokens = await $fetch<TokenResponse>(getApiUrl('/auth/refresh-token'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: { refresh_token: refreshTokenCookie.value },
      })

      saveTokens(tokens.access_token, tokens.refresh_token)
      return true
    } catch {
      clearTokens()
      return false
    }
  }

  const fetchCurrentUser = async (): Promise<User | null> => {
    if (!accessTokenCookie.value) {
      return null
    }

    loading.value = true
    error.value = null

    try {
      const userData = await authFetch<User>('/auth/me')
      user.value = userData
      return userData
    } catch (e: unknown) {
      // FetchError from $fetch has status on response or statusCode property
      const err = e as { status?: number; statusCode?: number; response?: { status?: number } }
      const status = err.status || err.statusCode || err.response?.status

      // If 401, try to refresh token
      if (status === 401) {
        const refreshed = await refreshAccessToken()
        if (refreshed) {
          return fetchCurrentUser()
        }
      }
      clearTokens()
      return null
    } finally {
      loading.value = false
    }
  }

  const updateProfile = async (updates: UserUpdate): Promise<User> => {
    loading.value = true
    error.value = null

    try {
      const updatedUser = await authFetch<User>('/auth/me', {
        method: 'PUT',
        body: JSON.stringify(updates),
      })

      user.value = updatedUser
      return updatedUser
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to update profile'
      throw e
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (data: PasswordChangeRequest): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await authFetch('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    } catch (e: unknown) {
      const err = e as { data?: { detail?: string } }
      error.value = err.data?.detail || 'Failed to change password'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Check if user is authenticated on app start
  const checkAuth = async (): Promise<boolean> => {
    if (!accessTokenCookie.value) {
      return false
    }

    const userData = await fetchCurrentUser()
    return !!userData
  }

  return {
    // State
    user,
    loading,
    error,

    // Getters (tokens are now computed from cookies)
    accessToken,
    refreshToken,
    isAuthenticated,
    isLoggedIn,
    currentUser,
    userName,
    userEmail,

    // Actions
    register,
    login,
    logout,
    refreshAccessToken,
    fetchCurrentUser,
    updateProfile,
    changePassword,
    checkAuth,
    clearTokens,
  }
})
