/**
 * Authentication Pinia Store
 * Global state management for user authentication
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

// Token storage keys
const ACCESS_TOKEN_KEY = 'scrooge_access_token'
const REFRESH_TOKEN_KEY = 'scrooge_refresh_token'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const initialized = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
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

    if (accessToken.value) {
      headers['Authorization'] = `Bearer ${accessToken.value}`
    }

    const response = await $fetch<T>(getApiUrl(path), {
      ...options,
      headers,
    })

    return response
  }

  // Initialize: Load tokens from localStorage
  const initialize = () => {
    if (import.meta.client && !initialized.value) {
      accessToken.value = localStorage.getItem(ACCESS_TOKEN_KEY)
      refreshToken.value = localStorage.getItem(REFRESH_TOKEN_KEY)
      initialized.value = true
    }
  }

  // Save tokens to localStorage
  const saveTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh

    if (import.meta.client) {
      localStorage.setItem(ACCESS_TOKEN_KEY, access)
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    }
  }

  // Clear tokens from localStorage
  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null

    if (import.meta.client) {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
    }
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
      if (accessToken.value) {
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
    if (!refreshToken.value) {
      return false
    }

    try {
      const tokens = await $fetch<TokenResponse>(getApiUrl('/auth/refresh-token'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: { refresh_token: refreshToken.value },
      })

      saveTokens(tokens.access_token, tokens.refresh_token)
      return true
    } catch {
      clearTokens()
      return false
    }
  }

  const fetchCurrentUser = async (): Promise<User | null> => {
    if (!accessToken.value) {
      return null
    }

    loading.value = true
    error.value = null

    try {
      const userData = await authFetch<User>('/auth/me')
      user.value = userData
      return userData
    } catch (e: unknown) {
      const err = e as { status?: number }
      // If 401, try to refresh token
      if (err.status === 401) {
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
    initialize()

    if (!accessToken.value) {
      return false
    }

    const userData = await fetchCurrentUser()
    return !!userData
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    initialized,

    // Getters
    isAuthenticated,
    isLoggedIn,
    currentUser,
    userName,
    userEmail,

    // Actions
    initialize,
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
