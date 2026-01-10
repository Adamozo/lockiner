<script setup lang="ts">
/**
 * Inventory item card
 */
import type { FoodInventoryItem } from '~/types/food'

interface Props {
  item: FoodInventoryItem
}

const props = defineProps<Props>()
const emit = defineEmits<{
  consume: [item: FoodInventoryItem]
  open: [item: FoodInventoryItem]
  edit: [item: FoodInventoryItem]
  delete: [item: FoodInventoryItem]
}>()

const locationIcon = computed(() => {
  switch (props.item.location) {
    case 'fridge':
      return 'i-heroicons-cube'
    case 'freezer':
      return 'i-heroicons-cube-transparent'
    case 'pantry':
      return 'i-heroicons-archive-box'
    default:
      return 'i-heroicons-cube'
  }
})

const locationLabel = computed(() => {
  switch (props.item.location) {
    case 'fridge':
      return 'Fridge'
    case 'freezer':
      return 'Freezer'
    case 'pantry':
      return 'Pantry'
    default:
      return props.item.location
  }
})

const statusBadge = computed(() => {
  switch (props.item.status) {
    case 'opened':
      return { label: 'Opened', class: 'bg-cyber-blue/10 text-cyber-blue' }
    case 'consumed':
      return { label: 'Consumed', class: 'bg-electric-green/10 text-electric-green' }
    case 'expired':
      return { label: 'Expired', class: 'bg-danger-red/10 text-danger-red' }
    case 'thrown_away':
      return { label: 'Thrown away', class: 'bg-pure-white/10 text-pure-white/60' }
    default:
      return null
  }
})

const categoryName = computed(() => {
  return props.item.product.food_category?.name || 'Uncategorized'
})
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-xl p-4 hover:border-electric-green/30 transition-colors">
    <div class="flex items-start justify-between gap-4">
      <!-- Product Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <h3 class="font-medium text-pure-white truncate">
            {{ item.product.name }}
          </h3>
          <span
            v-if="statusBadge"
            class="px-2 py-0.5 rounded text-xs font-medium"
            :class="statusBadge.class"
          >
            {{ statusBadge.label }}
          </span>
        </div>

        <div class="flex flex-wrap items-center gap-3 text-sm text-pure-white/60">
          <span class="flex items-center gap-1">
            <UIcon :name="locationIcon" class="w-4 h-4" />
            {{ locationLabel }}
          </span>
          <span>{{ item.quantity }} {{ item.unit }}</span>
          <span class="text-pure-white/40">{{ categoryName }}</span>
        </div>

        <!-- Expiry -->
        <div class="mt-2">
          <FoodExpiryBadge :expiry-date="item.expiry_date" />
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-1">
        <BaseButton
          v-if="item.status === 'available'"
          icon="i-heroicons-arrow-up-on-square"
          variant="ghost"
          size="sm"
          title="Mark as opened"
          @click="emit('open', item)"
        />
        <BaseButton
          v-if="item.status === 'available' || item.status === 'opened'"
          icon="i-heroicons-minus-circle"
          variant="ghost"
          size="sm"
          title="Consume"
          @click="emit('consume', item)"
        />
        <BaseButton
          icon="i-heroicons-pencil"
          variant="ghost"
          size="sm"
          title="Edit"
          @click="emit('edit', item)"
        />
        <BaseButton
          icon="i-heroicons-trash"
          variant="danger"
          size="sm"
          title="Delete"
          @click="emit('delete', item)"
        />
      </div>
    </div>
  </div>
</template>
