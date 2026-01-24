<script setup lang="ts">
// Skills module layout with sidebar + skills navbar

const skillsNavigation = [
  { label: 'Dashboard', icon: 'i-heroicons-home', to: '/skills' },
  { label: 'Journeys', icon: 'i-heroicons-academic-cap', to: '/skills/journeys' },
  { label: 'Log', icon: 'i-heroicons-clipboard-document-list', to: '/skills/log' },
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
        module-name="Skills"
        module-icon="i-heroicons-academic-cap"
        module-color="cyber-blue"
        :navigation="skillsNavigation"
      />

      <!-- Page Content -->
      <main class="container mx-auto px-4 py-6">
        <slot />
      </main>
    </div>
  </div>
</template>
