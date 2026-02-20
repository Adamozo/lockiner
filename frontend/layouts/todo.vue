<script setup lang="ts">
const todayPath = `/todo/${new Date().toISOString().split('T')[0]}`

const todoNavigation = [
  { label: 'Today', icon: 'i-heroicons-calendar-days', to: todayPath },
  { label: 'Stats', icon: 'i-heroicons-chart-bar', to: '/todo/stats' },
  { label: 'Reminder Rules', icon: 'i-heroicons-bell-alert', to: '/todo/notifications' },
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
        module-name="Todo"
        module-icon="i-heroicons-check-circle"
        module-color="electric-green"
        :navigation="todoNavigation"
      />

      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
