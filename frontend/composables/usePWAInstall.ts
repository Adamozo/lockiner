import { ref, watch, onMounted } from 'vue'

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
const isIOSSafari = ref(false)
const needRefresh = ref(false)
const isUpdateDismissed = ref(false)
const updateServiceWorker = ref<(() => Promise<void>) | null>(null)

// Capture beforeinstallprompt immediately at module level
// so it's not missed before onMounted runs
if (import.meta.client) {
  window.addEventListener('beforeinstallprompt', (e: Event) => {
    e.preventDefault()
    deferredPrompt.value = e as BeforeInstallPromptEvent
    isInstallable.value = true
  })

  window.addEventListener('appinstalled', () => {
    isInstalled.value = true
    isInstallable.value = false
    deferredPrompt.value = null
  })

  // Check if already running as installed PWA
  if (window.matchMedia('(display-mode: standalone)').matches
    || (navigator as any).standalone === true) {
    isInstalled.value = true
  }

  // Detect iOS Safari
  const ua = navigator.userAgent
  const isIOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  const isSafari = /Safari/.test(ua) && !/CriOS|FxiOS|Chrome/.test(ua)
  isIOSSafari.value = isIOS && isSafari
}

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

  const dismissUpdate = () => {
    isUpdateDismissed.value = true
    needRefresh.value = false
  }

  const initPWA = async () => {
    if (!import.meta.client) return

    checkDismissed()

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

      // Watch for updates (respect dismissed state)
      watch(swNeedRefresh, (value) => {
        if (value && !isUpdateDismissed.value) {
          needRefresh.value = true
        } else if (!value) {
          needRefresh.value = false
          isUpdateDismissed.value = false
        }
      }, { immediate: true })

      updateServiceWorker.value = swUpdate
    } catch (error) {
      // PWA registration not available (e.g., in dev without SW)
      console.debug('PWA registration not available:', error)
    }
  }

  onMounted(() => {
    initPWA()
  })

  return {
    isInstallable,
    isInstalled,
    isIOSSafari,
    isDismissed,
    needRefresh,
    installApp,
    dismissInstall,
    dismissUpdate,
    refreshApp,
  }
}
