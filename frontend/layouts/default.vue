<script setup lang="ts">
// Default layout with sidebar only (for home and settings pages)
// No module-specific navbar

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

  // Poll for changes (since storage event only fires in other tabs)
  const interval = setInterval(checkSidebar, 100)
  onUnmounted(() => clearInterval(interval))
})
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <!-- Global Sidebar (desktop) -->
    <GlobalSidebar />

    <!-- Mobile Bottom Navigation -->
    <MobileSidebar />

    <!-- Main Content Area -->
    <main
      class="min-h-screen transition-all duration-300"
      :class="sidebarCollapsed ? 'md:ml-16' : 'md:ml-56'"
    >
      <div class="container mx-auto px-4 py-6">
        <slot />
      </div>
    </main>
  </div>
</template>
