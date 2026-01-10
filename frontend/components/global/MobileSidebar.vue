<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

interface ModuleItem {
  name: string
  icon: string
  to: string
}

const modules: ModuleItem[] = [
  { name: 'Home', icon: 'i-heroicons-home', to: '/home' },
  { name: 'Finance', icon: 'i-heroicons-banknotes', to: '/finance' },
  { name: 'Households', icon: 'i-heroicons-home-modern', to: '/households' },
  { name: 'Fitness', icon: 'i-heroicons-fire', to: '/fitness' },
  { name: 'Skills', icon: 'i-heroicons-academic-cap', to: '/skills' },
  { name: 'Food', icon: 'i-heroicons-shopping-cart', to: '/food' },
]

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Mobile menu state
const menuOpen = ref(false)

// Initialize auth on mount
onMounted(() => {
  authStore.initialize()
})

// Close menu on route change
watch(() => route.path, () => {
  menuOpen.value = false
})

// Current module based on route
const currentModule = computed(() => {
  const found = modules.find(m => m.to !== '/home' && route.path.startsWith(m.to))
  return found?.to || '/home'
})

// Handle module change from select
const handleModuleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  router.push(target.value)
  menuOpen.value = false
}

// User initials for avatar
const userInitials = computed(() => {
  if (!authStore.userName) return '?'
  return authStore.userName.charAt(0).toUpperCase()
})

// Logout handler
const handleLogout = async () => {
  menuOpen.value = false
  await authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <!-- Mobile Header with Hamburger -->
  <header class="md:hidden sticky top-0 z-50 bg-background-black/95 backdrop-blur-glass border-b border-border-gray">
    <div class="px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <NuxtLink to="/home" class="flex items-center gap-2">
          <LockIcon :size="32" class="shrink-0" />
          <span class="font-bold text-lg">
            <span class="text-cyber-blue">Lock</span>
            <span class="text-electric-green">In</span>
            <span class="text-pure-white">er</span>
          </span>
        </NuxtLink>

        <!-- Hamburger Button -->
        <button
          class="p-2 rounded-lg text-pure-white/70 hover:text-pure-white hover:bg-card-black/50 transition-colors"
          @click="menuOpen = !menuOpen"
        >
          <UIcon
            :name="menuOpen ? 'i-heroicons-x-mark' : 'i-heroicons-bars-3'"
            class="w-6 h-6"
          />
        </button>
      </div>

      <!-- Mobile Dropdown Menu -->
      <nav v-if="menuOpen" class="mt-3 pt-3 border-t border-border-gray">
        <!-- Module Switcher -->
        <div class="mb-3">
          <label class="block text-xs font-medium text-pure-white/40 uppercase tracking-wider mb-2">Go to Module</label>
          <select
            :value="currentModule"
            @change="handleModuleChange"
            class="w-full px-3 py-2.5 bg-card-black border border-border-gray rounded-lg text-pure-white focus:outline-none focus:border-electric-green transition-colors"
          >
            <option v-for="mod in modules" :key="mod.to" :value="mod.to">
              {{ mod.name }}
            </option>
          </select>
        </div>

        <!-- Divider -->
        <div class="border-t border-border-gray my-3" />

        <!-- User Section -->
        <div v-if="authStore.isAuthenticated" class="space-y-1">
          <!-- Profile -->
          <NuxtLink
            to="/profile"
            class="flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200"
            :class="
              route.path === '/profile'
                ? 'text-electric-green bg-electric-green/10 border-l-2 border-electric-green'
                : 'text-pure-white/70 hover:text-pure-white hover:bg-card-black/50'
            "
          >
            <div class="w-5 h-5 rounded-full bg-gradient-to-br from-cyber-blue to-electric-green flex items-center justify-center text-xs font-bold text-background-black">
              {{ userInitials }}
            </div>
            <span class="font-medium">{{ authStore.userName }}</span>
          </NuxtLink>

          <!-- Settings -->
          <NuxtLink
            to="/settings"
            class="flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200"
            :class="
              route.path === '/settings'
                ? 'text-cyber-blue bg-cyber-blue/10 border-l-2 border-cyber-blue'
                : 'text-pure-white/70 hover:text-pure-white hover:bg-card-black/50'
            "
          >
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" />
            <span class="font-medium">Settings</span>
          </NuxtLink>

          <!-- Logout -->
          <button
            @click="handleLogout"
            class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-pure-white/70 hover:text-danger-red hover:bg-danger-red/10"
          >
            <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-5 h-5" />
            <span class="font-medium">Logout</span>
          </button>
        </div>

        <!-- Login Button (not authenticated) -->
        <NuxtLink
          v-else
          to="/login"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-pure-white/70 hover:text-electric-green hover:bg-electric-green/10"
        >
          <UIcon name="i-heroicons-arrow-right-end-on-rectangle" class="w-5 h-5" />
          <span class="font-medium">Login</span>
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>
