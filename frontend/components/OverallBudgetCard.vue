<script setup lang="ts">
import { formatCurrency } from '~/utils/formatters'
import type { OverallBudgetStatus } from '~/types/api'

const props = defineProps<{
  budget: OverallBudgetStatus
}>()

// Get status color
const getStatusColor = (status: string) => {
  switch (status) {
    case 'ok':
      return 'bg-electric-green'
    case 'warning':
      return 'bg-warning-orange'
    case 'over':
      return 'bg-danger-red'
    case 'no_limit':
      return 'bg-pure-white/20'
    default:
      return 'bg-pure-white/20'
  }
}

const getStatusTextColor = (status: string) => {
  switch (status) {
    case 'ok':
      return 'text-electric-green'
    case 'warning':
      return 'text-warning-orange'
    case 'over':
      return 'text-danger-red'
    case 'no_limit':
      return 'text-pure-white/60'
    default:
      return 'text-pure-white/60'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'ok':
      return 'i-heroicons-check-circle'
    case 'warning':
      return 'i-heroicons-exclamation-triangle'
    case 'over':
      return 'i-heroicons-x-circle'
    case 'no_limit':
      return 'i-heroicons-minus-circle'
    default:
      return 'i-heroicons-minus-circle'
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'ok':
      return 'On Track'
    case 'warning':
      return 'Warning'
    case 'over':
      return 'Over Budget'
    case 'no_limit':
      return 'No Limit Set'
    default:
      return 'Unknown'
  }
}
</script>

<template>
  <div
    class="bg-gradient-to-br from-card-black to-background-black rounded-xl p-4 sm:p-6 border-2 transition-all duration-300 hover:shadow-xl"
    :class="
      budget.status === 'over'
        ? 'border-danger-red'
        : budget.status === 'warning'
        ? 'border-warning-orange'
        : budget.status === 'ok'
        ? 'border-electric-green'
        : 'border-border-gray'
    "
  >
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <div class="flex items-center gap-3">
        <div class="p-2 sm:p-3 rounded-full bg-cyber-blue/20 shrink-0">
          <UIcon name="i-heroicons-banknotes" class="w-5 h-5 sm:w-7 sm:h-7 text-cyber-blue" />
        </div>
        <div class="min-w-0">
          <h3 class="text-lg sm:text-xl font-bold text-pure-white">Overall Monthly Budget</h3>
          <p class="text-sm text-pure-white/60">{{ budget.month }}</p>
        </div>
      </div>

      <div
        class="flex items-center gap-2 px-3 py-1.5 rounded-full border self-start sm:self-auto shrink-0"
        :class="getStatusTextColor(budget.status)"
      >
        <UIcon :name="getStatusIcon(budget.status)" class="w-4 h-4 sm:w-5 sm:h-5" />
        <span class="text-xs sm:text-sm font-semibold">{{ getStatusLabel(budget.status) }}</span>
      </div>
    </div>

    <!-- Alert Message -->
    <div
      v-if="budget.alert_message"
      class="mb-3 sm:mb-4 p-2 sm:p-3 rounded-lg border flex items-start gap-2"
      :class="
        budget.status === 'over'
          ? 'bg-danger-red/10 border-danger-red text-danger-red'
          : 'bg-warning-orange/10 border-warning-orange text-warning-orange'
      "
    >
      <UIcon
        :name="
          budget.status === 'over' ? 'i-heroicons-exclamation-circle' : 'i-heroicons-exclamation-triangle'
        "
        class="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0 mt-0.5"
      />
      <p class="text-xs sm:text-sm font-medium">{{ budget.alert_message }}</p>
    </div>

    <!-- Budget Info -->
    <div v-if="budget.overall_limit" class="space-y-3 sm:space-y-4">
      <div class="flex items-end justify-between gap-2">
        <div class="min-w-0">
          <p class="text-xs sm:text-sm text-pure-white/60 mb-1">Spent This Month</p>
          <p class="text-xl sm:text-3xl font-bold text-pure-white truncate">
            {{ formatCurrency(budget.total_spent) }}
          </p>
        </div>
        <div class="text-right shrink-0">
          <p class="text-xs sm:text-sm text-pure-white/60 mb-1">Monthly Limit</p>
          <p class="text-base sm:text-xl font-semibold text-pure-white/80">
            {{ formatCurrency(budget.overall_limit) }}
          </p>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="relative w-full h-3 sm:h-4 bg-card-black rounded-full overflow-hidden">
        <div
          class="absolute top-0 left-0 h-full transition-all duration-500"
          :class="getStatusColor(budget.status)"
          :style="{ width: `${Math.min(budget.percentage, 100)}%` }"
        ></div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-2 sm:gap-4">
        <div class="bg-card-black/50 rounded-lg p-2 sm:p-3">
          <p class="text-[10px] sm:text-xs text-pure-white/60 mb-1">Remaining</p>
          <p
            class="text-sm sm:text-lg font-semibold truncate"
            :class="budget.remaining >= 0 ? 'text-electric-green' : 'text-danger-red'"
          >
            {{
              budget.remaining >= 0
                ? formatCurrency(budget.remaining)
                : formatCurrency(Math.abs(budget.remaining))
            }}
          </p>
        </div>
        <div class="bg-card-black/50 rounded-lg p-2 sm:p-3">
          <p class="text-[10px] sm:text-xs text-pure-white/60 mb-1">Used</p>
          <p class="text-sm sm:text-lg font-semibold" :class="getStatusTextColor(budget.status)">
            {{ budget.percentage.toFixed(1) }}%
          </p>
        </div>
      </div>
    </div>

    <!-- No Limit Set -->
    <div v-else class="text-center py-4 sm:py-6">
      <UIcon name="i-heroicons-minus-circle" class="w-10 h-10 sm:w-12 sm:h-12 text-pure-white/40 mx-auto mb-2 sm:mb-3" />
      <p class="text-sm sm:text-base text-pure-white/60 mb-2">No overall budget limit set</p>
      <p class="text-xl sm:text-2xl font-bold text-pure-white mb-1">
        {{ formatCurrency(budget.total_spent) }}
      </p>
      <p class="text-xs sm:text-sm text-pure-white/40">spent this month</p>
    </div>
  </div>
</template>
