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
  // Auto-calculate total_price if quantity or unit_price changed
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

// Get category for display
const categoryInfo = computed(() => {
  const cat = categoriesStore.getCategoryByName(editForm.value.category || props.item.category || 'Inne')
  return cat || { name: editForm.value.category || 'Inne', icon: '📦', color: '#C7CEEA' }
})
</script>

<template>
  <tr
    :class="isEditing ? 'bg-card-black/30' : ''"
    class="transition-colors"
  >
    <!-- Display Mode -->
    <template v-if="!isEditing">
      <!-- Item Name -->
      <td class="px-4 py-3 text-sm text-pure-white">
        {{ item.name }}
      </td>

      <!-- Quantity -->
      <td class="px-4 py-3 text-sm text-pure-white text-right">
        {{ item.quantity }}
      </td>

      <!-- Unit Price -->
      <td class="px-4 py-3 text-sm text-pure-white text-right">
        {{ formatCurrency(item.unit_price) }}
      </td>

      <!-- Total Price -->
      <td class="px-4 py-3 text-sm font-medium text-electric-green text-right">
        {{ formatCurrency(item.total_price) }}
      </td>

      <!-- Category -->
      <td class="px-4 py-3 text-sm text-pure-white">
        <div
          v-if="item.category"
          class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium"
          :style="{
            backgroundColor: `${categoryInfo.color}20`,
            borderColor: categoryInfo.color,
            color: categoryInfo.color
          }"
          style="border-width: 1px;"
        >
          <CategoryIcon
            v-if="categoryInfo.icon"
            :icon="categoryInfo.icon"
            :size="14"
            :color="categoryInfo.color"
          />
          <span>{{ categoryInfo.name }}</span>
        </div>
        <span v-else class="text-pure-white/40 italic text-xs">
          No category
        </span>
      </td>

      <!-- Actions -->
      <td class="px-4 py-3 text-right">
        <button
          v-if="isEditable"
          class="p-1.5 rounded-md hover:bg-cyber-blue/20 transition-colors text-pure-white/60 hover:text-cyber-blue"
          title="Edit item"
          @click="startEditing"
        >
          <UIcon name="i-heroicons-pencil" class="w-4 h-4" />
        </button>
      </td>
    </template>

    <!-- Edit Mode -->
    <template v-else>
      <!-- Item Name (editable) -->
      <td class="px-4 py-3">
        <input
          v-model="editForm.name"
          type="text"
          class="w-full px-2 py-1.5 text-sm bg-card-black border border-border-gray rounded-md text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
          placeholder="Item name"
        >
      </td>

      <!-- Quantity (editable) -->
      <td class="px-4 py-3">
        <input
          v-model.number="editForm.quantity"
          type="number"
          min="1"
          class="w-20 px-2 py-1.5 text-sm text-right bg-card-black border border-border-gray rounded-md text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
        >
      </td>

      <!-- Unit Price (editable) -->
      <td class="px-4 py-3">
        <input
          v-model.number="editForm.unit_price"
          type="number"
          step="0.01"
          min="0"
          class="w-24 px-2 py-1.5 text-sm text-right bg-card-black border border-border-gray rounded-md text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
        >
      </td>

      <!-- Total Price (auto-calculated) -->
      <td class="px-4 py-3 text-sm font-medium text-electric-green text-right">
        {{ formatCurrency(editForm.total_price) }}
      </td>

      <!-- Category (editable) -->
      <td class="px-4 py-3">
        <select
          v-model="editForm.category"
          class="w-full px-2 py-1.5 text-xs bg-card-black border border-border-gray rounded-md text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
          :style="{ color: categoryInfo.color }"
        >
          <option
            v-for="cat in categoriesStore.categoryNames"
            :key="cat"
            :value="cat"
          >
            {{ cat }}
          </option>
        </select>
      </td>

      <!-- Actions (Save/Cancel) -->
      <td class="px-4 py-3">
        <div class="flex items-center justify-end gap-1">
          <button
            class="p-1.5 rounded-md bg-electric-green/20 hover:bg-electric-green/30 transition-colors text-electric-green"
            title="Save changes"
            @click="saveChanges"
          >
            <UIcon name="i-heroicons-check" class="w-4 h-4" />
          </button>
          <button
            class="p-1.5 rounded-md bg-danger-red/20 hover:bg-danger-red/30 transition-colors text-danger-red"
            title="Cancel"
            @click="cancelEditing"
          >
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
          </button>
        </div>
      </td>
    </template>
  </tr>
</template>
