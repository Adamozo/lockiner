<script setup lang="ts">
// Food module layout with sidebar + food navbar

const foodNavigation = [
  { label: 'Inventory', icon: 'i-heroicons-archive-box', to: '/food' },
  { label: 'Imports', icon: 'i-heroicons-inbox-arrow-down', to: '/food/imports' },
  { label: 'Recipes', icon: 'i-heroicons-book-open', to: '/food/recipes' },
  { label: 'Settings', icon: 'i-heroicons-cog-6-tooth', to: '/food/settings' },
]

// Check sidebar collapsed state for main content margin
const sidebarCollapsed = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('sidebar-collapsed')
  sidebarCollapsed.value = saved === 'true'

  // Watch for changes from sidebar toggle
  const checkSidebar = () => {
    const saved = localStorage.getItem('sidebar-collapsed')
    sidebarCollapsed.value = saved === 'true'
  }

  const interval = setInterval(checkSidebar, 100)
  onUnmounted(() => clearInterval(interval))
})
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <!-- Global Sidebar (desktop) -->
    <GlobalSidebar />

    <!-- Main Content Area with Module Navbar -->
    <div
      class="min-h-screen transition-all duration-300"
      :class="sidebarCollapsed ? 'md:ml-16' : 'md:ml-56'"
    >
      <!-- Module Navbar -->
      <ModuleNavbar
        module-name="Food"
        module-icon="i-heroicons-shopping-cart"
        module-color="electric-green"
        :navigation="foodNavigation"
      />

      <!-- Page Content -->
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
