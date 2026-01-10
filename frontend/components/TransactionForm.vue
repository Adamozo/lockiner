<script setup lang="ts">
import { z } from 'zod'
import type { Transaction, TransactionCreate } from '~/types/api'

interface Props {
  transaction?: Transaction | null
  categories?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  transaction: null,
  categories: () => ['Jedzenie', 'Transport', 'Rozrywka', 'Zdrowie', 'Dom', 'Edukacja', 'Inne'],
})

const emit = defineEmits<{
  submit: [transaction: TransactionCreate]
  cancel: []
}>()

// Form validation schema
const schema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Invalid date format'),
  amount: z.number().refine((val) => val !== 0, 'Amount cannot be zero'),
  description: z.string().optional(),
  category: z.string().min(1, 'Category is required'),
  notes: z.string().optional(),
})

// Form state
const form = reactive<TransactionCreate>({
  date: props.transaction?.date || formatDateForInput(),
  amount: props.transaction?.amount || 0,
  description: props.transaction?.description || '',
  category: props.transaction?.category || 'Inne',
  payment_method: props.transaction?.payment_method || null,
  notes: props.transaction?.notes || '',
})

// Payment method options
const paymentMethods = [
  { value: null, label: 'Not specified', icon: 'i-heroicons-minus-circle' },
  { value: 'card', label: 'Card', icon: 'i-heroicons-credit-card' },
  { value: 'cash', label: 'Cash', icon: 'i-heroicons-banknotes' },
  { value: 'blik', label: 'BLIK', icon: 'i-heroicons-device-phone-mobile' },
  { value: 'other', label: 'Other', icon: 'i-heroicons-ellipsis-horizontal-circle' },
]

// Validation errors
const errors = ref<Record<string, string>>({})

// Add category dialog state
const isAddCategoryDialogOpen = ref(false)

// Transaction type toggle (income/expense)
const transactionType = ref<'expense' | 'income'>(
  props.transaction && props.transaction.amount > 0 ? 'income' : 'expense'
)

// Computed amount with sign
const amountValue = computed({
  get: () => Math.abs(form.amount),
  set: (value: number) => {
    form.amount = transactionType.value === 'expense' ? -Math.abs(value) : Math.abs(value)
  },
})

// Watch transaction type changes
watch(transactionType, (newType) => {
  form.amount = newType === 'expense' ? -Math.abs(form.amount) : Math.abs(form.amount)
})

// Handle form submission
const handleSubmit = () => {
  errors.value = {}

  try {
    // Validate form
    schema.parse(form)

    // Emit submit event
    emit('submit', {
      ...form,
      // Clean up optional fields
      description: form.description || null,
      notes: form.notes || null,
    })

    // Reset form if creating new transaction
    if (!props.transaction) {
      resetForm()
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.errors.forEach((err) => {
        if (err.path[0]) {
          errors.value[err.path[0] as string] = err.message
        }
      })
    }
  }
}

// Reset form
const resetForm = () => {
  form.date = formatDateForInput()
  form.amount = 0
  form.description = ''
  form.category = 'Inne'
  form.payment_method = null
  form.notes = ''
  transactionType.value = 'expense'
  errors.value = {}
}

// Handle cancel
const handleCancel = () => {
  resetForm()
  emit('cancel')
}

// Open add category dialog
const openAddCategoryDialog = () => {
  isAddCategoryDialogOpen.value = true
}

// Handle category created
const handleCategoryCreated = (categoryName: string) => {
  // Auto-select the newly created category
  form.category = categoryName
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Transaction Type Toggle -->
    <div>
      <label class="block text-sm font-medium text-pure-white mb-3">
        Type
      </label>
      <div class="flex gap-3">
        <button
          type="button"
          class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all duration-300"
          :class="transactionType === 'expense'
            ? 'bg-gradient-to-r from-danger-red to-pink-500 text-white shadow-lg shadow-danger-red/30'
            : 'border-2 border-border-gray bg-transparent text-pure-white hover:border-danger-red/50'"
          @click="transactionType = 'expense'"
        >
          <UIcon name="i-heroicons-arrow-trending-down" class="w-5 h-5" />
          Expense
        </button>
        <button
          type="button"
          class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all duration-300"
          :class="transactionType === 'income'
            ? 'bg-gradient-to-r from-electric-green to-cyan-400 text-background-black shadow-lg shadow-electric-green/30'
            : 'border-2 border-border-gray bg-transparent text-pure-white hover:border-electric-green/50'"
          @click="transactionType = 'income'"
        >
          <UIcon name="i-heroicons-arrow-trending-up" class="w-5 h-5" />
          Income
        </button>
      </div>
    </div>

    <!-- Date -->
    <div>
      <label for="date" class="block text-sm font-medium text-pure-white mb-2">
        Date *
      </label>
      <input
        id="date"
        v-model="form.date"
        type="date"
        required
        class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
        :class="{ 'border-danger-red focus:border-danger-red focus:ring-danger-red/30': errors.date }"
      />
      <p v-if="errors.date" class="mt-1 text-sm text-danger-red">
        {{ errors.date }}
      </p>
    </div>

    <!-- Amount -->
    <div>
      <label for="amount" class="block text-sm font-medium text-pure-white mb-2">
        Amount (PLN) *
      </label>
      <input
        id="amount"
        v-model.number="amountValue"
        type="number"
        step="0.01"
        min="0.01"
        required
        class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
        :class="{ 'border-danger-red focus:border-danger-red focus:ring-danger-red/30': errors.amount }"
      />
      <p v-if="errors.amount" class="mt-1 text-sm text-danger-red">
        {{ errors.amount }}
      </p>
    </div>

    <!-- Category -->
    <div>
      <label for="category" class="block text-sm font-medium text-pure-white mb-2">
        Category *
      </label>
      <div class="flex gap-2">
        <select
          id="category"
          v-model="form.category"
          required
          class="flex-1 block rounded-lg border border-border-gray bg-card-black text-pure-white px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          :class="{ 'border-danger-red focus:border-danger-red focus:ring-danger-red/30': errors.category }"
        >
          <option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
        <button
          type="button"
          class="flex-shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-lg border-2 border-dashed border-border-gray bg-card-black text-cyber-blue hover:border-cyber-blue hover:bg-cyber-blue/10 transition-all duration-300"
          title="Add new category"
          @click="openAddCategoryDialog"
        >
          <UIcon name="i-heroicons-plus" class="w-5 h-5" />
        </button>
      </div>
      <p v-if="errors.category" class="mt-1 text-sm text-danger-red">
        {{ errors.category }}
      </p>
    </div>

    <!-- Payment Method -->
    <div>
      <label for="payment-method" class="block text-sm font-medium text-pure-white mb-2">
        Payment Method
      </label>
      <select
        id="payment-method"
        v-model="form.payment_method"
        class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
      >
        <option v-for="method in paymentMethods" :key="method.value || 'null'" :value="method.value">
          {{ method.label }}
        </option>
      </select>
    </div>

    <!-- Description -->
    <div>
      <label for="description" class="block text-sm font-medium text-pure-white mb-2">
        Description
      </label>
      <input
        id="description"
        v-model="form.description"
        type="text"
        placeholder="e.g., Grocery shopping at Biedronka"
        class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
      />
    </div>

    <!-- Notes -->
    <div>
      <label for="notes" class="block text-sm font-medium text-pure-white mb-2">
        Notes
      </label>
      <textarea
        id="notes"
        v-model="form.notes"
        rows="3"
        placeholder="Additional notes..."
        class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-2 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none resize-none"
      ></textarea>
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-3 pt-4 border-t border-border-gray">
      <BaseButton
        v-if="transaction"
        type="button"
        variant="secondary"
        @click="handleCancel"
      >
        Cancel
      </BaseButton>
      <BaseButton type="submit" variant="primary">
        {{ transaction ? 'Update' : 'Add' }} Transaction
      </BaseButton>
    </div>
  </form>

  <!-- Add Category Dialog -->
  <AddCategoryDialog
    v-model="isAddCategoryDialogOpen"
    @category-created="handleCategoryCreated"
  />
</template>
