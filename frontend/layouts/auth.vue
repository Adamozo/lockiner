<script setup lang="ts">
// Auth layout - centered content without sidebar
// Used for login, register, and other auth pages
</script>

<template>
  <div
    class="min-h-screen bg-background-black flex items-center justify-center px-4 py-8"
  >
    <div class="w-full max-w-md">
      <!-- Logo/Brand -->
      <div class="text-center mb-2">
        <NuxtLink to="/" class="mx-auto inline-flex items-center gap-3 group">
          <LockIcon
            class="w-12 h-12 text-electric-green group-hover:scale-110 transition-transform"
          />
          <span class="text-2xl font-bold"
            ><span class="text-cyber-blue">Lock</span
            ><span class="text-electric-green">In</span
            ><span class="text-pure-white">er</span></span
          >
        </NuxtLink>
      </div>

      <!-- Content Slot -->
      <slot />
    </div>
  </div>
</template>
