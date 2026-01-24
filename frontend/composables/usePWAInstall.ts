import { ref, onMounted, onUnmounted } from 'vue'

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[]
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed'
    platform: string
  }>
  prompt(): Promise<void>
}

const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null)
const isInstallable = ref(false)
const isInstalled = ref(false)
const needRefresh = ref(false)
const updateServiceWorker = ref<(() => Promise<void>) | null>(null)

export function usePWAInstall() {
  const DISMISS_KEY = 'pwa-install-dismissed'
  const DISMISS_DURATION = 7 * 24 * 60 * 60 * 1000 // 1 week

  const isDismissed = ref(false)

  const checkDismissed = () => {
    if (import.meta.client) {
      const dismissedAt = localStorage.getItem(DISMISS_KEY)
      if (dismissedAt) {
        const elapsed = Date.now() - parseInt(dismissedAt, 10)
        isDismissed.value = elapsed < DISMISS_DURATION
        if (elapsed >= DISMISS_DURATION) {
          localStorage.removeItem(DISMISS_KEY)
        }
      }
    }
  }

  const dismissInstall = () => {
    isDismissed.value = true
    if (import.meta.client) {
      localStorage.setItem(DISMISS_KEY, Date.now().toString())
    }
  }

  const handleBeforeInstallPrompt = (e: Event) => {
    e.preventDefault()
    deferredPrompt.value = e as BeforeInstallPromptEvent
    isInstallable.value = true
  }

  const handleAppInstalled = () => {
    isInstalled.value = true
    isInstallable.value = false
    deferredPrompt.value = null
  }

  const installApp = async () => {
    if (!deferredPrompt.value) return false

    try {
      await deferredPrompt.value.prompt()
      const { outcome } = await deferredPrompt.value.userChoice

      if (outcome === 'accepted') {
        isInstalled.value = true
        isInstallable.value = false
      }

      deferredPrompt.value = null
      return outcome === 'accepted'
    } catch {
      return false
    }
  }

  const refreshApp = async () => {
    if (updateServiceWorker.value) {
      await updateServiceWorker.value()
    }
  }

  const initPWA = async () => {
    if (!import.meta.client) return

    checkDismissed()

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      isInstalled.value = true
    }

    // Dynamic import to avoid SSR issues
    try {
      const { useRegisterSW } = await import('virtual:pwa-register/vue')
      const { needRefresh: swNeedRefresh, updateServiceWorker: swUpdate } = useRegisterSW({
        immediate: true,
        onRegistered(r) {
          if (r) {
            // Check for updates every hour
            setInterval(() => {
              r.update()
            }, 60 * 60 * 1000)
          }
        },
        onRegisterError(error) {
          console.error('SW registration error:', error)
        },
      })

      // Watch for updates
      watch(swNeedRefresh, (value) => {
        needRefresh.value = value
      }, { immediate: true })

      updateServiceWorker.value = swUpdate
    } catch (error) {
      // PWA registration not available (e.g., in dev without SW)
      console.debug('PWA registration not available:', error)
    }
  }

  onMounted(() => {
    if (import.meta.client) {
      window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
      window.addEventListener('appinstalled', handleAppInstalled)
      initPWA()
    }
  })

  onUnmounted(() => {
    if (import.meta.client) {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
      window.removeEventListener('appinstalled', handleAppInstalled)
    }
  })

  return {
    isInstallable,
    isInstalled,
    isDismissed,
    needRefresh,
    installApp,
    dismissInstall,
    refreshApp,
  }
}
