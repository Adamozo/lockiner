<script setup lang="ts">
interface Props {
  lines?: number
  showIcon?: boolean
  showBadge?: boolean
}

withDefaults(defineProps<Props>(), {
  lines: 2,
  showIcon: true,
  showBadge: false,
})
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg p-6 animate-pulse">
    <div class="flex items-start gap-4">
      <!-- Icon skeleton -->
      <div
        v-if="showIcon"
        class="w-12 h-12 rounded-xl bg-background-black flex-shrink-0"
      />

      <div class="flex-1 space-y-3">
        <!-- Title skeleton -->
        <div class="h-5 bg-background-black rounded w-3/4" />

        <!-- Line skeletons -->
        <template v-for="i in lines" :key="i">
          <div
            class="h-4 bg-background-black rounded"
            :class="i === lines ? 'w-1/2' : 'w-full'"
          />
        </template>
      </div>

      <!-- Badge skeleton -->
      <div
        v-if="showBadge"
        class="w-16 h-6 bg-background-black rounded-full flex-shrink-0"
      />
    </div>
  </div>
</template>
