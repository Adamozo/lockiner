<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import AppToasts from '~/components/AppToasts.vue'

// Initialize PWA functionality
usePWAInstall()

// Auto-subscribe to push after login
if (import.meta.client) {
  const authStore = useAuthStore()
  const { subscribeToPush } = useNotifications()

  watch(() => authStore.isAuthenticated, async (isAuth) => {
    if (isAuth && 'Notification' in window && Notification.permission !== 'denied') {
      // Small delay to let SW register
      setTimeout(() => subscribeToPush(), 3000)
    }
  }, { immediate: true })
}
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <NuxtPwaAssets />
    <NuxtLoadingIndicator />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <PwaInstallBanner />
    <PwaUpdatePrompt />
    <AppToasts />
  </div>
</template>
