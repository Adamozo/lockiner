<script setup lang="ts">
import type { Transaction } from '~/types/api'

interface Props {
  transactions: Transaction[]
  loading?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  edit: [transaction: Transaction]
  delete: [id: number]
}>()

// Table columns
const columns = [
  {
    key: 'date',
    label: 'Date',
  },
  {
    key: 'description',
    label: 'Description',
  },
  {
    key: 'category',
    label: 'Category',
  },
  {
    key: 'payment_method',
    label: 'Payment',
  },
  {
    key: 'amount',
    label: 'Amount',
  },
  {
    key: 'actions',
    label: '',
  },
]

// Format amount with color
const formatAmount = (amount: number) => {
  const isIncome = amount > 0
  const formatted = formatCurrency(Math.abs(amount))
  return {
    text: isIncome ? `+${formatted}` : `-${formatted}`,
    class: isIncome ? 'text-electric-green font-semibold' : 'text-danger-red font-semibold',
  }
}

// Payment method helper
const getPaymentMethodInfo = (method: string | null) => {
  const methods: Record<string, { label: string; icon: string; color: string }> = {
    card: { label: 'Card', icon: 'i-heroicons-credit-card', color: 'text-cyber-blue' },
    cash: { label: 'Cash', icon: 'i-heroicons-banknotes', color: 'text-electric-green' },
    blik: { label: 'BLIK', icon: 'i-heroicons-device-phone-mobile', color: 'text-purple-400' },
    other: { label: 'Other', icon: 'i-heroicons-ellipsis-horizontal-circle', color: 'text-pure-white/60' },
  }
  return method && methods[method] ? methods[method] : { label: '-', icon: 'i-heroicons-minus-circle', color: 'text-pure-white/40' }
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <!-- Empty state -->
    <CommonEmptyState
      v-if="!loading && transactions.length === 0"
      icon="i-heroicons-banknotes"
      title="No transactions yet"
      description="Your transactions will appear here once you add them"
    />

    <!-- Mobile: Card view -->
    <div v-else>
      <div class="sm:hidden divide-y divide-border-gray">
        <div
          v-for="transaction in transactions"
          :key="'m-' + transaction.id"
          class="p-4 hover:bg-card-black/30 transition-colors"
        >
          <!-- Top row: description + amount -->
          <div class="flex items-start justify-between gap-3 mb-2">
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-pure-white truncate">
                {{ transaction.description || 'No description' }}
              </p>
              <p class="text-xs text-pure-white/50 mt-0.5">
                {{ formatDate(transaction.date) }}
              </p>
            </div>
            <span :class="formatAmount(transaction.amount).class" class="text-sm whitespace-nowrap">
              {{ formatAmount(transaction.amount).text }}
            </span>
          </div>

          <!-- Bottom row: category, payment, actions -->
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-2 min-w-0">
              <CategoryBadge :category="transaction.category" />
              <div class="flex items-center gap-1">
                <UIcon
                  :name="getPaymentMethodInfo(transaction.payment_method).icon"
                  class="w-3.5 h-3.5"
                  :class="getPaymentMethodInfo(transaction.payment_method).color"
                />
                <span class="text-xs" :class="getPaymentMethodInfo(transaction.payment_method).color">
                  {{ getPaymentMethodInfo(transaction.payment_method).label }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1 shrink-0">
              <BaseButton
                icon="i-heroicons-pencil"
                size="sm"
                variant="ghost"
                @click="emit('edit', transaction)"
              />
              <BaseButton
                icon="i-heroicons-trash"
                size="sm"
                variant="ghost"
                @click="emit('delete', transaction.id)"
              />
            </div>
          </div>

          <!-- Notes -->
          <p v-if="transaction.notes" class="text-xs text-pure-white/40 mt-1.5 truncate">
            {{ truncateText(transaction.notes, 60) }}
          </p>
        </div>
      </div>

      <!-- Desktop: Table view -->
      <div class="hidden sm:block overflow-x-auto">
        <table class="w-full">
          <thead class="bg-card-black/50 border-b border-border-gray">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                class="px-6 py-4 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider"
              >
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border-gray">
            <tr
              v-for="transaction in transactions"
              :key="transaction.id"
              class="hover:bg-card-black/30 transition-colors"
            >
              <!-- Date -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-pure-white">
                {{ formatDate(transaction.date) }}
              </td>

              <!-- Description -->
              <td class="px-6 py-4 text-sm text-pure-white">
                <div>
                  <div class="font-medium">
                    {{ transaction.description || 'No description' }}
                  </div>
                  <div v-if="transaction.notes" class="text-xs text-pure-white/60 mt-1">
                    {{ truncateText(transaction.notes, 50) }}
                  </div>
                </div>
              </td>

              <!-- Category -->
              <td class="px-6 py-4 whitespace-nowrap">
                <CategoryBadge :category="transaction.category" />
              </td>

              <!-- Payment Method -->
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <UIcon
                    :name="getPaymentMethodInfo(transaction.payment_method).icon"
                    class="w-4 h-4"
                    :class="getPaymentMethodInfo(transaction.payment_method).color"
                  />
                  <span :class="getPaymentMethodInfo(transaction.payment_method).color">
                    {{ getPaymentMethodInfo(transaction.payment_method).label }}
                  </span>
                </div>
              </td>

              <!-- Amount -->
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span :class="formatAmount(transaction.amount).class">
                  {{ formatAmount(transaction.amount).text }}
                </span>
              </td>

              <!-- Actions -->
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <BaseButton
                    icon="i-heroicons-pencil"
                    size="sm"
                    variant="ghost"
                    @click="emit('edit', transaction)"
                  />
                  <BaseButton
                    icon="i-heroicons-trash"
                    size="sm"
                    variant="ghost"
                    @click="emit('delete', transaction.id)"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
