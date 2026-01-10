<script setup lang="ts">
// Landing page hero section
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
    <div class="text-center">
      <LockIcon :size="96" class="mx-auto mb-8" />
      <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold mb-6">
        <span class="text-cyber-blue">Lock</span
        ><span class="text-electric-green">In</span
        ><span class="text-pure-white">er</span>
      </h1>
      <p
        class="text-xl md:text-2xl text-pure-white/60 max-w-3xl mx-auto mb-10"
      >
        Your personal dashboard to manage finances, track fitness progress,
        master new skills and manage food. Join and do it seamlessly!
      </p>
      <div class="flex flex-col sm:flex-row justify-center gap-4">
        <NuxtLink
          to="/register"
          class="px-8 py-3 bg-electric-green hover:bg-electric-green/90 text-background-black font-semibold rounded-lg text-lg transition-colors"
        >
          Get Started Free
        </NuxtLink>
        <NuxtLink
          to="/login"
          class="px-8 py-3 border border-border-gray hover:border-pure-white/40 text-pure-white font-semibold rounded-lg text-lg transition-colors"
        >
          Sign In
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
