<script setup lang="ts">
import type { ShoppingListItemCreate } from '~/types/shopping'

const props = defineProps<{
  listId: number
}>()

const emit = defineEmits<{
  added: [item: ShoppingListItemCreate]
  cancel: []
}>()

const nameInput = ref<HTMLInputElement | null>(null)

const form = reactive<ShoppingListItemCreate>({
  name: '',
  quantity: null,
  unit: null,
  category: null,
  notes: null,
})

const showDetails = ref(false)

onMounted(() => {
  nextTick(() => nameInput.value?.focus())
})

function submit() {
  if (!form.name.trim()) return
  emit('added', { ...form })
  // Reset for next quick-add
  form.name = ''
  form.quantity = null
  form.unit = null
  form.category = null
  form.notes = null
  showDetails.value = false
  nextTick(() => nameInput.value?.focus())
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') submit()
  if (e.key === 'Escape') emit('cancel')
}
</script>

<template>
  <div class="bg-card-black border border-warning-orange/40 rounded-xl p-4 space-y-3">
    <!-- Name row -->
    <div class="flex items-center gap-2">
      <input
        ref="nameInput"
        v-model="form.name"
        type="text"
        placeholder="Item name..."
        class="flex-1 bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
        @keydown="handleKeydown"
      />
      <button
        class="p-2 rounded-lg text-border-gray hover:text-warning-orange transition-colors"
        :title="showDetails ? 'Hide details' : 'Add details'"
        @click="showDetails = !showDetails"
      >
        <span :class="showDetails ? 'i-heroicons-chevron-up' : 'i-heroicons-adjustments-horizontal'" class="text-sm" />
      </button>
    </div>

    <!-- Optional details -->
    <div v-if="showDetails" class="grid grid-cols-2 gap-2">
      <div>
        <label class="text-xs text-border-gray mb-1 block">Quantity</label>
        <input
          v-model.number="form.quantity"
          type="number"
          min="0.01"
          step="0.01"
          placeholder="e.g. 2"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
        />
      </div>
      <div>
        <label class="text-xs text-border-gray mb-1 block">Unit</label>
        <input
          v-model="form.unit"
          type="text"
          placeholder="e.g. kg, pcs"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
        />
      </div>
      <div>
        <label class="text-xs text-border-gray mb-1 block">Category</label>
        <input
          v-model="form.category"
          type="text"
          placeholder="e.g. Dairy, Hardware"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
        />
      </div>
      <div>
        <label class="text-xs text-border-gray mb-1 block">Note</label>
        <input
          v-model="form.notes"
          type="text"
          placeholder="Optional note"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
        />
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-2">
      <BaseButton variant="primary" size="sm" :disabled="!form.name.trim()" @click="submit">
        <span class="i-heroicons-plus text-sm mr-1" />
        Add
      </BaseButton>
      <BaseButton variant="ghost" size="sm" @click="emit('cancel')">
        Cancel
      </BaseButton>
    </div>
  </div>
</template>
