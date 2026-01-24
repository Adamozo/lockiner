import { ref, onMounted, onUnmounted } from 'vue'

const isOnline = ref(true)

export function useNetworkStatus() {
  const updateOnlineStatus = () => {
    if (import.meta.client) {
      isOnline.value = navigator.onLine
    }
  }

  onMounted(() => {
    if (import.meta.client) {
      isOnline.value = navigator.onLine
      window.addEventListener('online', updateOnlineStatus)
      window.addEventListener('offline', updateOnlineStatus)
    }
  })

  onUnmounted(() => {
    if (import.meta.client) {
      window.removeEventListener('online', updateOnlineStatus)
      window.removeEventListener('offline', updateOnlineStatus)
    }
  })

  return {
    isOnline,
  }
}
