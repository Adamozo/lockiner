<script setup lang="ts">
import type { NotificationItem } from '~/types/api'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: "default",
})

useSeoMeta({
  title: "Dashboard - LockIner",
  description: "Your personal life management hub",
})

const authStore = useAuthStore()
const { fetchNotifications, fetchUnreadCount } = useNotifications()

const recentNotifications = ref<NotificationItem[]>([])
const loadingNotifications = ref(true)

onMounted(async () => {
  try {
    recentNotifications.value = await fetchNotifications(0, 5)
    await fetchUnreadCount()
  } catch {
    // ignore
  } finally {
    loadingNotifications.value = false
  }
})

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

interface QuickLink {
  name: string
  icon: string
  to: string
  color: string
  description: string
}

const quickLinks: QuickLink[] = [
  { name: 'Finance', icon: 'i-heroicons-banknotes', to: '/finance', color: 'electric-green', description: 'Track expenses & receipts' },
  { name: 'Households', icon: 'i-heroicons-home-modern', to: '/households', color: 'cyber-blue', description: 'Manage shared finances' },
  { name: 'Fitness', icon: 'i-heroicons-fire', to: '/fitness', color: 'warning-orange', description: 'Track workouts & weight' },
  { name: 'Food', icon: 'i-heroicons-shopping-cart', to: '/food', color: 'electric-green', description: 'Food inventory & expiry' },
  { name: 'Journal', icon: 'i-heroicons-book-open', to: '/journal', color: 'cyber-blue', description: 'Daily reflection & reports' },
  { name: 'Skills', icon: 'i-heroicons-academic-cap', to: '/skills', color: 'cyber-blue', description: 'Learning journeys' },
]

const getColorClasses = (color: string) => {
  switch (color) {
    case 'electric-green': return 'border-electric-green/20 hover:border-electric-green/40 text-electric-green'
    case 'warning-orange': return 'border-warning-orange/20 hover:border-warning-orange/40 text-warning-orange'
    default: return 'border-cyber-blue/20 hover:border-cyber-blue/40 text-cyber-blue'
  }
}
</script>

<template>
  <div class="space-y-8">
    <!-- Welcome Header -->
    <header>
      <h1 class="text-3xl font-bold text-pure-white">
        Welcome back<span v-if="authStore.userName">, {{ authStore.userName }}</span>
      </h1>
      <p class="mt-1 text-pure-white/60">Your personal dashboard</p>
    </header>

    <!-- Recent Notifications -->
    <section>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-pure-white flex items-center gap-2">
          <UIcon name="i-heroicons-bell" class="w-5 h-5 text-cyber-blue" />
          Recent Notifications
        </h2>
        <NuxtLink
          to="/notifications"
          class="text-sm text-cyber-blue hover:text-cyber-blue/80 transition-colors"
        >
          View all
        </NuxtLink>
      </div>

      <div v-if="loadingNotifications" class="bg-card-black border border-border-gray rounded-xl p-6">
        <div class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-4 bg-border-gray rounded animate-pulse" :class="i === 3 ? 'w-1/2' : 'w-3/4'" />
        </div>
      </div>

      <div v-else-if="recentNotifications.length === 0" class="bg-card-black border border-border-gray rounded-xl p-6 text-center">
        <UIcon name="i-heroicons-bell-slash" class="w-10 h-10 text-pure-white/20 mx-auto mb-2" />
        <p class="text-pure-white/40 text-sm">No notifications</p>
      </div>

      <div v-else class="space-y-2">
        <NuxtLink
          v-for="item in recentNotifications"
          :key="item.id"
          to="/notifications"
          class="block bg-card-black border rounded-xl p-4 transition-all duration-200 hover:border-cyber-blue/30"
          :class="item.status === 'unread' ? 'border-cyber-blue/20' : 'border-border-gray'"
        >
          <div class="flex items-center gap-3">
            <div v-if="item.status === 'unread'" class="w-2 h-2 bg-cyber-blue rounded-full flex-shrink-0" />
            <div v-else class="w-2 h-2 flex-shrink-0" />
            <div class="flex-1 min-w-0">
              <p
                class="text-sm truncate"
                :class="item.status === 'unread' ? 'font-semibold text-pure-white' : 'text-pure-white/60'"
              >
                {{ item.title }}
              </p>
            </div>
            <span class="text-xs text-pure-white/30 flex-shrink-0">{{ formatDate(item.created_at) }}</span>
          </div>
        </NuxtLink>
      </div>
    </section>

    <!-- Quick Links -->
    <section>
      <h2 class="text-lg font-semibold text-pure-white mb-4">Modules</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <NuxtLink
          v-for="link in quickLinks"
          :key="link.name"
          :to="link.to"
          class="bg-card-black border rounded-xl p-5 transition-all duration-200"
          :class="getColorClasses(link.color)"
        >
          <div class="flex items-center gap-3 mb-2">
            <UIcon :name="link.icon" class="w-6 h-6" />
            <h3 class="font-semibold text-pure-white">{{ link.name }}</h3>
          </div>
          <p class="text-sm text-pure-white/40">{{ link.description }}</p>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>
