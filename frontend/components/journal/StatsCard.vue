<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  icon: string
  color?: string
}>()
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-xl p-4">
    <div class="flex items-center gap-3">
      <div class="p-2 rounded-lg bg-background-black">
        <UIcon :name="icon" class="w-5 h-5" :class="color || 'text-cyber-blue'" />
      </div>
      <div>
        <p class="text-2xl font-bold text-pure-white">{{ value }}</p>
        <p class="text-sm text-pure-white/50">{{ label }}</p>
      </div>
    </div>
  </div>
</template>
