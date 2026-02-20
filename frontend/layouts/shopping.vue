<script setup lang="ts">
const shoppingNavigation = [
  { label: 'Lists', icon: 'i-heroicons-list-bullet', to: '/shopping' },
  { label: 'Completed', icon: 'i-heroicons-check-circle', to: '/shopping/completed' },
]

const { sidebarCollapsed } = useSidebarState()
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <GlobalSidebar />

    <div
      class="min-h-screen transition-all duration-300"
      :class="sidebarCollapsed ? 'md:ml-16' : 'md:ml-56'"
    >
      <ModuleNavbar
        module-name="Shopping"
        module-icon="i-heroicons-shopping-bag"
        module-color="warning-orange"
        :navigation="shoppingNavigation"
      />

      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
