<script setup lang="ts">
definePageMeta({
  layout: "default",
});

useSeoMeta({
  title: "Dashboard - LockIner",
  description: "Coming soon - Your personal life management hub",
});
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center">
    <div class="text-center max-w-lg mx-auto px-4">
      <div class="mb-8">
        <div class="relative inline-block">
          <UIcon
            name="i-heroicons-wrench-screwdriver"
            class="w-24 h-24 text-warning-orange animate-pulse"
          />
          <div class="absolute -top-2 -right-2">
            <UIcon
              name="i-heroicons-cog-6-tooth"
              class="w-8 h-8 text-cyber-blue animate-spin"
              style="animation-duration: 3s"
            />
          </div>
        </div>
      </div>

      <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
        <span class="text-cyber-blue">Under</span>
        <br class="sm:hidden" />
        <span class="text-pure-white hidden sm:inline"> </span>
        <span class="text-electric-green">Construction</span>
      </h1>

      <p class="text-lg text-pure-white/60 mb-8">
        We're building something awesome. The dashboard is being redesigned to
        bring you a better experience.
      </p>

      <div class="bg-card-black border border-border-gray rounded-xl p-6 mb-8">
        <div class="flex items-center justify-center gap-2 text-pure-white/50">
          <div class="w-2 h-2 bg-electric-green rounded-full animate-pulse" />
          <span class="text-sm">Development in progress</span>
        </div>
      </div>

      <NuxtLink
        to="/finance"
        class="inline-flex items-center gap-2 px-6 py-3 bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg text-cyber-blue hover:bg-cyber-blue/20 transition-colors"
      >
        <UIcon name="i-heroicons-banknotes" class="w-5 h-5" />
        <span>Go to Finance Module</span>
      </NuxtLink>
    </div>
  </div>
</template>
