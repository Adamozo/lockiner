<script setup lang="ts">
import { z } from 'zod'
import type { Category } from '~/types/api'

const props = defineProps<{
  modelValue: boolean
  category: Category
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'budget-updated': [category: Category]
}>()

const categoriesStore = useCategoriesStore()
const toast = useToast()

// Form validation schema
const schema = z.object({
  budget_limit: z.number().positive('Budget must be positive').optional().nullable(),
})

// Form state
const form = reactive({
  budget_limit: props.category.budget_limit,
})

const loading = ref(false)
const errors = ref<Record<string, string>>({})

// Handle form submission
const handleSubmit = async () => {
  errors.value = {}

  try {
    schema.parse(form)

    loading.value = true

    const updated = await categoriesStore.updateCategory(props.category.id, {
      budget_limit: form.budget_limit,
    })

    toast.add({
      title: 'Success',
      description: `Budget limit for "${updated.name}" updated successfully`,
      color: 'green',
    })

    emit('budget-updated', updated)
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
        description: error instanceof Error ? error.message : 'Failed to update budget',
        color: 'red',
      })
    }
  } finally {
    loading.value = false
  }
}

// Close modal
const close = () => {
  form.budget_limit = props.category.budget_limit
  errors.value = {}
  emit('update:modelValue', false)
}

// Watch for category changes
watch(
  () => props.category,
  (newCategory) => {
    form.budget_limit = newCategory.budget_limit
  }
)
</script>

<template>
  <BaseModal :model-value="modelValue" :title="`Edit Budget: ${category.name}`" max-width="md" @update:model-value="close">
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Category Preview -->
      <div class="flex items-center gap-3 p-3 bg-card-black/50 rounded-lg">
        <div
          class="w-10 h-10 rounded-lg flex items-center justify-center"
          :style="{ backgroundColor: (category.color || '#00d4ff') + '20' }"
        >
          <CategoryIcon
            :icon="category.icon"
            :size="24"
            :color="category.color || '#00d4ff'"
          />
        </div>
        <div>
          <p class="font-semibold text-pure-white">{{ category.name }}</p>
          <p class="text-xs text-pure-white/60">Category</p>
        </div>
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
          placeholder="e.g., 500.00"
          class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-3 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          :class="{ 'border-danger-red': errors.budget_limit }"
        />
        <p class="mt-2 text-xs text-pure-white/60">
          Leave empty to remove budget limit for this category
        </p>
        <p v-if="errors.budget_limit" class="mt-1 text-sm text-danger-red">
          {{ errors.budget_limit }}
        </p>
      </div>

      <!-- Current vs New -->
      <div
        v-if="form.budget_limit !== category.budget_limit"
        class="bg-cyber-blue/10 border border-cyber-blue rounded-lg p-3"
      >
        <p class="text-xs font-medium text-cyber-blue mb-2">Change Preview:</p>
        <div class="flex items-center justify-between text-sm">
          <span class="text-pure-white/60">
            Current: {{ category.budget_limit ? `${category.budget_limit.toFixed(2)} PLN` : 'No limit' }}
          </span>
          <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 text-cyber-blue" />
          <span class="text-pure-white font-medium">
            New: {{ form.budget_limit ? `${form.budget_limit.toFixed(2)} PLN` : 'No limit' }}
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-4 border-t border-border-gray">
        <BaseButton type="button" variant="secondary" @click="close"> Cancel </BaseButton>
        <BaseButton type="submit" variant="primary" :loading="loading"> Update Budget </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
