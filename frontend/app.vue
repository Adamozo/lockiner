<script setup lang="ts">
// Initialize PWA functionality
usePWAInstall()
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <NuxtPwaAssets />
    <NuxtLoadingIndicator />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>
