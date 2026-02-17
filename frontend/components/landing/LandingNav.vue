<script setup lang="ts">
// Landing page navigation bar
</script>

<template>
  <nav class="border-b border-border-gray">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-14 sm:h-16">
        <NuxtLink to="/" class="flex items-center gap-2 sm:gap-3 group">
          <LockIcon class="w-8 h-8 sm:w-10 sm:h-10 text-electric-green group-hover:scale-110 transition-transform" />
          <span class="hidden sm:inline text-xl font-bold"
            ><span class="text-cyber-blue">Lock</span
            ><span class="text-electric-green">In</span
            ><span class="text-pure-white">er</span></span
          >
        </NuxtLink>
        <div class="flex items-center gap-2 sm:gap-4">
          <NuxtLink
            to="/login"
            class="hidden sm:inline text-pure-white/70 hover:text-pure-white transition-colors font-medium"
          >
            Sign in
          </NuxtLink>
          <NuxtLink
            to="/login"
            class="sm:hidden px-3 py-1.5 border border-border-gray text-pure-white text-sm font-medium rounded-lg transition-colors"
          >
            Sign in
          </NuxtLink>
          <NuxtLink
            to="/register"
            class="px-3 py-1.5 sm:px-4 sm:py-2 bg-electric-green hover:bg-electric-green/90 text-background-black text-sm sm:text-base font-semibold rounded-lg transition-colors"
          >
            Get Started
          </NuxtLink>
        </div>
      </div>
    </div>
  </nav>
</template>
