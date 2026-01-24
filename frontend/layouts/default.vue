<script setup lang="ts">
// Default layout with sidebar only (for home and settings pages)
// No module-specific navbar

// SSR-safe sidebar state using cookie
const { sidebarCollapsed } = useSidebarState()
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
