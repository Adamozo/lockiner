/**
 * Global Auth Middleware
 * Protects all routes except public ones (index, login, register)
 * Redirects unauthenticated users to login page
 */

import { useAuthStore } from '~/stores/auth'

// Routes that don't require authentication
const publicRoutes = ['/', '/login', '/register', '/privacy-policy', '/terms', '/changelog']

// Routes that start with these prefixes are also public
const publicPrefixes = ['/join/']

const isPublicRoute = (path: string): boolean => {
  if (publicRoutes.includes(path)) {
    return true
  }

  return publicPrefixes.some((prefix) => path.startsWith(prefix))
}

export default defineNuxtRouteMiddleware(async (to) => {
  // Skip for public routes
  if (isPublicRoute(to.path)) {
    return
  }

  const authStore = useAuthStore()

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

  // Admin route protection
  if (to.path.startsWith('/admin') && authStore.currentUser?.role !== 'admin') {
    return navigateTo('/home')
  }
})
