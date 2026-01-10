<script setup lang="ts">
interface Props {
  count?: number
  lines?: number
  showIcon?: boolean
  showBadge?: boolean
}

withDefaults(defineProps<Props>(), {
  count: 3,
  lines: 2,
  showIcon: true,
  showBadge: false,
})
</script>

<template>
  <div class="space-y-4">
    <CommonSkeletonCard
      v-for="i in count"
      :key="i"
      :lines="lines"
      :show-icon="showIcon"
      :show-badge="showBadge"
    />
  </div>
</template>
