<script setup lang="ts">
import type { ShoppingListItem, ShoppingItemStatus } from '~/types/shopping'

const props = defineProps<{
  item: ShoppingListItem
}>()

const emit = defineEmits<{
  statusChange: [id: number, status: ShoppingItemStatus]
  edit: [item: ShoppingListItem]
  delete: [id: number]
}>()

// Cycle: pending → in_cart → purchased → pending
function cycleStatus() {
  const next: Record<ShoppingItemStatus, ShoppingItemStatus> = {
    pending: 'in_cart',
    in_cart: 'purchased',
    purchased: 'pending',
  }
  emit('statusChange', props.item.id, next[props.item.status])
}

const statusConfig = computed(() => {
  switch (props.item.status) {
    case 'in_cart':
      return {
        icon: 'i-heroicons-shopping-cart',
        color: 'text-warning-orange',
        bg: 'bg-warning-orange/10 border-warning-orange/30',
        label: 'In cart',
      }
    case 'purchased':
      return {
        icon: 'i-heroicons-check-circle',
        color: 'text-electric-green',
        bg: 'bg-electric-green/10 border-electric-green/30',
        label: 'Purchased',
      }
    default:
      return {
        icon: 'i-heroicons-circle',
        color: 'text-border-gray',
        bg: 'bg-transparent border-border-gray',
        label: 'Pending',
      }
  }
})

const quantityLabel = computed(() => {
  if (!props.item.quantity) return null
  return props.item.unit ? `${props.item.quantity} ${props.item.unit}` : String(props.item.quantity)
})
</script>

<template>
  <div
    class="flex items-center gap-3 p-3 rounded-xl border transition-colors"
    :class="[
      item.status === 'purchased'
        ? 'bg-card-black/50 border-border-gray/40 opacity-60'
        : 'bg-card-black border-border-gray',
    ]"
  >
    <!-- Status toggle button -->
    <button
      class="flex-shrink-0 w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all"
      :class="statusConfig.bg"
      :title="statusConfig.label"
      @click="cycleStatus"
    >
      <span :class="[statusConfig.icon, statusConfig.color, 'text-sm']" />
    </button>

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <p
        class="text-sm font-medium"
        :class="item.status === 'purchased' ? 'line-through text-border-gray' : 'text-pure-white'"
      >
        {{ item.name }}
      </p>
      <div class="flex items-center gap-2 mt-0.5 flex-wrap">
        <span v-if="quantityLabel" class="text-xs text-border-gray">{{ quantityLabel }}</span>
        <span v-if="item.category" class="text-xs text-warning-orange/80">{{ item.category }}</span>
        <span v-if="item.notes" class="text-xs text-border-gray italic truncate max-w-[160px]">{{ item.notes }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-1 flex-shrink-0">
      <button
        class="p-1.5 rounded-lg text-border-gray hover:text-pure-white hover:bg-card-black transition-colors"
        title="Edit"
        @click="emit('edit', item)"
      >
        <span class="i-heroicons-pencil text-sm" />
      </button>
      <button
        class="p-1.5 rounded-lg text-border-gray hover:text-danger-red hover:bg-danger-red/10 transition-colors"
        title="Delete"
        @click="emit('delete', item.id)"
      >
        <span class="i-heroicons-trash text-sm" />
      </button>
    </div>
  </div>
</template>
