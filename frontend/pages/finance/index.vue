<script setup lang="ts">
// Finance Dashboard page
definePageMeta({
  layout: 'finance',
})

useSeoMeta({
  title: "Finance Dashboard - LockIner",
  description: "Overview of your finances",
})

const { currentHouseholdId, householdIdForApi, isPersonalContext } = useHouseholdContext()
const { transactions, loading, fetchTransactions } = useTransactions()

// Load data function
const loadData = async () => {
  try {
    await fetchTransactions({
      householdId: householdIdForApi.value,
      limit: 10,
    })
  } catch (error) {
    console.error("Failed to fetch transactions:", error)
  }
}

// Fetch recent transactions on mount
onMounted(loadData)

// Reload data when context changes
watch(() => currentHouseholdId.value, loadData)

// Calculate basic stats
const stats = computed(() => {
  const income = transactions.value
    .filter((t) => t.amount > 0)
    .reduce((sum, t) => sum + t.amount, 0)

  const expenses = transactions.value
    .filter((t) => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(t.amount), 0)

  return {
    income,
    expenses,
    balance: income - expenses,
    count: transactions.value.length,
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div>
      <h1 class="text-3xl font-bold text-pure-white">Dashboard</h1>
      <p class="mt-2 text-pure-white/60">
        Overview of your {{ isPersonalContext ? 'personal' : 'household' }} finances
      </p>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Total Income -->
      <div
        class="bg-card-black border border-border-gray rounded-lg shadow-lg p-6 relative overflow-hidden transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-electric-green/10"
      >
        <!-- Top gradient border -->
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
        ></div>

        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Total Income</p>
            <p class="mt-2 text-3xl font-bold text-electric-green">
              {{ formatCurrency(stats.income) }}
            </p>
          </div>
          <div
            class="p-3 bg-gradient-to-br from-electric-green/20 to-electric-green/5 rounded-full border border-electric-green/30 shadow-lg shadow-electric-green/20"
          >
            <UIcon
              name="i-heroicons-arrow-trending-up"
              class="w-8 h-8 text-electric-green"
            />
          </div>
        </div>
      </div>

      <!-- Total Expenses -->
      <div
        class="bg-card-black border border-border-gray rounded-lg shadow-lg p-6 relative overflow-hidden transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-danger-red/10"
      >
        <!-- Top gradient border -->
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-danger-red to-pink-500"
        ></div>

        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Total Expenses</p>
            <p class="mt-2 text-3xl font-bold text-danger-red">
              {{ formatCurrency(stats.expenses) }}
            </p>
          </div>
          <div
            class="p-3 bg-gradient-to-br from-danger-red/20 to-danger-red/5 rounded-full border border-danger-red/30 shadow-lg shadow-danger-red/20"
          >
            <UIcon
              name="i-heroicons-arrow-trending-down"
              class="w-8 h-8 text-danger-red"
            />
          </div>
        </div>
      </div>

      <!-- Balance -->
      <div
        class="bg-card-black border border-border-gray rounded-lg shadow-lg p-6 relative overflow-hidden transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-cyber-blue/10"
      >
        <!-- Top gradient border -->
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
        ></div>

        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Balance</p>
            <p
              class="mt-2 text-3xl font-bold"
              :class="
                stats.balance >= 0 ? 'text-electric-green' : 'text-danger-red'
              "
            >
              {{ formatCurrency(stats.balance) }}
            </p>
          </div>
          <div
            class="p-3 bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 rounded-full border border-cyber-blue/30 shadow-lg shadow-cyber-blue/20"
          >
            <UIcon name="i-heroicons-wallet" class="w-8 h-8 text-cyber-blue" />
          </div>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="bg-card-black border border-border-gray rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold text-pure-white mb-4">Quick Actions</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <NuxtLink
          to="/finance/transactions"
          class="flex flex-col items-center p-4 rounded-lg border-2 border-border-gray bg-card-black/50 backdrop-blur-sm transition-all duration-300 hover:border-electric-green hover:-translate-y-1 hover:shadow-lg hover:shadow-electric-green/20 hover:bg-card-black"
        >
          <UIcon
            name="i-heroicons-banknotes"
            class="w-8 h-8 text-electric-green mb-2"
          />
          <span class="text-sm font-medium text-pure-white">Transactions</span>
        </NuxtLink>

        <NuxtLink
          to="/finance/receipts"
          class="flex flex-col items-center p-4 rounded-lg border-2 border-border-gray bg-card-black/50 backdrop-blur-sm transition-all duration-300 hover:border-electric-green hover:-translate-y-1 hover:shadow-lg hover:shadow-electric-green/20 hover:bg-card-black"
        >
          <UIcon
            name="i-heroicons-document-text"
            class="w-8 h-8 text-electric-green mb-2"
          />
          <span class="text-sm font-medium text-pure-white">Receipts</span>
        </NuxtLink>

        <NuxtLink
          to="/finance/analytics"
          class="flex flex-col items-center p-4 rounded-lg border-2 border-border-gray bg-card-black/50 backdrop-blur-sm transition-all duration-300 hover:border-electric-green hover:-translate-y-1 hover:shadow-lg hover:shadow-electric-green/20 hover:bg-card-black"
        >
          <UIcon
            name="i-heroicons-chart-bar"
            class="w-8 h-8 text-electric-green mb-2"
          />
          <span class="text-sm font-medium text-pure-white">Analytics</span>
        </NuxtLink>

        <NuxtLink
          to="/finance/limits"
          class="flex flex-col items-center p-4 rounded-lg border-2 border-border-gray bg-card-black/50 backdrop-blur-sm transition-all duration-300 hover:border-electric-green hover:-translate-y-1 hover:shadow-lg hover:shadow-electric-green/20 hover:bg-card-black"
        >
          <UIcon
            name="i-heroicons-scale"
            class="w-8 h-8 text-electric-green mb-2"
          />
          <span class="text-sm font-medium text-pure-white">Limits</span>
        </NuxtLink>
      </div>
    </div>

    <!-- Recent transactions -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-pure-white">
          Recent Transactions
        </h2>
        <NuxtLink to="/finance/transactions">
          <UButton
            variant="ghost"
            trailing-icon="i-heroicons-arrow-right"
            class="text-electric-green hover:text-cyber-blue"
          >
            View all
          </UButton>
        </NuxtLink>
      </div>

      <TransactionList
        :transactions="transactions"
        :loading="loading"
        @edit="() => navigateTo('/finance/transactions')"
        @delete="(id) => console.log('Delete', id)"
      />
    </div>
  </div>
</template>
