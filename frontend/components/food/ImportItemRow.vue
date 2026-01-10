<script setup lang="ts">
/**
 * Import item row for pending imports
 */
import type { FoodPendingImportItem, FoodProduct, FoodCategory } from '~/types/food'

interface Props {
  item: FoodPendingImportItem
  categories: FoodCategory[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  accept: [data: { itemId: number; productId?: number; expiryDate?: string; quantity?: number }]
  reject: [itemId: number]
  createProduct: [data: { itemId: number; name: string; categoryId?: number }]
}>()

const isProcessed = computed(() => props.item.status !== 'pending')

const matchBadge = computed(() => {
  if (!props.item.matched_product_id) {
    return { label: 'No match', class: 'bg-warning-orange/10 text-warning-orange', icon: 'i-heroicons-question-mark-circle' }
  }
  switch (props.item.match_method) {
    case 'exact_name':
      return { label: 'Exact', class: 'bg-electric-green/10 text-electric-green', icon: 'i-heroicons-check-circle' }
    case 'alias':
      return { label: 'Alias', class: 'bg-cyber-blue/10 text-cyber-blue', icon: 'i-heroicons-link' }
    case 'barcode':
      return { label: 'Barcode', class: 'bg-violet-500/10 text-violet-400', icon: 'i-heroicons-qr-code' }
    case 'ai_suggestion':
      return { label: 'AI', class: 'bg-purple-500/10 text-purple-400', icon: 'i-heroicons-sparkles' }
    default:
      return { label: 'Matched', class: 'bg-electric-green/10 text-electric-green', icon: 'i-heroicons-check' }
  }
})

const statusBadge = computed(() => {
  switch (props.item.status) {
    case 'accepted':
      return { label: 'Accepted', class: 'bg-electric-green/10 text-electric-green' }
    case 'rejected':
      return { label: 'Rejected', class: 'bg-danger-red/10 text-danger-red' }
    case 'skipped':
      return { label: 'Skipped', class: 'bg-pure-white/10 text-pure-white/60' }
    default:
      return null
  }
})

// Quick accept with matched product
const quickAccept = () => {
  if (!props.item.matched_product_id) return
  emit('accept', {
    itemId: props.item.id,
    productId: props.item.matched_product_id,
    expiryDate: props.item.suggested_expiry_date ?? undefined,
    quantity: props.item.quantity ?? 1,
  })
}

// Reject item
const reject = () => {
  emit('reject', props.item.id)
}
</script>

<template>
  <div
    class="p-4 border border-border-gray rounded-xl transition-colors"
    :class="isProcessed ? 'bg-pure-white/5' : 'bg-card-black hover:border-electric-green/30'"
  >
    <div class="flex items-start justify-between gap-4">
      <!-- Item Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <h3
            class="font-medium truncate"
            :class="isProcessed ? 'text-pure-white/60' : 'text-pure-white'"
          >
            {{ item.original_name }}
          </h3>
          <span
            v-if="statusBadge"
            class="px-2 py-0.5 rounded text-xs font-medium"
            :class="statusBadge.class"
          >
            {{ statusBadge.label }}
          </span>
        </div>

        <!-- Match Status -->
        <div class="flex flex-wrap items-center gap-3 text-sm">
          <span
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium"
            :class="matchBadge.class"
          >
            <UIcon :name="matchBadge.icon" class="w-3.5 h-3.5" />
            {{ matchBadge.label }}
          </span>

          <span v-if="item.quantity" class="text-pure-white/60">
            Qty: {{ item.quantity }}
          </span>

          <span v-if="item.total_price" class="text-pure-white/60">
            {{ item.total_price.toFixed(2) }} PLN
          </span>
        </div>

        <!-- Matched Product Info -->
        <div v-if="item.matched_product" class="mt-2 text-sm text-pure-white/60">
          <span class="text-pure-white/40">Matched: </span>
          {{ item.matched_product.name }}
          <span v-if="item.matched_product.food_category" class="text-pure-white/40">
            ({{ item.matched_product.food_category.name }})
          </span>
        </div>

        <!-- Suggested Expiry -->
        <div v-if="item.suggested_expiry_date && !isProcessed" class="mt-2">
          <span class="text-sm text-pure-white/40">Suggested expiry: </span>
          <FoodExpiryBadge :expiry-date="item.suggested_expiry_date" :show-days="false" />
        </div>
      </div>

      <!-- Actions -->
      <div v-if="!isProcessed" class="flex items-center gap-2">
        <BaseButton
          v-if="item.matched_product_id"
          icon="i-heroicons-check"
          variant="primary"
          size="sm"
          @click="quickAccept"
        >
          Accept
        </BaseButton>
        <BaseButton
          v-else
          icon="i-heroicons-plus"
          variant="secondary"
          size="sm"
          @click="emit('createProduct', { itemId: item.id, name: item.original_name })"
        >
          Add Product
        </BaseButton>
        <BaseButton
          icon="i-heroicons-x-mark"
          variant="ghost"
          size="sm"
          @click="reject"
        >
          Skip
        </BaseButton>
      </div>
    </div>
  </div>
</template>
