<script setup lang="ts">
const { t } = useI18n()

const fitnessNavigation = computed(() => [
  { label: 'Dashboard', icon: 'i-heroicons-home', to: '/fitness' },
  { label: 'Workouts', icon: 'i-heroicons-fire', to: '/fitness/workouts' },
  { label: 'Measurements', icon: 'i-heroicons-clipboard-document-list', to: '/fitness/measurements' },
  { label: 'Progress', icon: 'i-heroicons-chart-bar', to: '/fitness/progress' },
  { label: t('food.nav_calories'), icon: 'i-heroicons-cake', to: '/fitness/nutrition' },
  { label: 'Medicines', icon: 'i-heroicons-beaker', to: '/fitness/medicines' },
])

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
        module-name="Fitness"
        module-icon="i-heroicons-fire"
        module-color="warning-orange"
        :navigation="fitnessNavigation"
      />
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
