<script setup lang="ts">
import { useHouseholds } from '~/composables/useHouseholds'
import { useAnalytics } from '~/composables/useAnalytics'
import { usePermissions } from '~/composables/usePermissions'
import type {
  HouseholdMonthlySummary,
  HouseholdSpendingByMember,
  HouseholdSpendingByCategory,
} from '~/types/api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const householdUid = computed(() => route.params.uid as string)

const { currentHousehold, fetchHousehold } = useHouseholds()
const { isBlocked, canViewAnalytics } = usePermissions()
const {
  getHouseholdMonthlySummary,
  getHouseholdSpendingByMember,
  getHouseholdSpendingByCategory,
} = useAnalytics()

// State
const loading = ref(true)
const error = ref<string | null>(null)
const selectedMonth = ref(new Date().toISOString().slice(0, 7)) // YYYY-MM

const summary = ref<HouseholdMonthlySummary | null>(null)
const spendingByMember = ref<HouseholdSpendingByMember | null>(null)
const spendingByCategory = ref<HouseholdSpendingByCategory | null>(null)

// Available months (last 12 months)
const availableMonths = computed(() => {
  const months = []
  const now = new Date()
  for (let i = 0; i < 12; i++) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const value = date.toISOString().slice(0, 7)
    const label = date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'long' })
    months.push({ value, label })
  }
  return months
})

// Fetch all analytics data
const fetchAnalytics = async () => {
  loading.value = true
  error.value = null

  try {
    const [summaryData, memberData, categoryData] = await Promise.all([
      getHouseholdMonthlySummary(householdUid.value, selectedMonth.value),
      getHouseholdSpendingByMember(householdUid.value, selectedMonth.value),
      getHouseholdSpendingByCategory(householdUid.value, selectedMonth.value),
    ])

    summary.value = summaryData
    spendingByMember.value = memberData
    spendingByCategory.value = categoryData
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'Failed to load analytics'
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(async () => {
  await fetchHousehold(householdUid.value)
  await fetchAnalytics()
})

// Watch for month changes
watch(selectedMonth, () => {
  fetchAnalytics()
})

// Update SEO
watchEffect(() => {
  if (currentHousehold.value) {
    useSeoMeta({
      title: `Analytics - ${currentHousehold.value.name} - LockIner`,
      description: `View spending analytics for ${currentHousehold.value.name}`,
    })
  }
})

// Format currency
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
  }).format(amount)
}

// Get color for member (cycle through colors)
const memberColors = [
  'bg-cyber-blue',
  'bg-electric-green',
  'bg-purple-500',
  'bg-orange-500',
  'bg-pink-500',
  'bg-yellow-500',
  'bg-cyan-500',
  'bg-indigo-500',
]

const getMemberColor = (index: number): string => {
  return memberColors[index % memberColors.length]
}
</script>

<template>
  <div class="space-y-8">
    <!-- Blocked access -->
    <CommonBlockedAccess
      v-if="currentHousehold && isBlocked"
      :household-name="currentHousehold.name"
    />

    <template v-else>
    <!-- Header -->
    <header>
      <NuxtLink
        :to="`/households/${householdUid}`"
        class="inline-flex items-center gap-2 text-pure-white/60 hover:text-pure-white transition-colors mb-4"
      >
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        <span>Back to {{ currentHousehold?.name || 'Household' }}</span>
      </NuxtLink>

      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold text-pure-white">Analytics</h1>
          <p class="mt-2 text-pure-white/60">
            Spending insights for {{ currentHousehold?.name }}
          </p>
        </div>

        <!-- Month selector -->
        <div class="flex-shrink-0">
          <select
            v-model="selectedMonth"
            class="px-4 py-2.5 border border-border-gray rounded-lg bg-background-black text-pure-white focus:outline-none focus:ring-2 focus:border-cyber-blue focus:ring-cyber-blue/30"
          >
            <option
              v-for="month in availableMonths"
              :key="month.value"
              :value="month.value"
            >
              {{ month.label }}
            </option>
          </select>
        </div>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-8 h-8 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="p-6 bg-danger-red/10 border border-danger-red/30 rounded-lg"
    >
      <div class="flex items-center gap-3 text-danger-red">
        <UIcon name="i-heroicons-exclamation-circle" class="w-6 h-6" />
        <span>{{ error }}</span>
      </div>
    </div>

    <!-- Analytics content -->
    <template v-else>
      <!-- Summary cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-full bg-electric-green/10 flex items-center justify-center">
              <UIcon name="i-heroicons-arrow-trending-up" class="w-5 h-5 text-electric-green" />
            </div>
            <span class="text-sm text-pure-white/60">Income</span>
          </div>
          <p class="text-2xl font-bold text-electric-green">
            {{ formatCurrency(summary?.total_income || 0) }}
          </p>
        </div>

        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-full bg-danger-red/10 flex items-center justify-center">
              <UIcon name="i-heroicons-arrow-trending-down" class="w-5 h-5 text-danger-red" />
            </div>
            <span class="text-sm text-pure-white/60">Expenses</span>
          </div>
          <p class="text-2xl font-bold text-danger-red">
            {{ formatCurrency(summary?.total_expenses || 0) }}
          </p>
        </div>

        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-full bg-cyber-blue/10 flex items-center justify-center">
              <UIcon name="i-heroicons-scale" class="w-5 h-5 text-cyber-blue" />
            </div>
            <span class="text-sm text-pure-white/60">Net</span>
          </div>
          <p
            class="text-2xl font-bold"
            :class="(summary?.net_amount || 0) >= 0 ? 'text-electric-green' : 'text-danger-red'"
          >
            {{ formatCurrency(summary?.net_amount || 0) }}
          </p>
        </div>

        <div class="bg-card-black border border-border-gray rounded-lg p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-full bg-purple-500/10 flex items-center justify-center">
              <UIcon name="i-heroicons-receipt-percent" class="w-5 h-5 text-purple-500" />
            </div>
            <span class="text-sm text-pure-white/60">Transactions</span>
          </div>
          <p class="text-2xl font-bold text-pure-white">
            {{ summary?.transactions_count || 0 }}
          </p>
        </div>
      </div>

      <!-- Spending by member -->
      <div class="bg-card-black border border-border-gray rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-border-gray relative">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
          <h2 class="text-xl font-semibold text-pure-white">Spending by Member</h2>
        </div>

        <div class="p-6">
          <div
            v-if="!spendingByMember?.members.length"
            class="text-center py-8 text-pure-white/40"
          >
            No spending data for this month
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="(member, index) in spendingByMember.members"
              :key="member.user_id"
              class="space-y-2"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div
                    class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    :class="getMemberColor(index)"
                  >
                    {{ member.user_name.charAt(0).toUpperCase() }}
                  </div>
                  <span class="text-pure-white">{{ member.user_name }}</span>
                </div>
                <div class="text-right">
                  <span class="text-pure-white font-medium">{{ formatCurrency(member.total) }}</span>
                  <span class="text-pure-white/40 text-sm ml-2">({{ member.percentage.toFixed(1) }}%)</span>
                </div>
              </div>

              <!-- Progress bar -->
              <div class="h-2 bg-background-black rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="getMemberColor(index)"
                  :style="{ width: `${member.percentage}%` }"
                />
              </div>

              <div class="flex justify-between text-xs text-pure-white/40">
                <span>{{ member.count }} transactions</span>
                <span>Avg: {{ formatCurrency(member.average) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Spending by category -->
      <div class="bg-card-black border border-border-gray rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-border-gray relative">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-purple-500 to-pink-500" />
          <h2 class="text-xl font-semibold text-pure-white">Spending by Category</h2>
        </div>

        <div class="p-6">
          <div
            v-if="!spendingByCategory?.categories.length"
            class="text-center py-8 text-pure-white/40"
          >
            No spending data for this month
          </div>

          <div v-else class="space-y-6 max-h-[480px] overflow-y-auto pr-1 scrollbar-thin">
            <div
              v-for="category in spendingByCategory.categories"
              :key="category.category"
              class="space-y-3"
            >
              <!-- Category header -->
              <div class="flex items-center justify-between">
                <span class="text-pure-white font-medium">{{ category.category }}</span>
                <div class="text-right">
                  <span class="text-pure-white">{{ formatCurrency(category.total) }}</span>
                  <span class="text-pure-white/40 text-sm ml-2">({{ category.percentage.toFixed(1) }}%)</span>
                </div>
              </div>

              <!-- Overall progress bar -->
              <div class="h-3 bg-background-black rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-cyber-blue to-electric-green rounded-full transition-all duration-500"
                  :style="{ width: `${category.percentage}%` }"
                />
              </div>

              <!-- Member breakdown -->
              <div
                v-if="category.by_member.length > 0"
                class="ml-4 space-y-2 text-sm"
              >
                <div
                  v-for="(member, mIndex) in category.by_member"
                  :key="member.user_id"
                  class="flex items-center justify-between text-pure-white/60"
                >
                  <div class="flex items-center gap-2">
                    <div
                      class="w-4 h-4 rounded-full flex items-center justify-center text-white text-[10px] font-medium"
                      :class="getMemberColor(mIndex)"
                    >
                      {{ member.user_name.charAt(0).toUpperCase() }}
                    </div>
                    <span>{{ member.user_name }}</span>
                  </div>
                  <span>{{ formatCurrency(member.total) }} ({{ member.percentage.toFixed(1) }}%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Member breakdown from summary -->
      <div
        v-if="summary?.by_member && summary.by_member.length > 0"
        class="bg-card-black border border-border-gray rounded-lg overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-border-gray relative">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-orange-500 to-yellow-500" />
          <h2 class="text-xl font-semibold text-pure-white">Member Overview</h2>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-border-gray">
                <th class="px-6 py-3 text-left text-sm font-medium text-pure-white/60">Member</th>
                <th class="px-6 py-3 text-right text-sm font-medium text-pure-white/60">Spent</th>
                <th class="px-6 py-3 text-right text-sm font-medium text-pure-white/60">Transactions</th>
                <th class="px-6 py-3 text-right text-sm font-medium text-pure-white/60">Average</th>
                <th class="px-6 py-3 text-right text-sm font-medium text-pure-white/60">Share</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(member, index) in summary.by_member"
                :key="member.user_id"
                class="border-b border-border-gray/50 last:border-0"
              >
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div
                      class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                      :class="getMemberColor(index)"
                    >
                      {{ member.user_name.charAt(0).toUpperCase() }}
                    </div>
                    <span class="text-pure-white">{{ member.user_name }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-right text-pure-white">
                  {{ formatCurrency(member.total) }}
                </td>
                <td class="px-6 py-4 text-right text-pure-white/60">
                  {{ member.count }}
                </td>
                <td class="px-6 py-4 text-right text-pure-white/60">
                  {{ formatCurrency(member.average) }}
                </td>
                <td class="px-6 py-4 text-right">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyber-blue/10 text-cyber-blue">
                    {{ member.percentage.toFixed(1) }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
    </template>
  </div>
</template>
