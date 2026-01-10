/**
 * Global Auth Middleware
 * Protects all routes except public ones (index, login, register)
 * Redirects unauthenticated users to login page
 */

import { useAuthStore } from '~/stores/auth'

// Routes that don't require authentication
const publicRoutes = ['/', '/login', '/register']

// Routes that start with these prefixes are also public
const publicPrefixes = ['/join/']

const isPublicRoute = (path: string): boolean => {
  if (publicRoutes.includes(path)) {
    return true
  }

  return publicPrefixes.some((prefix) => path.startsWith(prefix))
}

export default defineNuxtRouteMiddleware(async (to) => {
  // Only run on client side
  if (import.meta.server) {
    return
  }

  // Skip for public routes
  if (isPublicRoute(to.path)) {
    return
  }

  const authStore = useAuthStore()

  // Initialize store if not already done
  if (!authStore.initialized) {
    authStore.initialize()
  }

  // If we have a token, try to fetch user data
  if (authStore.accessToken && !authStore.user) {
    await authStore.fetchCurrentUser()
  }

  // If still not authenticated, redirect to login
  if (!authStore.isAuthenticated) {
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath },
    })
  }
})
