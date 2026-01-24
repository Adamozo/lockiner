/**
 * Authentication Composable
 * Wrapper around auth store with additional utilities
 */

import { useAuthStore } from '~/stores/auth'
import type { UserCreate, LoginRequest, UserUpdate, PasswordChangeRequest } from '~/types/api'

export const useAuth = () => {
  const store = useAuthStore()
  const router = useRouter()

  // Re-export store state and getters
  const user = computed(() => store.user)
  const isAuthenticated = computed(() => store.isAuthenticated)
  const isLoggedIn = computed(() => store.isLoggedIn)
  const loading = computed(() => store.loading)
  const error = computed(() => store.error)
  const userName = computed(() => store.userName)
  const userEmail = computed(() => store.userEmail)

  /**
   * Register a new user
   */
  const register = async (userData: UserCreate) => {
    return await store.register(userData)
  }

  /**
   * Login user and redirect to home
   */
  const login = async (credentials: LoginRequest, redirectTo = '/') => {
    await store.login(credentials)
    if (store.isAuthenticated) {
      await router.push(redirectTo)
    }
  }

  /**
   * Logout user and redirect to login
   */
  const logout = async (redirectTo = '/login') => {
    await store.logout()
    await router.push(redirectTo)
  }

  /**
   * Update user profile
   */
  const updateProfile = async (updates: UserUpdate) => {
    return await store.updateProfile(updates)
  }

  /**
   * Change user password
   */
  const changePassword = async (data: PasswordChangeRequest) => {
    return await store.changePassword(data)
  }

  /**
   * Check authentication status on app start
   */
  const checkAuth = async () => {
    return await store.checkAuth()
  }

  /**
   * Get current access token (for manual API calls)
   */
  const getAccessToken = () => {
    return store.accessToken
  }

  /**
   * Refresh the access token
   */
  const refreshToken = async () => {
    return await store.refreshAccessToken()
  }

  /**
   * Require authentication - redirect to login if not authenticated
   */
  const requireAuth = async (redirectTo = '/login') => {
    if (!store.isAuthenticated) {
      // Try to fetch user if we have a token
      if (store.accessToken) {
        await store.fetchCurrentUser()
      }

      if (!store.isAuthenticated) {
        await router.push(redirectTo)
        return false
      }
    }

    return true
  }

  /**
   * Require guest - redirect to home if authenticated
   */
  const requireGuest = async (redirectTo = '/') => {
    if (store.accessToken) {
      await store.fetchCurrentUser()
    }

    if (store.isAuthenticated) {
      await router.push(redirectTo)
      return false
    }

    return true
  }

  return {
    // State
    user,
    isAuthenticated,
    isLoggedIn,
    loading,
    error,
    userName,
    userEmail,

    // Actions
    register,
    login,
    logout,
    updateProfile,
    changePassword,
    checkAuth,
    getAccessToken,
    refreshToken,
    requireAuth,
    requireGuest,
  }
}
