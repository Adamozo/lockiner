/**
 * Guest Middleware
 * Protects routes that should only be accessible to non-authenticated users
 * Redirects authenticated users to home page (e.g., login, register pages)
 */

import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async (to) => {
  // Only run on client side
  if (import.meta.server) {
    return
  }

  const authStore = useAuthStore()

  // If we have a token, try to fetch user data
  if (authStore.accessToken && !authStore.user) {
    await authStore.fetchCurrentUser()
  }

  // If authenticated, redirect to home or specified redirect
  if (authStore.isAuthenticated) {
    // Check if there's a redirect query param
    const redirect = to.query.redirect as string

    return navigateTo(redirect || '/home')
  }
})
