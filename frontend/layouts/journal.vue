<script setup lang="ts">
const today = new Date().toISOString().slice(0, 10)

const journalNavigation = [
  { label: 'Dashboard', icon: 'i-heroicons-home', to: '/journal' },
  { label: 'Today', icon: 'i-heroicons-pencil-square', to: `/journal/${today}` },
  { label: 'History', icon: 'i-heroicons-clock', to: '/journal/history' },
  { label: 'Meditation', icon: 'i-heroicons-moon', to: '/journal/meditation' },
  { label: 'Reports', icon: 'i-heroicons-chart-bar', to: '/journal/reports' },
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
        module-name="Journal"
        module-icon="i-heroicons-book-open"
        module-color="cyber-blue"
        :navigation="journalNavigation"
      />

      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
