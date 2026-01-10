<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

interface ModuleItem {
  name: string
  icon: string
  to: string
  color: string
}

const modules: ModuleItem[] = [
  {
    name: 'Home',
    icon: 'i-heroicons-home',
    to: '/home',
    color: 'cyber-blue',
  },
  {
    name: 'Finance',
    icon: 'i-heroicons-banknotes',
    to: '/finance',
    color: 'electric-green',
  },
  {
    name: 'Households',
    icon: 'i-heroicons-home-modern',
    to: '/households',
    color: 'cyber-blue',
  },
  {
    name: 'Fitness',
    icon: 'i-heroicons-fire',
    to: '/fitness',
    color: 'warning-orange',
  },
  {
    name: 'Skills',
    icon: 'i-heroicons-academic-cap',
    to: '/skills',
    color: 'cyber-blue',
  },
  {
    name: 'Food',
    icon: 'i-heroicons-shopping-cart',
    to: '/food',
    color: 'electric-green',
  },
]

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Initialize auth store on mount
onMounted(() => {
  authStore.initialize()
  if (authStore.accessToken && !authStore.user) {
    authStore.fetchCurrentUser()
  }
})

// Sidebar collapsed state with localStorage persistence
const isCollapsed = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('sidebar-collapsed')
  if (saved !== null) {
    isCollapsed.value = saved === 'true'
  }
})

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebar-collapsed', String(isCollapsed.value))
}

const isActiveModule = (path: string) => {
  if (path === '/home') return route.path === '/home'
  return route.path.startsWith(path)
}

const getColorClass = (color: string, isActive: boolean) => {
  if (!isActive) return 'text-pure-white/60 hover:text-pure-white'
  switch (color) {
    case 'electric-green':
      return 'text-electric-green'
    case 'warning-orange':
      return 'text-warning-orange'
    case 'cyber-blue':
    default:
      return 'text-cyber-blue'
  }
}

const getBgClass = (color: string, isActive: boolean) => {
  if (!isActive) return 'hover:bg-card-black/50'
  switch (color) {
    case 'electric-green':
      return 'bg-electric-green/10 border-l-2 border-electric-green'
    case 'warning-orange':
      return 'bg-warning-orange/10 border-l-2 border-warning-orange'
    case 'cyber-blue':
    default:
      return 'bg-cyber-blue/10 border-l-2 border-cyber-blue'
  }
}

// Auth actions
const handleLogout = async () => {
  await authStore.logout()
  await router.push('/login')
}

// Get user initials for avatar
const userInitials = computed(() => {
  if (!authStore.userName) return '?'
  return authStore.userName.charAt(0).toUpperCase()
})
</script>

<template>
  <aside
    class="fixed left-0 top-0 h-full bg-card-black border-r border-border-gray z-50 flex-col transition-all duration-300 hidden md:flex"
    :class="isCollapsed ? 'w-16' : 'w-56'"
  >
    <!-- Logo / Toggle -->
    <div class="p-4 border-b border-border-gray flex items-center" :class="isCollapsed ? 'justify-center' : 'justify-between'">
      <NuxtLink v-if="!isCollapsed" to="/" class="flex items-center space-x-2 group">
        <LockIcon :size="32" class="group-hover:scale-110 transition-transform" />
        <span class="font-bold"><span class="text-cyber-blue">Lock</span><span class="text-electric-green">In</span><span class="text-pure-white">er</span></span>
      </NuxtLink>
      <button
        @click="toggleSidebar"
        class="p-2 rounded-lg hover:bg-background-black/50 text-pure-white/60 hover:text-pure-white transition-colors"
        :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <UIcon
          :name="isCollapsed ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-left'"
          class="w-5 h-5"
        />
      </button>
    </div>

    <!-- Module Navigation -->
    <nav class="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
      <NuxtLink
        v-for="mod in modules"
        :key="mod.name"
        :to="mod.to"
        class="flex items-center rounded-lg transition-all duration-200"
        :class="[
          isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3',
          getColorClass(mod.color, isActiveModule(mod.to)),
          getBgClass(mod.color, isActiveModule(mod.to)),
        ]"
        :title="isCollapsed ? mod.name : undefined"
      >
        <UIcon :name="mod.icon" class="w-5 h-5 flex-shrink-0" />
        <span v-if="!isCollapsed" class="font-medium">{{ mod.name }}</span>
      </NuxtLink>
    </nav>

    <!-- Bottom section: Household Context -->
    <div class="p-2 border-t border-border-gray space-y-1">
      <!-- Household Selector -->
      <HouseholdSelector :collapsed="isCollapsed" />
    </div>

    <!-- User section at very bottom -->
    <div class="p-2 border-t border-border-gray space-y-1">
      <!-- Logged in: User info, Settings & Logout -->
      <div v-if="authStore.isAuthenticated" class="space-y-1">
        <!-- User info (expanded) - clickable to profile -->
        <NuxtLink
          v-if="!isCollapsed"
          to="/profile"
          class="flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 hover:bg-card-black/50"
          :class="route.path === '/profile' ? 'bg-electric-green/10 border-l-2 border-electric-green' : ''"
        >
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-cyber-blue to-electric-green flex items-center justify-center text-sm font-bold text-background-black flex-shrink-0">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-pure-white truncate">{{ authStore.userName }}</p>
            <p class="text-xs text-pure-white/60 truncate">{{ authStore.userEmail }}</p>
          </div>
        </NuxtLink>

        <!-- User avatar only (collapsed) - clickable to profile -->
        <NuxtLink
          v-else
          to="/profile"
          class="flex justify-center py-2 rounded-lg transition-all duration-200 hover:bg-card-black/50"
          :class="route.path === '/profile' ? 'bg-electric-green/10' : ''"
          :title="authStore.userName + ' - Profile'"
        >
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-cyber-blue to-electric-green flex items-center justify-center text-sm font-bold text-background-black">
            {{ userInitials }}
          </div>
        </NuxtLink>

        <!-- Settings -->
        <NuxtLink
          to="/settings"
          class="flex items-center rounded-lg transition-all duration-200"
          :class="[
            isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3',
            route.path === '/settings'
              ? 'text-cyber-blue bg-cyber-blue/10 border-l-2 border-cyber-blue'
              : 'text-pure-white/60 hover:text-pure-white hover:bg-card-black/50',
          ]"
          :title="isCollapsed ? 'Settings' : undefined"
        >
          <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 flex-shrink-0" />
          <span v-if="!isCollapsed" class="font-medium">Settings</span>
        </NuxtLink>

        <!-- Logout button -->
        <button
          @click="handleLogout"
          class="w-full flex items-center rounded-lg transition-all duration-200 text-pure-white/60 hover:text-danger-red hover:bg-danger-red/10"
          :class="isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3'"
          :title="isCollapsed ? 'Logout' : undefined"
        >
          <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-5 h-5 flex-shrink-0" />
          <span v-if="!isCollapsed" class="font-medium">Logout</span>
        </button>
      </div>

      <!-- Not logged in: Login button -->
      <NuxtLink
        v-else
        to="/login"
        class="w-full flex items-center rounded-lg transition-all duration-200 text-pure-white/60 hover:text-electric-green hover:bg-electric-green/10"
        :class="isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3'"
        :title="isCollapsed ? 'Login' : undefined"
      >
        <UIcon name="i-heroicons-arrow-right-end-on-rectangle" class="w-5 h-5 flex-shrink-0" />
        <span v-if="!isCollapsed" class="font-medium">Login</span>
      </NuxtLink>
    </div>
  </aside>
</template>
