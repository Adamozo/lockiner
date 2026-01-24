<script setup lang="ts">
defineProps<{
  providerName: string;
}>();
</script>

<template>
  <div
    class="p-4 bg-electric-green/10 border border-electric-green/30 rounded-lg backdrop-blur-sm"
  >
    <div class="flex items-center gap-3">
      <div
        class="w-3 h-3 rounded-full bg-electric-green shadow-lg shadow-electric-green/50"
      />
      <span class="font-medium text-pure-white">Active Provider:</span>
      <span class="text-pure-white capitalize">{{ providerName }}</span>
    </div>
  </div>
</template>
