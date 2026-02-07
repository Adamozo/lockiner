<script setup lang="ts">
import type { NotificationItem } from '~/types/api'

definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: 'Notifications - LockIner',
  description: 'Your notifications',
})

const { fetchNotifications, fetchUnreadCount, markAsRead, markAsUnread, markAllAsRead, deleteNotification } = useNotifications()

const notifications = ref<NotificationItem[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(true)
const PAGE_SIZE = 20

const loadNotifications = async () => {
  loading.value = true
  try {
    notifications.value = await fetchNotifications(0, PAGE_SIZE)
    hasMore.value = notifications.value.length >= PAGE_SIZE
  } catch (e) {
    console.error('Failed to load notifications:', e)
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  try {
    const more = await fetchNotifications(notifications.value.length, PAGE_SIZE)
    notifications.value.push(...more)
    hasMore.value = more.length >= PAGE_SIZE
  } catch (e) {
    console.error('Failed to load more:', e)
  } finally {
    loadingMore.value = false
  }
}

const handleMarkAllRead = async () => {
  await markAllAsRead()
  notifications.value.forEach(n => { n.status = 'read' })
}

const handleToggleRead = async (item: NotificationItem) => {
  if (item.status === 'unread') {
    await markAsRead(item.id)
    item.status = 'read'
  } else {
    await markAsUnread(item.id)
    item.status = 'unread'
  }
  await fetchUnreadCount()
}

const handleDelete = async (item: NotificationItem) => {
  await deleteNotification(item.id)
  notifications.value = notifications.value.filter(n => n.id !== item.id)
  await fetchUnreadCount()
}

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('pl-PL', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const typeIcon = (type: string) => {
  switch (type) {
    case 'alert': return 'i-heroicons-exclamation-triangle'
    case 'system': return 'i-heroicons-cog-6-tooth'
    default: return 'i-heroicons-bell'
  }
}

const typeColor = (type: string) => {
  switch (type) {
    case 'alert': return 'text-warning-orange'
    case 'system': return 'text-cyber-blue'
    default: return 'text-electric-green'
  }
}

onMounted(async () => {
  await loadNotifications()
  // Auto-mark all as read when visiting
  await markAllAsRead()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-pure-white">Notifications</h1>
        <p class="mt-1 text-pure-white/60">Your notification center</p>
      </div>
      <button
        v-if="notifications.some(n => n.status === 'unread')"
        @click="handleMarkAllRead"
        class="px-4 py-2 text-sm bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg text-cyber-blue hover:bg-cyber-blue/20 transition-colors"
      >
        Mark all as read
      </button>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="space-y-4">
      <div v-for="i in 5" :key="i" class="bg-card-black border border-border-gray rounded-xl p-4 animate-pulse">
        <div class="h-4 bg-border-gray rounded w-1/3 mb-2" />
        <div class="h-3 bg-border-gray rounded w-2/3" />
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="notifications.length === 0" class="text-center py-16">
      <UIcon name="i-heroicons-bell-slash" class="w-16 h-16 text-pure-white/20 mx-auto mb-4" />
      <p class="text-pure-white/40 text-lg">No notifications yet</p>
    </div>

    <!-- Notification list -->
    <div v-else class="space-y-3">
      <div
        v-for="item in notifications"
        :key="item.id"
        class="bg-card-black border rounded-xl p-4 transition-all duration-200"
        :class="item.status === 'unread'
          ? 'border-cyber-blue/30 bg-cyber-blue/5'
          : 'border-border-gray'"
      >
        <div class="flex items-start gap-3">
          <!-- Type icon -->
          <div class="flex-shrink-0 mt-0.5">
            <UIcon :name="typeIcon(item.notification_type)" class="w-5 h-5" :class="typeColor(item.notification_type)" />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h3
                class="text-sm truncate"
                :class="item.status === 'unread' ? 'font-bold text-pure-white' : 'font-medium text-pure-white/70'"
              >
                {{ item.title }}
              </h3>
              <div v-if="item.status === 'unread'" class="w-2 h-2 bg-cyber-blue rounded-full flex-shrink-0" />
            </div>
            <p class="text-sm text-pure-white/50 mt-1">{{ item.body }}</p>
            <p class="text-xs text-pure-white/30 mt-2">{{ formatDate(item.created_at) }}</p>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-1 flex-shrink-0">
            <button
              @click="handleToggleRead(item)"
              class="p-1.5 rounded-lg text-pure-white/40 hover:text-pure-white hover:bg-background-black/50 transition-colors"
              :title="item.status === 'unread' ? 'Mark as read' : 'Mark as unread'"
            >
              <UIcon
                :name="item.status === 'unread' ? 'i-heroicons-envelope-open' : 'i-heroicons-envelope'"
                class="w-4 h-4"
              />
            </button>
            <button
              @click="handleDelete(item)"
              class="p-1.5 rounded-lg text-pure-white/40 hover:text-danger-red hover:bg-danger-red/10 transition-colors"
              title="Delete"
            >
              <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Load more -->
      <div v-if="hasMore" class="text-center pt-4">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="px-6 py-2 text-sm bg-card-black border border-border-gray rounded-lg text-pure-white/60 hover:text-pure-white hover:border-cyber-blue/30 transition-colors disabled:opacity-50"
        >
          {{ loadingMore ? 'Loading...' : 'Load more' }}
        </button>
      </div>
    </div>
  </div>
</template>
