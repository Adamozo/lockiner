<script setup lang="ts">
import type { Transaction, TransactionCreate } from '~/types/api'

definePageMeta({
  layout: 'finance',
})

useSeoMeta({
  title: 'Transactions - LockIner',
  description: 'Manage your financial transactions',
})

const { currentHouseholdId, householdIdForApi, isPersonalContext } = useHouseholdContext()
const categoriesStore = useCategoriesStore()
const {
  transactions,
  loading,
  error,
  fetchTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
} = useTransactions()

const toast = useToast()

// UI state
const isAddModalOpen = ref(false)
const isEditModalOpen = ref(false)
const isImportModalOpen = ref(false)
const editingTransaction = ref<Transaction | null>(null)

// Load data function
const loadData = async () => {
  try {
    await fetchTransactions({ householdId: householdIdForApi.value })
  } catch (err) {
    console.error('Failed to fetch transactions:', err)
    toast.add({
      title: 'Error',
      description: 'Failed to load transactions. Please check if the backend is running.',
      color: 'red',
    })
  }
}

// Fetch transactions on mount
onMounted(loadData)

// Reload data when context changes
watch(() => currentHouseholdId.value, loadData)

// Handle add transaction
const handleAddTransaction = async (transaction: TransactionCreate) => {
  try {
    await createTransaction(transaction, householdIdForApi.value)
    isAddModalOpen.value = false
    await loadData()

    toast.add({
      title: 'Success',
      description: 'Transaction added successfully',
      color: 'green',
    })
  } catch (err) {
    toast.add({
      title: 'Error',
      description: err instanceof Error ? err.message : 'Failed to add transaction',
      color: 'red',
    })
  }
}

const handleAddCancel = () => {
  isAddModalOpen.value = false
}

// Handle edit transaction
const handleEditClick = (transaction: Transaction) => {
  editingTransaction.value = transaction
  isEditModalOpen.value = true
}

const handleUpdateTransaction = async (updates: TransactionCreate) => {
  if (!editingTransaction.value) return

  try {
    await updateTransaction(editingTransaction.value.id, updates, householdIdForApi.value)
    isEditModalOpen.value = false
    editingTransaction.value = null
    await loadData()

    toast.add({
      title: 'Success',
      description: 'Transaction updated successfully',
      color: 'green',
    })
  } catch (err) {
    toast.add({
      title: 'Error',
      description: err instanceof Error ? err.message : 'Failed to update transaction',
      color: 'red',
    })
  }
}

const handleEditCancel = () => {
  isEditModalOpen.value = false
  editingTransaction.value = null
}

const { confirm } = useConfirm()

// Handle delete transaction
const handleDeleteTransaction = async (id: number) => {
  if (!await confirm({ message: 'Are you sure you want to delete this transaction?', confirmText: 'Delete' }))
    return

  try {
    await deleteTransaction(id, householdIdForApi.value)
    await loadData()
    toast.add({
      title: 'Success',
      description: 'Transaction deleted successfully',
      color: 'green',
    })
  } catch (err) {
    toast.add({
      title: 'Error',
      description: err instanceof Error ? err.message : 'Failed to delete transaction',
      color: 'red',
    })
  }
}

const openAddModal = () => {
  isAddModalOpen.value = true
}

const openImportModal = () => {
  isImportModalOpen.value = true
}

// Handle successful import
const handleImportSuccess = async () => {
  // Refresh transactions list
  await loadData()
}

// Stats with icon data
const stats = computed(() => {
  const income = transactions.value
    .filter(t => t.amount > 0)
    .reduce((sum, t) => sum + t.amount, 0)

  const expenses = transactions.value
    .filter(t => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(t.amount), 0)

  return [
    {
      name: 'Total Transactions',
      value: transactions.value.length,
      icon: 'i-heroicons-banknotes',
      color: 'blue' as const,
    },
    {
      name: 'Income',
      value: income,
      formatted: formatCurrency(income),
      icon: 'i-heroicons-arrow-trending-up',
      color: 'green' as const,
    },
    {
      name: 'Expenses',
      value: expenses,
      formatted: formatCurrency(expenses),
      icon: 'i-heroicons-arrow-trending-down',
      color: 'red' as const,
    },
    {
      name: 'Balance',
      value: income - expenses,
      formatted: formatCurrency(income - expenses),
      icon: 'i-heroicons-wallet',
      color: (income - expenses >= 0 ? 'green' : 'red') as const,
    },
  ]
})
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">
          Transactions
        </h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">
          Manage all your financial transactions
        </p>
      </div>
      <div class="flex gap-2 sm:gap-3">
        <BaseButton
          icon="i-heroicons-arrow-up-tray"
          size="sm"
          variant="secondary"
          @click="openImportModal"
        >
          Import CSV
        </BaseButton>
        <BaseButton
          icon="i-heroicons-plus"
          size="sm"
          variant="primary"
          @click="openAddModal"
        >
          Add Transaction
        </BaseButton>
      </div>
    </header>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="stat in stats"
        :key="stat.name"
        class="bg-card-black border border-border-gray rounded-lg shadow p-6 relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
        :class="{
          'hover:shadow-cyber-blue/10': stat.color === 'blue',
          'hover:shadow-electric-green/10': stat.color === 'green',
          'hover:shadow-danger-red/10': stat.color === 'red',
        }"
      >
        <!-- Top gradient border -->
        <div
          class="absolute top-0 left-0 w-full h-0.5"
          :class="{
            'bg-gradient-to-r from-cyber-blue to-electric-green': stat.color === 'blue',
            'bg-gradient-to-r from-electric-green to-cyber-blue': stat.color === 'green',
            'bg-gradient-to-r from-danger-red to-pink-500': stat.color === 'red',
          }"
        />

        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-medium text-pure-white/60">
              {{ stat.name }}
            </p>
            <p
              class="mt-1 text-2xl font-bold"
              :class="{
                'text-cyber-blue': stat.color === 'blue',
                'text-electric-green': stat.color === 'green',
                'text-danger-red': stat.color === 'red',
              }"
            >
              {{ stat.formatted || stat.value }}
            </p>
          </div>
          <div
            class="p-3 rounded-full border"
            :class="{
              'bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 border-cyber-blue/30': stat.color === 'blue',
              'bg-gradient-to-br from-electric-green/20 to-electric-green/5 border-electric-green/30': stat.color === 'green',
              'bg-gradient-to-br from-danger-red/20 to-danger-red/5 border-danger-red/30': stat.color === 'red',
            }"
          >
            <UIcon
              :name="stat.icon"
              class="w-8 h-8"
              :class="{
                'text-cyber-blue': stat.color === 'blue',
                'text-electric-green': stat.color === 'green',
                'text-danger-red': stat.color === 'red',
              }"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main>
      <!-- Loading state -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 mx-auto text-gray-400 dark:text-gray-500 animate-spin" />
        <p class="mt-2 text-gray-500 dark:text-gray-400">
          Loading transactions...
        </p>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="bg-danger-red/10 border border-danger-red/30 text-danger-red px-6 py-4 rounded-lg backdrop-blur-sm">
        <div class="flex items-center">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 mr-2" />
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="transactions.length === 0" class="bg-card-black border border-border-gray rounded-lg shadow text-center p-8">
        <UIcon name="i-heroicons-banknotes" class="w-12 h-12 mx-auto text-gray-400" />
        <h3 class="mt-4 text-lg font-semibold text-pure-white">
          No transactions yet
        </h3>
        <p class="mt-2 text-sm text-pure-white/60">
          Get started by adding your first transaction.
        </p>
        <BaseButton
          class="mt-6"
          icon="i-heroicons-plus"
          variant="primary"
          @click="openAddModal"
        >
          Add First Transaction
        </BaseButton>
      </div>

      <!-- Transactions list -->
      <TransactionList
        v-else
        :transactions="transactions"
        :loading="loading"
        @edit="handleEditClick"
        @delete="handleDeleteTransaction"
      />
    </main>

    <!-- Add Transaction Modal -->
    <BaseModal
      v-model="isAddModalOpen"
      title="Add New Transaction"
      max-width="2xl"
    >
      <TransactionForm
        :categories="categoriesStore.categoryNames"
        @submit="handleAddTransaction"
        @cancel="handleAddCancel"
      />
    </BaseModal>

    <!-- Edit Transaction Modal -->
    <BaseModal
      v-model="isEditModalOpen"
      title="Edit Transaction"
      max-width="2xl"
    >
      <TransactionForm
        :transaction="editingTransaction"
        :categories="categoriesStore.categoryNames"
        @submit="handleUpdateTransaction"
        @cancel="handleEditCancel"
      />
    </BaseModal>

    <!-- Import CSV Modal -->
    <ImportDialog
      v-model="isImportModalOpen"
      @import-success="handleImportSuccess"
    />
  </div>
</template>
