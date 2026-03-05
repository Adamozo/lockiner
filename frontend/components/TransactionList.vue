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
  'bulk-delete': [ids: number[]]
}>()

// --- Selection state ---
const selectedIds = ref<Set<number>>(new Set())

const isSelected = (id: number) => selectedIds.value.has(id)

const toggleOne = (id: number) => {
  const next = new Set(selectedIds.value)
  next.has(id) ? next.delete(id) : next.add(id)
  selectedIds.value = next
}

const allSelected = (transactions: Transaction[]) =>
  transactions.length > 0 && transactions.every(t => selectedIds.value.has(t.id))

const toggleAll = (transactions: Transaction[]) => {
  if (allSelected(transactions)) {
    selectedIds.value = new Set()
  } else {
    selectedIds.value = new Set(transactions.map(t => t.id))
  }
}

const clearSelection = () => {
  selectedIds.value = new Set()
}

const handleBulkDelete = () => {
  emit('bulk-delete', [...selectedIds.value])
  clearSelection()
}

// --- Formatting helpers ---
const formatAmount = (amount: number) => {
  const isIncome = amount > 0
  const formatted = formatCurrency(Math.abs(amount))
  return {
    text: isIncome ? `+${formatted}` : `-${formatted}`,
    class: isIncome ? 'text-electric-green font-semibold' : 'text-danger-red font-semibold',
  }
}

const getPaymentMethodInfo = (method: string | null) => {
  const methods: Record<string, { label: string; icon: string; color: string }> = {
    card: { label: 'Card', icon: 'i-heroicons-credit-card', color: 'text-cyber-blue' },
    cash: { label: 'Cash', icon: 'i-heroicons-banknotes', color: 'text-electric-green' },
    blik: { label: 'BLIK', icon: 'i-heroicons-device-phone-mobile', color: 'text-purple-400' },
    transfer: { label: 'Przelew', icon: 'i-heroicons-arrows-right-left', color: 'text-warning-orange' },
    other: { label: 'Other', icon: 'i-heroicons-ellipsis-horizontal-circle', color: 'text-pure-white/60' },
  }
  return method && methods[method] ? methods[method] : { label: '-', icon: 'i-heroicons-minus-circle', color: 'text-pure-white/40' }
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <CommonEmptyState
      v-if="!loading && transactions.length === 0"
      icon="i-heroicons-banknotes"
      title="No transactions yet"
      description="Your transactions will appear here once you add them"
    />

    <div v-else>
      <!-- Bulk action bar -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="selectedIds.size > 0"
          class="flex items-center justify-between gap-3 px-4 py-3 bg-danger-red/10 border-b border-danger-red/30"
        >
          <div class="flex items-center gap-3">
            <!-- Checkbox "select all" -->
            <button
              class="w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors"
              :class="allSelected(transactions)
                ? 'bg-danger-red border-danger-red'
                : 'border-danger-red/60 hover:border-danger-red'"
              @click="toggleAll(transactions)"
            >
              <UIcon
                v-if="allSelected(transactions)"
                name="i-heroicons-check"
                class="w-3 h-3 text-pure-white"
              />
              <div
                v-else
                class="w-2 h-0.5 bg-danger-red rounded"
              />
            </button>
            <span class="text-sm font-medium text-danger-red">
              {{ selectedIds.size }} zaznaczonych
            </span>
          </div>

          <div class="flex items-center gap-2">
            <button
              class="text-xs text-pure-white/50 hover:text-pure-white transition-colors px-2 py-1"
              @click="clearSelection"
            >
              Odznacz
            </button>
            <BaseButton
              icon="i-heroicons-trash"
              size="sm"
              variant="danger"
              @click="handleBulkDelete"
            >
              Usuń {{ selectedIds.size }}
            </BaseButton>
          </div>
        </div>
      </Transition>

      <!-- Mobile: Card view -->
      <div class="sm:hidden divide-y divide-border-gray">
        <div
          v-for="transaction in transactions"
          :key="'m-' + transaction.id"
          class="flex items-stretch transition-colors"
          :class="isSelected(transaction.id) ? 'bg-danger-red/5' : 'hover:bg-card-black/30'"
        >
          <!-- Checkbox strip -->
          <button
            class="flex items-center justify-center w-11 shrink-0 border-r border-border-gray/40 transition-colors"
            :class="isSelected(transaction.id) ? 'bg-danger-red/10' : 'hover:bg-border-gray/20'"
            @click="toggleOne(transaction.id)"
          >
            <div
              class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
              :class="isSelected(transaction.id)
                ? 'bg-danger-red border-danger-red'
                : 'border-border-gray hover:border-danger-red/60'"
            >
              <UIcon
                v-if="isSelected(transaction.id)"
                name="i-heroicons-check"
                class="w-3 h-3 text-pure-white"
              />
            </div>
          </button>

          <!-- Card content -->
          <div class="flex-1 p-4 min-w-0">
            <!-- Top row: description + amount -->
            <div class="flex items-start justify-between gap-3 mb-2">
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-pure-white truncate">
                  {{ transaction.description || 'Brak opisu' }}
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

            <p v-if="transaction.notes" class="text-xs text-pure-white/40 mt-1.5 truncate">
              {{ truncateText(transaction.notes, 60) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Desktop: Table view -->
      <div class="hidden sm:block overflow-x-auto">
        <table class="w-full">
          <thead class="bg-card-black/50 border-b border-border-gray">
            <tr>
              <!-- Select all checkbox -->
              <th class="pl-4 pr-2 py-4 w-10">
                <button
                  class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
                  :class="allSelected(transactions)
                    ? 'bg-electric-green border-electric-green'
                    : selectedIds.size > 0
                      ? 'border-electric-green/60 hover:border-electric-green'
                      : 'border-border-gray hover:border-electric-green/60'"
                  @click="toggleAll(transactions)"
                >
                  <UIcon
                    v-if="allSelected(transactions)"
                    name="i-heroicons-check"
                    class="w-3 h-3 text-background-black"
                  />
                  <div
                    v-else-if="selectedIds.size > 0"
                    class="w-2 h-0.5 bg-electric-green/60 rounded"
                  />
                </button>
              </th>
              <th class="px-4 py-4 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Data
              </th>
              <th class="px-4 py-4 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Opis
              </th>
              <th class="px-4 py-4 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Kategoria
              </th>
              <th class="px-4 py-4 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Płatność
              </th>
              <th class="px-4 py-4 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Kwota
              </th>
              <th class="px-4 py-4 w-20" />
            </tr>
          </thead>
          <tbody class="divide-y divide-border-gray">
            <tr
              v-for="transaction in transactions"
              :key="transaction.id"
              class="transition-colors"
              :class="isSelected(transaction.id) ? 'bg-electric-green/5' : 'hover:bg-card-black/30'"
            >
              <!-- Row checkbox -->
              <td class="pl-4 pr-2 py-4 w-10">
                <button
                  class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
                  :class="isSelected(transaction.id)
                    ? 'bg-electric-green border-electric-green'
                    : 'border-border-gray hover:border-electric-green/60'"
                  @click="toggleOne(transaction.id)"
                >
                  <UIcon
                    v-if="isSelected(transaction.id)"
                    name="i-heroicons-check"
                    class="w-3 h-3 text-background-black"
                  />
                </button>
              </td>

              <td class="px-4 py-4 whitespace-nowrap text-sm text-pure-white">
                {{ formatDate(transaction.date) }}
              </td>

              <td class="px-4 py-4 text-sm text-pure-white max-w-xs">
                <div class="font-medium truncate">
                  {{ transaction.description || 'Brak opisu' }}
                </div>
                <div v-if="transaction.notes" class="text-xs text-pure-white/60 mt-1 truncate">
                  {{ truncateText(transaction.notes, 50) }}
                </div>
              </td>

              <td class="px-4 py-4 whitespace-nowrap">
                <CategoryBadge :category="transaction.category" />
              </td>

              <td class="px-4 py-4 whitespace-nowrap text-sm">
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

              <td class="px-4 py-4 whitespace-nowrap text-sm">
                <span :class="formatAmount(transaction.amount).class">
                  {{ formatAmount(transaction.amount).text }}
                </span>
              </td>

              <td class="px-4 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-1">
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
