<script setup lang="ts">
const { t } = useI18n()

const foodNavigation = computed(() => [
  { label: t('food.nav_inventory'), icon: 'i-heroicons-archive-box', to: '/food' },
  { label: t('food.nav_today'), icon: 'i-heroicons-sun', to: '/food/today' },
  { label: t('food.nav_imports'), icon: 'i-heroicons-inbox-arrow-down', to: '/food/imports' },
  { label: t('food.nav_recipes'), icon: 'i-heroicons-book-open', to: '/food/recipes' },
  { label: t('food.nav_settings'), icon: 'i-heroicons-cog-6-tooth', to: '/food/settings' },
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
        module-name="Food"
        module-icon="i-heroicons-shopping-cart"
        module-color="electric-green"
        :navigation="foodNavigation"
      />
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
