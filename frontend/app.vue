<script setup lang="ts">
// Initialize PWA functionality
usePWAInstall()
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <NuxtLoadingIndicator />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <PwaInstallBanner />
    <PwaUpdatePrompt />
  </div>
</template>
