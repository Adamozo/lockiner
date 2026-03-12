<script setup lang="ts">
const adminNavigation = [
  { label: 'Vouchers', icon: 'i-heroicons-ticket', to: '/admin/vouchers' },
  { label: 'Users', icon: 'i-heroicons-users', to: '/admin/users' },
  { label: 'Notifications', icon: 'i-heroicons-bell', to: '/admin/notifications' },
  { label: 'OFF Search', icon: 'i-heroicons-magnifying-glass', to: '/admin/off-search' },
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
        module-name="Admin"
        module-icon="i-heroicons-shield-check"
        module-color="warning-orange"
        :navigation="adminNavigation"
      />
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
