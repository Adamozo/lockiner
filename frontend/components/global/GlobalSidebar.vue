<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const { t } = useI18n()

interface ModuleItem {
  nameKey: string;
  icon: string;
  to: string;
  color: string;
}

const modules: ModuleItem[] = [
  { nameKey: "nav.home",        icon: "i-heroicons-home",           to: "/home",       color: "cyber-blue" },
  { nameKey: "nav.finance",     icon: "i-heroicons-banknotes",      to: "/finance",    color: "electric-green" },
  { nameKey: "nav.fitness",     icon: "i-heroicons-fire",           to: "/fitness",    color: "warning-orange" },
  { nameKey: "nav.households",  icon: "i-heroicons-home-modern",    to: "/households", color: "cyber-blue" },
  { nameKey: "nav.food",        icon: "i-heroicons-shopping-cart",  to: "/food",       color: "electric-green" },
  { nameKey: "nav.shopping",    icon: "i-heroicons-shopping-bag",   to: "/shopping",   color: "warning-orange" },
  { nameKey: "nav.journal",     icon: "i-heroicons-book-open",      to: "/journal",    color: "cyber-blue" },
  { nameKey: "nav.todo",        icon: "i-heroicons-check-circle",   to: "/todo",       color: "electric-green" },
  // TODO: unhide when skills module is ready
  // { nameKey: "nav.skills",      icon: "i-heroicons-academic-cap",   to: "/skills",     color: "cyber-blue" },
];

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { unreadCount, fetchUnreadCount } = useNotifications();

// SSR-safe sidebar state using cookie
const { sidebarCollapsed: isCollapsed, toggleSidebar } = useSidebarState();

// Fetch user data and unread count on mount
let unreadInterval: ReturnType<typeof setInterval> | null = null;
onMounted(() => {
  if (authStore.accessToken && !authStore.user) {
    authStore.fetchCurrentUser();
  }
  if (authStore.accessToken) {
    fetchUnreadCount();
    // Poll every 60s
    unreadInterval = setInterval(() => {
      if (authStore.isAuthenticated) fetchUnreadCount();
    }, 60000);
  }
});
onUnmounted(() => {
  if (unreadInterval) clearInterval(unreadInterval);
});

const isActiveModule = (path: string) => {
  if (path === "/home") return route.path === "/home";
  return route.path.startsWith(path);
};

const getColorClass = (color: string, isActive: boolean) => {
  if (!isActive) return "text-pure-white/60 hover:text-pure-white";
  switch (color) {
    case "electric-green":
      return "text-electric-green";
    case "warning-orange":
      return "text-warning-orange";
    case "cyber-blue":
    default:
      return "text-cyber-blue";
  }
};

const getBgClass = (color: string, isActive: boolean) => {
  if (!isActive) return "hover:bg-card-black/50";
  switch (color) {
    case "electric-green":
      return "bg-electric-green/10 border-l-2 border-electric-green";
    case "warning-orange":
      return "bg-warning-orange/10 border-l-2 border-warning-orange";
    case "cyber-blue":
    default:
      return "bg-cyber-blue/10 border-l-2 border-cyber-blue";
  }
};

// Auth actions
const handleLogout = async () => {
  await authStore.logout();
  await router.push("/login");
};

// Get user initials for avatar
const userInitials = computed(() => {
  if (!authStore.userName) return "?";
  return authStore.userName.charAt(0).toUpperCase();
});

// User menu dropdown state
const isUserMenuOpen = ref(false);
const userMenuRef = ref<HTMLElement | null>(null);

// Close user menu on outside click
const handleUserMenuClickOutside = (event: MouseEvent) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    isUserMenuOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleUserMenuClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleUserMenuClickOutside);
});
</script>

<template>
  <aside
    class="fixed left-0 top-0 h-full bg-card-black border-r border-border-gray z-50 flex-col transition-all duration-300 hidden md:flex"
    :class="isCollapsed ? 'w-16' : 'w-56'"
  >
    <!-- Logo / Toggle -->
    <div
      class="p-4 border-b border-border-gray flex items-center"
      :class="isCollapsed ? 'justify-center' : 'justify-between'"
    >
      <NuxtLink
        v-if="!isCollapsed"
        to="/home"
        class="flex items-center space-x-2 group"
      >
        <LockIcon
          :size="32"
          class="group-hover:scale-110 transition-transform"
        />
        <span class="font-bold"
          ><span class="text-cyber-blue">Lock</span
          ><span class="text-electric-green">In</span
          ><span class="text-pure-white">er</span></span
        >
      </NuxtLink>
      <button
        @click="toggleSidebar"
        class="p-2 rounded-lg hover:bg-background-black/50 text-pure-white/60 hover:text-pure-white transition-colors"
        :title="isCollapsed ? $t('nav.expand_sidebar') : $t('nav.collapse_sidebar')"
      >
        <UIcon
          :name="
            isCollapsed
              ? 'i-heroicons-chevron-right'
              : 'i-heroicons-chevron-left'
          "
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
        :title="isCollapsed ? $t(mod.nameKey) : undefined"
      >
        <UIcon :name="mod.icon" class="w-5 h-5 flex-shrink-0" />
        <span v-if="!isCollapsed" class="font-medium">{{ $t(mod.nameKey) }}</span>
      </NuxtLink>

      <!-- Divider -->
      <div class="border-t border-border-gray my-2" />

      <!-- Notifications -->
      <NuxtLink
        to="/notifications"
        class="flex items-center rounded-lg transition-all duration-200 relative"
        :class="[
          isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3',
          route.path === '/notifications'
            ? 'text-cyber-blue bg-cyber-blue/10 border-l-2 border-cyber-blue'
            : 'text-pure-white/60 hover:text-pure-white hover:bg-card-black/50',
        ]"
        :title="isCollapsed ? $t('nav.notifications') : undefined"
      >
        <div class="relative">
          <UIcon name="i-heroicons-bell" class="w-5 h-5 flex-shrink-0" />
          <span
            v-if="unreadCount > 0"
            class="absolute -top-1.5 -right-1.5 min-w-[16px] h-4 px-1 bg-danger-red text-pure-white text-[10px] font-bold rounded-full flex items-center justify-center"
          >
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </span>
        </div>
        <span v-if="!isCollapsed" class="font-medium">{{ $t('nav.notifications') }}</span>
      </NuxtLink>

      <!-- Admin (conditional) -->
      <NuxtLink
        v-if="authStore.isAdmin"
        to="/admin"
        class="flex items-center rounded-lg transition-all duration-200"
        :class="[
          isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3',
          route.path.startsWith('/admin')
            ? 'text-warning-orange bg-warning-orange/10 border-l-2 border-warning-orange'
            : 'text-pure-white/60 hover:text-pure-white hover:bg-card-black/50',
        ]"
        :title="isCollapsed ? $t('nav.admin') : undefined"
      >
        <UIcon name="i-heroicons-shield-check" class="w-5 h-5 flex-shrink-0" />
        <span v-if="!isCollapsed" class="font-medium">{{ $t('nav.admin') }}</span>
      </NuxtLink>
    </nav>

    <!-- Bottom section: Household Context -->
    <div class="p-2 border-t border-border-gray space-y-1">
      <!-- Household Selector -->
      <HouseholdSelector :collapsed="isCollapsed" />
    </div>

    <!-- User section at very bottom -->
    <div class="p-2 border-t border-border-gray">
      <!-- Logged in: User menu dropdown -->
      <div v-if="authStore.isAuthenticated" ref="userMenuRef" class="relative">
        <!-- Trigger Button -->
        <button
          @click="isUserMenuOpen = !isUserMenuOpen"
          class="w-full flex items-center rounded-lg transition-all duration-200 text-pure-white/60 hover:text-pure-white hover:bg-card-black/50"
          :class="isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-2 space-x-3'"
          :title="isCollapsed ? authStore.userName : undefined"
        >
          <div
            class="w-8 h-8 rounded-full bg-gradient-to-br from-cyber-blue to-electric-green flex items-center justify-center text-sm font-bold text-background-black flex-shrink-0"
          >
            {{ userInitials }}
          </div>
          <template v-if="!isCollapsed">
            <div class="flex-1 min-w-0 text-left">
              <p class="text-sm font-medium text-pure-white truncate">
                {{ authStore.userName }}
              </p>
            </div>
            <UIcon
              :name="isUserMenuOpen ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
              class="w-4 h-4 flex-shrink-0"
            />
          </template>
        </button>

        <!-- Dropdown Menu -->
        <Transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div
            v-if="isUserMenuOpen"
            class="absolute z-50 bg-card-black border border-border-gray rounded-lg shadow-xl overflow-hidden min-w-[200px] left-full ml-2 bottom-0"
          >
            <div class="p-1">
              <!-- Profile -->
              <NuxtLink
                to="/profile"
                @click="isUserMenuOpen = false"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-left transition-colors"
                :class="route.path === '/profile'
                  ? 'bg-electric-green/10 text-electric-green'
                  : 'text-pure-white/80 hover:bg-background-black/50'"
              >
                <UIcon name="i-heroicons-user-circle" class="w-5 h-5 flex-shrink-0" />
                <span class="font-medium">{{ $t('nav.profile') }}</span>
                <UIcon
                  v-if="route.path === '/profile'"
                  name="i-heroicons-check"
                  class="w-4 h-4 ml-auto"
                />
              </NuxtLink>

              <!-- Settings -->
              <NuxtLink
                to="/settings"
                @click="isUserMenuOpen = false"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-left transition-colors"
                :class="route.path === '/settings'
                  ? 'bg-cyber-blue/10 text-cyber-blue'
                  : 'text-pure-white/80 hover:bg-background-black/50'"
              >
                <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 flex-shrink-0" />
                <span class="font-medium">{{ $t('nav.settings') }}</span>
                <UIcon
                  v-if="route.path === '/settings'"
                  name="i-heroicons-check"
                  class="w-4 h-4 ml-auto"
                />
              </NuxtLink>

              <!-- Divider -->
              <div class="my-1 border-t border-border-gray" />

              <!-- Logout -->
              <button
                @click="handleLogout"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-left text-pure-white/80 hover:text-danger-red hover:bg-danger-red/10 transition-colors"
              >
                <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-5 h-5 flex-shrink-0" />
                <span class="font-medium">{{ $t('nav.logout') }}</span>
              </button>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Not logged in: Login button -->
      <NuxtLink
        v-else
        to="/login"
        class="w-full flex items-center rounded-lg transition-all duration-200 text-pure-white/60 hover:text-electric-green hover:bg-electric-green/10"
        :class="
          isCollapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3'
        "
        :title="isCollapsed ? $t('nav.login') : undefined"
      >
        <UIcon
          name="i-heroicons-arrow-right-end-on-rectangle"
          class="w-5 h-5 flex-shrink-0"
        />
        <span v-if="!isCollapsed" class="font-medium">{{ $t('nav.login') }}</span>
      </NuxtLink>
    </div>
  </aside>
</template>
