<script setup lang="ts">
// Finance module layout with sidebar + finance navbar

const financeNavigation = [
  { label: 'Dashboard', icon: 'i-heroicons-home', to: '/finance' },
  { label: 'Transactions', icon: 'i-heroicons-banknotes', to: '/finance/transactions' },
  { label: 'Receipts', icon: 'i-heroicons-document-text', to: '/finance/receipts' },
  { label: 'Analytics', icon: 'i-heroicons-chart-bar', to: '/finance/analytics' },
  { label: 'Limits', icon: 'i-heroicons-scale', to: '/finance/limits' },
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
        module-name="Finance"
        module-icon="i-heroicons-banknotes"
        module-color="electric-green"
        :navigation="financeNavigation"
      />

      <!-- Page Content -->
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
