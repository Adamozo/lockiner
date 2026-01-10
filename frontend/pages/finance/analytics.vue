<script setup lang="ts">
import { formatCurrency } from '~/utils/formatters'
import type { MonthSummary, YearlySummary, BudgetStatus } from '~/types/api'

// Page metadata
definePageMeta({
  layout: 'finance',
})

useSeoMeta({
  title: 'Analytics - LockIner',
  description: 'Comprehensive overview of your spending patterns and financial health',
})

const { currentHouseholdId, householdIdForApi, isPersonalContext } = useHouseholdContext()
const { getMonthlySummary, getYearlySummary, getBudgetStatus } = useAnalytics()
const { activeAlerts, checkAndDisplayAlerts } = useBudgetAlerts()
const toast = useToast()

// View mode: 'month' or 'year'
const viewMode = ref<'month' | 'year'>('month')

// Current selected month/year
const now = new Date()
const currentMonth = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)
const currentYear = ref(String(now.getFullYear()))

// Data states
const monthlySummary = ref<MonthSummary | null>(null)
const yearlySummary = ref<YearlySummary | null>(null)
const budgetStatus = ref<BudgetStatus[]>([])
const loading = ref(false)

// Fetch data based on view mode
const fetchData = async () => {
  loading.value = true
  try {
    if (viewMode.value === 'month') {
      [monthlySummary.value, budgetStatus.value] = await Promise.all([
        getMonthlySummary(currentMonth.value, householdIdForApi.value),
        getBudgetStatus(currentMonth.value, householdIdForApi.value),
      ])
      // Check for budget alerts
      await checkAndDisplayAlerts(currentMonth.value, false, householdIdForApi.value)
    } else {
      yearlySummary.value = await getYearlySummary(currentYear.value, householdIdForApi.value)
    }
  } catch (error) {
    toast.add({
      title: 'Error',
      description: error instanceof Error ? error.message : 'Failed to load analytics',
      color: 'red',
    })
  } finally {
    loading.value = false
  }
}

// Watch for changes in view mode, selected period, or context
watch([viewMode, currentMonth, currentYear], () => {
  fetchData()
})

// Reload data when context changes
watch(() => currentHouseholdId.value, fetchData)

// Initial data load
onMounted(() => {
  fetchData()
})

// Navigation between months
const previousMonth = () => {
  const [year, month] = currentMonth.value.split('-').map(Number)
  const date = new Date(year, month - 2) // month-2 because month is 1-indexed, -1 for previous
  currentMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

const nextMonth = () => {
  const [year, month] = currentMonth.value.split('-').map(Number)
  const date = new Date(year, month) // month is already 1-indexed, so this gives us next month
  currentMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

// Navigation between years
const previousYear = () => {
  currentYear.value = String(Number(currentYear.value) - 1)
}

const nextYear = () => {
  currentYear.value = String(Number(currentYear.value) + 1)
}

// Format month for display
const formatMonthDisplay = (month: string) => {
  const [year, monthNum] = month.split('-')
  const date = new Date(Number(year), Number(monthNum) - 1)
  return date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'long' })
}

// Computed summary data
const summaryData = computed(() => {
  if (viewMode.value === 'month' && monthlySummary.value) {
    return {
      income: monthlySummary.value.total_income,
      expenses: monthlySummary.value.total_expenses,
      net: monthlySummary.value.net_amount,
      count: monthlySummary.value.transactions_count,
    }
  } else if (viewMode.value === 'year' && yearlySummary.value) {
    return {
      income: yearlySummary.value.total_income,
      expenses: yearlySummary.value.total_expenses,
      net: yearlySummary.value.net_amount,
      count: yearlySummary.value.transactions_count,
    }
  }
  return { income: 0, expenses: 0, net: 0, count: 0 }
})
</script>

<template>
  <div class="max-w-7xl">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-pure-white mb-2">
        Financial Analytics
      </h1>
      <p class="text-pure-white/60">
        Comprehensive overview of your spending patterns and financial health
      </p>
    </div>

    <!-- View Mode Toggle & Period Selector -->
    <div class="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <!-- View Mode Tabs -->
      <div class="inline-flex rounded-lg bg-card-black border border-border-gray p-1">
        <button
          :class="viewMode === 'month'
            ? 'bg-electric-green text-background-black'
            : 'text-pure-white hover:text-electric-green'"
          class="px-4 py-2 rounded-md font-semibold transition-all duration-300"
          @click="viewMode = 'month'"
        >
          Monthly
        </button>
        <button
          :class="viewMode === 'year'
            ? 'bg-electric-green text-background-black'
            : 'text-pure-white hover:text-electric-green'"
          class="px-4 py-2 rounded-md font-semibold transition-all duration-300"
          @click="viewMode = 'year'"
        >
          Yearly
        </button>
      </div>

      <!-- Period Navigation -->
      <div class="flex items-center gap-3">
        <button
          class="p-2 rounded-md bg-card-black border border-border-gray hover:border-electric-green transition-colors"
          :disabled="loading"
          @click="viewMode === 'month' ? previousMonth() : previousYear()"
        >
          <UIcon name="i-heroicons-chevron-left" class="w-5 h-5 text-pure-white" />
        </button>

        <span class="text-pure-white font-semibold text-lg min-w-[200px] text-center">
          {{ viewMode === 'month' ? formatMonthDisplay(currentMonth) : currentYear }}
        </span>

        <button
          class="p-2 rounded-md bg-card-black border border-border-gray hover:border-electric-green transition-colors"
          :disabled="loading"
          @click="viewMode === 'month' ? nextMonth() : nextYear()"
        >
          <UIcon name="i-heroicons-chevron-right" class="w-5 h-5 text-pure-white" />
        </button>
      </div>
    </div>

    <!-- Budget Alert Banner -->
    <BudgetAlertBanner v-if="viewMode === 'month' && activeAlerts.length > 0" :alerts="activeAlerts" />

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-electric-green mx-auto mb-4"></div>
        <p class="text-pure-white/60">Loading analytics...</p>
      </div>
    </div>

    <!-- Analytics Content -->
    <div v-else>
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <!-- Total Income -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-pure-white/60 text-sm">Total Income</span>
            <UIcon name="i-heroicons-arrow-trending-up" class="w-5 h-5 text-electric-green" />
          </div>
          <p class="text-2xl font-bold text-electric-green">
            {{ formatCurrency(summaryData.income) }}
          </p>
        </div>

        <!-- Total Expenses -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-pure-white/60 text-sm">Total Expenses</span>
            <UIcon name="i-heroicons-arrow-trending-down" class="w-5 h-5 text-danger-red" />
          </div>
          <p class="text-2xl font-bold text-danger-red">
            {{ formatCurrency(summaryData.expenses) }}
          </p>
        </div>

        <!-- Net Balance -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-pure-white/60 text-sm">Net Balance</span>
            <UIcon name="i-heroicons-banknotes" class="w-5 h-5 text-cyber-blue" />
          </div>
          <p class="text-2xl font-bold" :class="summaryData.net >= 0 ? 'text-electric-green' : 'text-danger-red'">
            {{ formatCurrency(summaryData.net) }}
          </p>
        </div>

        <!-- Transaction Count -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-pure-white/60 text-sm">Transactions</span>
            <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-pure-white/60" />
          </div>
          <p class="text-2xl font-bold text-pure-white">
            {{ summaryData.count }}
          </p>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Category Spending Pie Chart -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <h3 class="text-xl font-semibold text-pure-white mb-4">
            Spending by Category
          </h3>
          <CategoryPieChart
            v-if="viewMode === 'month' && monthlySummary"
            :data="monthlySummary.by_category"
          />
          <CategoryPieChart
            v-else-if="viewMode === 'year' && yearlySummary"
            :data="yearlySummary.by_category"
          />
          <p v-else class="text-pure-white/40 text-center py-8">
            No data available
          </p>
        </div>

        <!-- Merchant Spending Bar Chart -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <h3 class="text-xl font-semibold text-pure-white mb-4">
            Top Merchants
          </h3>
          <MerchantBarChart :month="viewMode === 'month' ? currentMonth : undefined" />
        </div>
      </div>

      <!-- Trends Line Chart (Full Width) -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 mb-8">
        <h3 class="text-xl font-semibold text-pure-white mb-4">
          Spending Trends
        </h3>
        <TrendsLineChart :months="viewMode === 'month' ? 6 : 12" />
      </div>

      <!-- Budget Status (Monthly View Only) -->
      <div v-if="viewMode === 'month' && budgetStatus.length > 0" class="bg-card-black border border-border-gray rounded-lg p-6">
        <h3 class="text-xl font-semibold text-pure-white mb-4">
          Budget Status
        </h3>
        <BudgetProgress :budgets="budgetStatus" />
      </div>
    </div>
  </div>
</template>
