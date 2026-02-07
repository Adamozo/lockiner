<script setup lang="ts">
import type { ReceiptItem } from '~/types/api'
import { formatCurrency } from '~/utils/formatters'

const props = defineProps<{
  item: ReceiptItem
  index: number
  isEditable: boolean
}>()

const emit = defineEmits<{
  update: [item: ReceiptItem]
}>()

const categoriesStore = useCategoriesStore()

// Edit mode state
const isEditing = ref(false)
const editForm = ref<ReceiptItem>({ ...props.item })

// Watch for external item changes
watch(() => props.item, (newItem) => {
  if (!isEditing.value) {
    editForm.value = { ...newItem }
  }
}, { deep: true })

// Start editing
const startEditing = () => {
  editForm.value = { ...props.item }
  isEditing.value = true
}

// Cancel editing
const cancelEditing = () => {
  editForm.value = { ...props.item }
  isEditing.value = false
}

// Save changes
const saveChanges = () => {
  // Auto-calculate total_price
  editForm.value.total_price = editForm.value.quantity * editForm.value.unit_price
  emit('update', { ...editForm.value })
  isEditing.value = false
}

// Auto-calculate total when quantity or unit_price changes
watch([() => editForm.value.quantity, () => editForm.value.unit_price], () => {
  if (isEditing.value) {
    editForm.value.total_price = editForm.value.quantity * editForm.value.unit_price
  }
})
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg p-4">
    <!-- Display Mode -->
    <template v-if="!isEditing">
      <div class="flex justify-between items-start mb-2">
        <h4 class="font-medium text-pure-white flex-1 pr-2">{{ item.name }}</h4>
        <span class="text-electric-green font-semibold whitespace-nowrap">
          {{ formatCurrency(item.total_price) }}
        </span>
      </div>
      <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-pure-white/60 mb-3">
        <span>Qty: {{ item.quantity }}</span>
        <span>@ {{ formatCurrency(item.unit_price) }}</span>
        <span v-if="item.category" class="text-cyber-blue">{{ item.category }}</span>
        <span v-else class="text-pure-white/40 italic">No category</span>
      </div>
      <button
        v-if="isEditable"
        class="text-sm text-cyber-blue hover:text-cyber-blue/80 transition-colors flex items-center gap-1"
        @click="startEditing"
      >
        <UIcon name="i-heroicons-pencil" class="w-4 h-4" />
        Edit
      </button>
    </template>

    <!-- Edit Mode -->
    <template v-else>
      <div class="space-y-3">
        <!-- Name -->
        <div>
          <label class="text-xs text-pure-white/60 mb-1 block">Name</label>
          <input
            v-model="editForm.name"
            type="text"
            class="w-full px-3 py-2 text-sm bg-background-black border border-border-gray rounded-lg text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
          >
        </div>

        <!-- Quantity & Unit Price -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-pure-white/60 mb-1 block">Quantity</label>
            <input
              v-model.number="editForm.quantity"
              type="number"
              min="1"
              class="w-full px-3 py-2 text-sm bg-background-black border border-border-gray rounded-lg text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
            >
          </div>
          <div>
            <label class="text-xs text-pure-white/60 mb-1 block">Unit Price</label>
            <input
              v-model.number="editForm.unit_price"
              type="number"
              step="0.01"
              min="0"
              class="w-full px-3 py-2 text-sm bg-background-black border border-border-gray rounded-lg text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
            >
          </div>
        </div>

        <!-- Category -->
        <div>
          <label class="text-xs text-pure-white/60 mb-1 block">Category</label>
          <select
            v-model="editForm.category"
            class="w-full px-3 py-2 text-sm bg-background-black border border-border-gray rounded-lg text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
          >
            <option value="">No category</option>
            <option
              v-for="cat in categoriesStore.categoryNames"
              :key="cat"
              :value="cat"
            >
              {{ cat }}
            </option>
          </select>
        </div>

        <!-- Total (calculated) -->
        <div class="flex justify-between items-center py-2 border-t border-border-gray">
          <span class="text-sm text-pure-white/60">Total</span>
          <span class="font-semibold text-electric-green">{{ formatCurrency(editForm.total_price) }}</span>
        </div>

        <!-- Actions -->
        <div class="flex gap-2">
          <BaseButton
            size="sm"
            variant="primary"
            icon="i-heroicons-check"
            class="flex-1"
            @click="saveChanges"
          >
            Save
          </BaseButton>
          <BaseButton
            size="sm"
            variant="ghost"
            icon="i-heroicons-x-mark"
            @click="cancelEditing"
          >
            Cancel
          </BaseButton>
        </div>
      </div>
    </template>
  </div>
</template>
