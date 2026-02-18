<script setup lang="ts">
import type { DevicePushSubscription } from '~/types/api'

const { fetchSubscriptions, deleteSubscription, subscribeToPush, getCurrentEndpoint } = useNotifications()

const subscriptions = ref<DevicePushSubscription[]>([])
const loading = ref(true)
const currentEndpoint = ref<string | null>(null)
const deletingId = ref<number | null>(null)
const subscribing = ref(false)
const expanded = ref(true)

const canSubscribe = computed(() =>
  currentEndpoint.value !== null
    ? !subscriptions.value.some(s => s.endpoint === currentEndpoint.value)
    : false
)

const notificationPermission = ref<NotificationPermission>('default')

onMounted(async () => {
  if ('Notification' in window) {
    notificationPermission.value = Notification.permission
  }
  const [subs, endpoint] = await Promise.all([
    fetchSubscriptions(),
    getCurrentEndpoint(),
  ])
  subscriptions.value = subs
  currentEndpoint.value = endpoint
  loading.value = false
})

const handleDelete = async (sub: DevicePushSubscription) => {
  deletingId.value = sub.id
  try {
    await deleteSubscription(sub.id)
    subscriptions.value = subscriptions.value.filter(s => s.id !== sub.id)
    if (sub.endpoint === currentEndpoint.value) {
      currentEndpoint.value = null
    }
  } finally {
    deletingId.value = null
  }
}

const handleSubscribe = async () => {
  subscribing.value = true
  try {
    const ok = await subscribeToPush()
    if (ok) {
      subscriptions.value = await fetchSubscriptions()
      currentEndpoint.value = await getCurrentEndpoint()
      notificationPermission.value = Notification.permission
    }
  } finally {
    subscribing.value = false
  }
}

function getDeviceLabel(endpoint: string): string {
  if (endpoint.includes('fcm.googleapis.com')) return 'Chrome'
  if (endpoint.includes('web.push.apple.com')) return 'Safari'
  if (endpoint.includes('mozilla.com')) return 'Firefox'
  if (endpoint.includes('windows.com') || endpoint.includes('microsoft.com')) return 'Edge'
  return 'Browser'
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffDays = Math.floor(diffMs / 86400000)
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
    <!-- Section header -->
    <button
      class="w-full flex items-center justify-between px-5 py-4 hover:bg-background-black/40 transition-colors"
      @click="expanded = !expanded"
    >
      <div class="flex items-center gap-3">
        <UIcon name="i-heroicons-device-phone-mobile" class="w-5 h-5 text-cyber-blue" />
        <span class="text-sm font-semibold text-pure-white">Push notification devices</span>
        <span
          v-if="!loading"
          class="text-xs bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/20 rounded-full px-2 py-0.5"
        >
          {{ subscriptions.length }}
        </span>
      </div>
      <UIcon
        :name="expanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
        class="w-4 h-4 text-pure-white/40"
      />
    </button>

    <!-- Body -->
    <div v-if="expanded" class="border-t border-border-gray">
      <!-- Loading skeleton -->
      <div v-if="loading" class="p-4 space-y-3">
        <div v-for="i in 2" :key="i" class="flex items-center gap-3 animate-pulse">
          <div class="w-9 h-9 bg-border-gray rounded-lg flex-shrink-0" />
          <div class="flex-1 space-y-1.5">
            <div class="h-3.5 bg-border-gray rounded w-1/3" />
            <div class="h-3 bg-border-gray rounded w-1/4" />
          </div>
        </div>
      </div>

      <!-- Permission denied notice -->
      <div
        v-else-if="notificationPermission === 'denied'"
        class="px-5 py-4 flex items-center gap-3 text-sm text-warning-orange/80"
      >
        <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 flex-shrink-0" />
        <span>Notifications are blocked in your browser settings. Change them to enable push notifications on this device.</span>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="subscriptions.length === 0"
        class="px-5 py-8 text-center"
      >
        <UIcon name="i-heroicons-bell-slash" class="w-10 h-10 text-pure-white/20 mx-auto mb-3" />
        <p class="text-sm text-pure-white/40 mb-4">No devices subscribed yet</p>
        <button
          class="px-4 py-2 text-sm bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg text-cyber-blue hover:bg-cyber-blue/20 transition-colors disabled:opacity-50"
          :disabled="subscribing"
          @click="handleSubscribe"
        >
          {{ subscribing ? 'Subscribing...' : 'Subscribe this device' }}
        </button>
      </div>

      <!-- Subscription list -->
      <div v-else class="divide-y divide-border-gray">
        <div
          v-for="sub in subscriptions"
          :key="sub.id"
          class="flex items-center gap-3 px-5 py-3.5"
        >
          <!-- Device icon -->
          <div class="w-9 h-9 bg-background-black border border-border-gray rounded-lg flex items-center justify-center flex-shrink-0">
            <UIcon name="i-heroicons-device-phone-mobile" class="w-4 h-4 text-pure-white/50" />
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-sm font-medium text-pure-white">{{ getDeviceLabel(sub.endpoint) }}</span>
              <span
                v-if="sub.endpoint === currentEndpoint"
                class="text-xs bg-electric-green/10 text-electric-green border border-electric-green/20 rounded-full px-2 py-0.5"
              >
                This device
              </span>
            </div>
            <p class="text-xs text-pure-white/40 mt-0.5">Subscribed {{ formatDate(sub.created_at) }}</p>
          </div>

          <!-- Revoke button -->
          <button
            class="flex-shrink-0 p-1.5 rounded-lg text-pure-white/40 hover:text-danger-red hover:bg-danger-red/10 transition-colors disabled:opacity-30"
            :disabled="deletingId === sub.id"
            :title="sub.endpoint === currentEndpoint ? 'Unsubscribe this device' : 'Revoke'"
            @click="handleDelete(sub)"
          >
            <UIcon
              :name="deletingId === sub.id ? 'i-heroicons-arrow-path' : 'i-heroicons-trash'"
              class="w-4 h-4"
              :class="deletingId === sub.id ? 'animate-spin' : ''"
            />
          </button>
        </div>

        <!-- Subscribe this device CTA (when not yet subscribed) -->
        <div v-if="canSubscribe" class="px-5 py-3.5">
          <button
            class="w-full flex items-center justify-center gap-2 py-2 text-sm bg-cyber-blue/10 border border-cyber-blue/20 border-dashed rounded-lg text-cyber-blue hover:bg-cyber-blue/20 transition-colors disabled:opacity-50"
            :disabled="subscribing"
            @click="handleSubscribe"
          >
            <UIcon name="i-heroicons-plus" class="w-4 h-4" />
            {{ subscribing ? 'Subscribing...' : 'Subscribe this device' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
