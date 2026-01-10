<script setup lang="ts">
/**
 * Location filter tabs for inventory
 */
import type { FoodInventoryLocation } from '~/types/food'

interface Props {
  modelValue: FoodInventoryLocation | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: FoodInventoryLocation | null]
}>()

const locations = [
  { value: null, label: 'All', icon: 'i-heroicons-squares-2x2' },
  { value: 'fridge' as const, label: 'Fridge', icon: 'i-heroicons-cube' },
  { value: 'freezer' as const, label: 'Freezer', icon: 'i-heroicons-cube-transparent' },
  { value: 'pantry' as const, label: 'Pantry', icon: 'i-heroicons-archive-box' },
]

const selectLocation = (value: FoodInventoryLocation | null) => {
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="flex gap-2 p-1 bg-card-black border border-border-gray rounded-xl">
    <button
      v-for="loc in locations"
      :key="loc.value ?? 'all'"
      class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
      :class="
        modelValue === loc.value
          ? 'bg-electric-green/20 text-electric-green'
          : 'text-pure-white/60 hover:text-pure-white hover:bg-pure-white/5'
      "
      @click="selectLocation(loc.value)"
    >
      <UIcon :name="loc.icon" class="w-4 h-4" />
      {{ loc.label }}
    </button>
  </div>
</template>
