<script setup lang="ts">
import type { ShoppingListSummary } from '~/types/shopping'

defineProps<{
  list: ShoppingListSummary
}>()

const emit = defineEmits<{
  delete: [id: number]
}>()

function progressPercent(list: ShoppingListSummary) {
  if (list.total_items === 0) return 0
  return Math.round((list.purchased_items / list.total_items) * 100)
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return null
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })
}
</script>

<template>
  <NuxtLink
    :to="`/shopping/${list.id}`"
    class="block bg-card-black border border-border-gray rounded-xl p-4 hover:border-warning-orange/50 transition-colors group"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <!-- Name + store -->
        <div class="flex items-center gap-2 flex-wrap">
          <h3 class="font-semibold text-pure-white group-hover:text-warning-orange transition-colors truncate">
            {{ list.name }}
          </h3>
          <span
            v-if="list.visibility === 'household'"
            class="text-xs px-1.5 py-0.5 bg-warning-orange/10 text-warning-orange rounded-md"
          >
            Household
          </span>
        </div>

        <div class="flex items-center gap-3 mt-1 flex-wrap">
          <span v-if="list.store_name" class="text-xs text-border-gray flex items-center gap-1">
            <span class="i-heroicons-map-pin text-xs" />
            {{ list.store_name }}
          </span>
          <span v-if="list.planned_date" class="text-xs text-border-gray flex items-center gap-1">
            <span class="i-heroicons-calendar text-xs" />
            {{ formatDate(list.planned_date) }}
          </span>
        </div>

        <!-- Progress -->
        <div v-if="list.total_items > 0" class="mt-3 space-y-1">
          <div class="flex items-center justify-between text-xs text-border-gray">
            <span>{{ list.purchased_items }}/{{ list.total_items }} items</span>
            <span v-if="list.in_cart_items > 0" class="text-warning-orange">
              {{ list.in_cart_items }} in cart
            </span>
          </div>
          <div class="h-1 bg-background-black rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="progressPercent(list) === 100 ? 'bg-electric-green' : 'bg-warning-orange'"
              :style="{ width: `${progressPercent(list)}%` }"
            />
          </div>
        </div>
        <p v-else class="text-xs text-border-gray mt-2">Empty list</p>
      </div>

      <!-- Delete -->
      <button
        class="p-1.5 rounded-lg text-border-gray hover:text-danger-red hover:bg-danger-red/10 transition-colors opacity-0 group-hover:opacity-100 flex-shrink-0"
        title="Delete list"
        @click.prevent="emit('delete', list.id)"
      >
        <span class="i-heroicons-trash text-sm" />
      </button>
    </div>
  </NuxtLink>
</template>
