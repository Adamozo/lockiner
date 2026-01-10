<script setup lang="ts">
const navigation = [
  {
    label: "Home",
    icon: "i-heroicons-home",
    to: "/",
  },
  {
    label: "Transactions",
    icon: "i-heroicons-banknotes",
    to: "/transactions",
  },
  {
    label: "Receipts",
    icon: "i-heroicons-document-text",
    to: "/receipts",
  },
  {
    label: "Analytics",
    icon: "i-heroicons-chart-bar",
    to: "/analytics",
  },
  {
    label: "Limits",
    icon: "i-heroicons-scale",
    to: "/limits",
  },
  {
    label: "Settings",
    icon: "i-heroicons-cog-6-tooth",
    to: "/settings",
  },
];

const route = useRoute();
const isActive = (path: string) => {
  return route.path === path;
};
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <!-- Header -->
    <header
      class="sticky top-0 z-50 bg-background-black/95 backdrop-blur-glass border-b border-border-gray"
    >
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo/Title -->
          <div class="flex items-center space-x-3 group">
            <div
              class="transition-transform group-hover:scale-110 group-hover:rotate-12"
            >
              <LockIcon :size="40" />
            </div>
            <div>
              <h1 class="text-xl font-bold">
                <span class="text-cyber-blue">Lock</span><span class="text-electric-green">In</span><span class="text-pure-white">er</span>
              </h1>
              <p class="text-xs text-pure-white/60">Lock In and Improve</p>
            </div>
          </div>

          <!-- Navigation -->
          <nav class="hidden md:flex items-center space-x-1">
            <NuxtLink
              v-for="item in navigation"
              :key="item.to"
              :to="item.to"
              class="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300"
              :class="
                isActive(item.to)
                  ? 'bg-card-black border-l-2 border-cyber-blue text-pure-white font-medium shadow-lg shadow-cyber-blue/20'
                  : 'text-pure-white/70 hover:bg-card-black/50 hover:text-electric-green hover:-translate-y-0.5'
              "
            >
              <UIcon :name="item.icon" class="w-5 h-5" />
              <span>{{ item.label }}</span>
            </NuxtLink>
          </nav>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <UButton variant="ghost" icon="i-heroicons-bars-3" />
          </div>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="container mx-auto px-4 py-6">
      <slot />
    </main>

    <!-- Mobile navigation -->
    <nav
      class="md:hidden fixed bottom-0 left-0 right-0 bg-background-black/95 backdrop-blur-glass border-t border-border-gray z-50"
    >
      <div class="flex items-center justify-around py-2">
        <NuxtLink
          v-for="item in navigation"
          :key="item.to"
          :to="item.to"
          class="flex flex-col items-center justify-center px-3 py-2 rounded-lg transition-all duration-300"
          :class="
            isActive(item.to)
              ? 'text-cyber-blue'
              : 'text-pure-white/60 hover:text-electric-green'
          "
        >
          <UIcon :name="item.icon" class="w-6 h-6" />
          <span class="text-xs mt-1">{{ item.label }}</span>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>
