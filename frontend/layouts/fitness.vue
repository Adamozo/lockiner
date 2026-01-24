<script setup lang="ts">
// Fitness module layout with sidebar + fitness navbar

const fitnessNavigation = [
  { label: 'Dashboard', icon: 'i-heroicons-home', to: '/fitness' },
  { label: 'Workouts', icon: 'i-heroicons-fire', to: '/fitness/workouts' },
  { label: 'Weight', icon: 'i-heroicons-scale', to: '/fitness/weight' },
  { label: 'Progress', icon: 'i-heroicons-chart-bar', to: '/fitness/progress' },
]

// SSR-safe sidebar state using cookie
const { sidebarCollapsed } = useSidebarState()
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
        module-name="Fitness"
        module-icon="i-heroicons-fire"
        module-color="warning-orange"
        :navigation="fitnessNavigation"
      />

      <!-- Page Content -->
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
