<script setup lang="ts">
import { z } from 'zod'
import type { CategoryCreate } from '~/types/api'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'category-created': [categoryName: string]
}>()

const categoriesStore = useCategoriesStore()
const toast = useToast()

// Form validation schema
const schema = z.object({
  name: z.string().min(1, 'Category name is required').max(50, 'Name too long'),
  icon: z.string().optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid color format').optional(),
  budget_limit: z.number().positive('Budget must be positive').optional(),
})

// Form state
const form = reactive<CategoryCreate>({
  name: '',
  icon: '',
  color: '#4ECDC4',
  budget_limit: undefined,
})

const loading = ref(false)
const errors = ref<Record<string, string>>({})

// Predefined emoji options for quick selection
const emojiOptions = [
  '🍔', '🚗', '🛒', '💡', '🎮', '💊', '🏠', '📦',
  '✈️', '🎬', '📚', '💼', '⚽', '🎵', '🍕', '☕',
  '💳', '🎁', '🔧', '📱', '👕', '🏥', '🚌', '🍺',
]

// Color presets
const colorPresets = [
  '#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181',
  '#AA96DA', '#FCBAD3', '#A8D8EA', '#C7CEEA',
  '#FFD93D', '#6BCF7F', '#4D96FF', '#FF6B9D',
]

// Handle form submission
const handleSubmit = async () => {
  errors.value = {}

  try {
    // Validate form
    const validated = schema.parse(form)

    loading.value = true

    // Create category
    const newCategory = await categoriesStore.createCategory({
      name: validated.name,
      icon: validated.icon || null,
      color: validated.color || null,
      budget_limit: validated.budget_limit || null,
    })

    toast.add({
      title: 'Success',
      description: `Category "${newCategory.name}" created successfully`,
      color: 'green',
    })

    // Emit event with new category name
    emit('category-created', newCategory.name)
    close()
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.errors.forEach((err) => {
        if (err.path[0]) {
          errors.value[err.path[0] as string] = err.message
        }
      })
    } else {
      toast.add({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to create category',
        color: 'red',
      })
    }
  } finally {
    loading.value = false
  }
}

// Reset form
const resetForm = () => {
  form.name = ''
  form.icon = ''
  form.color = '#4ECDC4'
  form.budget_limit = undefined
  errors.value = {}
}

// Close modal
const close = () => {
  resetForm()
  emit('update:modelValue', false)
}

// Set emoji
const setEmoji = (emoji: string) => {
  form.icon = emoji
}

// Set color
const setColor = (color: string) => {
  form.color = color
}
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Add New Category"
    max-width="lg"
    @update:model-value="close"
  >
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Name -->
      <div>
        <label for="name" class="block text-sm font-medium text-pure-white mb-2">
          Category Name *
        </label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          required
          placeholder="e.g., Groceries, Entertainment"
          class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          :class="{ 'border-danger-red focus:border-danger-red focus:ring-danger-red/30': errors.name }"
        />
        <p v-if="errors.name" class="mt-1 text-sm text-danger-red">
          {{ errors.name }}
        </p>
      </div>

      <!-- Icon (Emoji) -->
      <div>
        <label class="block text-sm font-medium text-pure-white mb-2">
          Icon (Emoji)
        </label>
        <div class="space-y-3">
          <input
            v-model="form.icon"
            type="text"
            placeholder="Type emoji or select below"
            maxlength="2"
            class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          />
          <div class="grid grid-cols-8 gap-2">
            <button
              v-for="emoji in emojiOptions"
              :key="emoji"
              type="button"
              class="text-2xl p-2 rounded-lg border border-border-gray bg-card-black/50 hover:bg-card-black hover:border-cyber-blue transition-all duration-200"
              :class="{ 'border-cyber-blue bg-card-black': form.icon === emoji }"
              @click="setEmoji(emoji)"
            >
              {{ emoji }}
            </button>
          </div>
        </div>
      </div>

      <!-- Color -->
      <div>
        <label class="block text-sm font-medium text-pure-white mb-2">
          Color
        </label>
        <div class="space-y-3">
          <div class="flex gap-3 items-center">
            <input
              v-model="form.color"
              type="color"
              class="h-10 w-20 rounded-lg border border-border-gray bg-card-black cursor-pointer"
            />
            <input
              v-model="form.color"
              type="text"
              placeholder="#4ECDC4"
              class="flex-1 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
              :class="{ 'border-danger-red focus:border-danger-red focus:ring-danger-red/30': errors.color }"
            />
          </div>
          <div class="grid grid-cols-6 gap-2">
            <button
              v-for="color in colorPresets"
              :key="color"
              type="button"
              class="h-10 rounded-lg border-2 transition-all duration-200 hover:scale-110"
              :style="{ backgroundColor: color }"
              :class="form.color === color ? 'border-pure-white' : 'border-border-gray'"
              @click="setColor(color)"
            />
          </div>
        </div>
        <p v-if="errors.color" class="mt-1 text-sm text-danger-red">
          {{ errors.color }}
        </p>
      </div>

      <!-- Budget Limit -->
      <div>
        <label for="budget_limit" class="block text-sm font-medium text-pure-white mb-2">
          Monthly Budget Limit (PLN)
        </label>
        <input
          id="budget_limit"
          v-model.number="form.budget_limit"
          type="number"
          step="0.01"
          min="0"
          placeholder="Optional"
          class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          :class="{ 'border-danger-red focus:border-danger-red focus:ring-danger-red/30': errors.budget_limit }"
        />
        <p class="mt-1 text-xs text-pure-white/60">
          Leave empty for no budget limit
        </p>
        <p v-if="errors.budget_limit" class="mt-1 text-sm text-danger-red">
          {{ errors.budget_limit }}
        </p>
      </div>

      <!-- Preview -->
      <div v-if="form.name" class="bg-card-black/50 border border-border-gray rounded-lg p-4">
        <p class="text-xs font-medium text-pure-white/60 mb-2">Preview:</p>
        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all"
             :style="{
               borderColor: form.color || '#4ECDC4',
               backgroundColor: `${form.color || '#4ECDC4'}15`
             }">
          <span v-if="form.icon" class="text-lg">{{ form.icon }}</span>
          <span class="font-medium" :style="{ color: form.color || '#4ECDC4' }">
            {{ form.name }}
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-4 border-t border-border-gray">
        <BaseButton
          type="button"
          variant="secondary"
          @click="close"
        >
          Cancel
        </BaseButton>
        <BaseButton
          type="submit"
          variant="primary"
          :loading="loading"
        >
          Create Category
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
