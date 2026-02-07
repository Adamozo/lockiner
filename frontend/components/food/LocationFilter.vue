<script setup lang="ts">
/**
 * Location filter dropdown for inventory
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
  { value: '', label: 'All Locations', icon: 'i-heroicons-squares-2x2' },
  { value: 'fridge', label: 'Fridge', icon: 'i-heroicons-cube' },
  { value: 'freezer', label: 'Freezer', icon: 'i-heroicons-cube-transparent' },
  { value: 'pantry', label: 'Pantry', icon: 'i-heroicons-archive-box' },
]

const selectedValue = computed({
  get: () => props.modelValue ?? '',
  set: (val: string) => emit('update:modelValue', val === '' ? null : val as FoodInventoryLocation)
})

const selectedLabel = computed(() => {
  const loc = locations.find(l => l.value === (props.modelValue ?? ''))
  return loc?.label ?? 'All Locations'
})
</script>

<template>
  <div class="flex items-center gap-2">
    <UIcon name="i-heroicons-funnel" class="w-4 h-4 text-pure-white/60" />
    <select
      v-model="selectedValue"
      class="px-3 py-2 bg-card-black border border-border-gray rounded-lg text-pure-white text-sm font-medium focus:border-electric-green focus:ring-1 focus:ring-electric-green focus:outline-none transition-colors"
    >
      <option
        v-for="loc in locations"
        :key="loc.value"
        :value="loc.value"
      >
        {{ loc.label }}
      </option>
    </select>
  </div>
</template>
