<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

interface NavItem {
  label: string
  icon: string
  to: string
}

interface ModuleItem {
  name: string
  icon: string
  to: string
  color: string
}

const props = defineProps<{
  moduleName: string
  moduleIcon: string
  moduleColor: 'cyber-blue' | 'electric-green' | 'warning-orange'
  navigation: NavItem[]
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isActive = (path: string) => route.path === path

// Mobile menu state
const mobileMenuOpen = ref(false)

// Close menu on route change
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

// All modules for switching
const allModules: ModuleItem[] = [
  { name: 'Home', icon: 'i-heroicons-home', to: '/home', color: 'cyber-blue' },
  { name: 'Finance', icon: 'i-heroicons-banknotes', to: '/finance', color: 'electric-green' },
  { name: 'Households', icon: 'i-heroicons-home-modern', to: '/households', color: 'cyber-blue' },
  { name: 'Fitness', icon: 'i-heroicons-fire', to: '/fitness', color: 'warning-orange' },
  { name: 'Skills', icon: 'i-heroicons-academic-cap', to: '/skills', color: 'cyber-blue' },
  { name: 'Food', icon: 'i-heroicons-shopping-cart', to: '/food', color: 'electric-green' },
]

// Current module based on route
const currentModule = computed(() => {
  const found = allModules.find(m => m.to !== '/home' && route.path.startsWith(m.to))
  return found?.to || '/home'
})

// Handle module change from select
const handleModuleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  router.push(target.value)
  mobileMenuOpen.value = false
}

// User initials
const userInitials = computed(() => {
  if (!authStore.userName) return '?'
  return authStore.userName.charAt(0).toUpperCase()
})

// Logout handler
const handleLogout = async () => {
  mobileMenuOpen.value = false
  await authStore.logout()
  await router.push('/login')
}

const colorClasses = computed(() => {
  switch (props.moduleColor) {
    case 'electric-green':
      return {
        title: 'text-electric-green',
        activeBg: 'bg-electric-green/10 border-l-2 border-electric-green',
        activeText: 'text-electric-green',
        hoverText: 'hover:text-electric-green',
      }
    case 'warning-orange':
      return {
        title: 'text-warning-orange',
        activeBg: 'bg-warning-orange/10 border-l-2 border-warning-orange',
        activeText: 'text-warning-orange',
        hoverText: 'hover:text-warning-orange',
      }
    case 'cyber-blue':
    default:
      return {
        title: 'text-cyber-blue',
        activeBg: 'bg-cyber-blue/10 border-l-2 border-cyber-blue',
        activeText: 'text-cyber-blue',
        hoverText: 'hover:text-cyber-blue',
      }
  }
})
</script>

<template>
  <header class="sticky top-0 z-40 bg-background-black/95 backdrop-blur-glass border-b border-border-gray overflow-hidden">
    <div class="px-4 py-3 min-[920px]:py-4">
      <div class="flex items-center justify-between gap-4">
        <!-- Module Title -->
        <div class="flex items-center space-x-2 min-[920px]:space-x-3 flex-shrink-0">
          <UIcon :name="moduleIcon" class="w-5 h-5 min-[920px]:w-7 min-[920px]:h-7" :class="colorClasses.title" />
          <h1 class="text-lg min-[920px]:text-xl font-bold text-pure-white">{{ moduleName }}</h1>
        </div>

        <!-- Desktop Navigation -->
        <nav class="hidden min-[920px]:flex items-center space-x-1 overflow-x-auto flex-shrink min-w-0">
          <NuxtLink
            v-for="item in navigation"
            :key="item.to"
            :to="item.to"
            class="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300"
            :class="
              isActive(item.to)
                ? [colorClasses.activeBg, colorClasses.activeText, 'font-medium shadow-lg']
                : ['text-pure-white/70 hover:bg-card-black/50', colorClasses.hoverText, 'hover:-translate-y-0.5']
            "
          >
            <UIcon :name="item.icon" class="w-5 h-5" />
            <span>{{ item.label }}</span>
          </NuxtLink>
        </nav>

        <!-- Mobile Hamburger Button -->
        <button
          class="min-[920px]:hidden p-2 rounded-lg text-pure-white/70 hover:text-pure-white hover:bg-card-black/50 transition-colors"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <UIcon
            :name="mobileMenuOpen ? 'i-heroicons-x-mark' : 'i-heroicons-bars-3'"
            class="w-6 h-6"
          />
        </button>
      </div>

      <!-- Mobile Dropdown Menu -->
      <nav
        v-if="mobileMenuOpen"
        class="min-[920px]:hidden mt-3 pt-3 border-t border-border-gray"
      >
        <!-- Current Module Pages -->
        <div class="space-y-1 mb-3">
          <p class="px-3 py-1 text-xs font-medium text-pure-white/40 uppercase tracking-wider">{{ moduleName }}</p>
          <NuxtLink
            v-for="item in navigation"
            :key="item.to"
            :to="item.to"
            class="flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200"
            :class="
              isActive(item.to)
                ? [colorClasses.activeBg, colorClasses.activeText, 'font-medium']
                : ['text-pure-white/70', colorClasses.hoverText, 'hover:bg-card-black/50']
            "
          >
            <UIcon :name="item.icon" class="w-5 h-5" />
            <span>{{ item.label }}</span>
          </NuxtLink>
        </div>

        <!-- Divider -->
        <div class="border-t border-border-gray my-3" />

        <!-- Module Switcher -->
        <div class="px-3 mb-3">
          <label class="block text-xs font-medium text-pure-white/40 uppercase tracking-wider mb-2">Switch Module</label>
          <select
            :value="currentModule"
            @change="handleModuleChange"
            class="w-full px-3 py-2.5 bg-card-black border border-border-gray rounded-lg text-pure-white focus:outline-none focus:border-electric-green transition-colors"
          >
            <option v-for="mod in allModules" :key="mod.to" :value="mod.to">
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
            <span>{{ authStore.userName }}</span>
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
            <span>Settings</span>
          </NuxtLink>

          <!-- Logout -->
          <button
            @click="handleLogout"
            class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-pure-white/70 hover:text-danger-red hover:bg-danger-red/10"
          >
            <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>

        <!-- Login (not authenticated) -->
        <NuxtLink
          v-else
          to="/login"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-pure-white/70 hover:text-electric-green hover:bg-electric-green/10"
        >
          <UIcon name="i-heroicons-arrow-right-end-on-rectangle" class="w-5 h-5" />
          <span>Login</span>
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>
