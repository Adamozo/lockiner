<script setup lang="ts">
import type { Receipt } from '~/types/api'

definePageMeta({
  layout: 'finance',
})

useSeoMeta({
  title: 'Receipts - LockIner',
  description: 'Manage your receipt scans with OCR',
})

const { currentHouseholdId, householdIdForApi, isPersonalContext } = useHouseholdContext()
const { receipts, loading, error: receiptsError, fetchReceipts, deleteReceipt } = useReceipts()
const categoriesStore = useCategoriesStore()
const toast = useToast()

// Modal state
const isUploadModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const selectedReceipt = ref<Receipt | null>(null)

// Filter state
const selectedMonth = ref('')

// Data for stats cards
const stats = computed(() => [
  {
    name: 'Total Receipts',
    value: receipts.value.length,
    icon: 'i-heroicons-document-text',
    color: 'blue' as const,
  },
  {
    name: 'Verified',
    value: receipts.value.filter(r => r.verified).length,
    icon: 'i-heroicons-check-circle',
    color: 'green' as const,
  },
  {
    name: 'Pending Review',
    value: receipts.value.filter(r => !r.verified).length,
    icon: 'i-heroicons-clock',
    color: 'yellow' as const,
  },
])

// Load data function
const loadData = async () => {
  try {
    // Fetch categories and receipts in parallel
    await Promise.all([
      categoriesStore.fetchCategories(),
      fetchReceipts(householdIdForApi.value),
    ])
  }
  catch (error) {
    console.error('Failed to fetch data:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to load receipts. Please check if the backend is running.',
      color: 'red',
    })
  }
}

// Fetch receipts on mount
onMounted(loadData)

// Reload data when context changes
watch(() => currentHouseholdId.value, loadData)

// Filtered receipts
const filteredReceipts = computed(() => {
  if (!selectedMonth.value)
    return receipts.value

  return receipts.value.filter((receipt) => {
    const receiptDate = new Date(receipt.scan_date)
    const receiptMonth = `${receiptDate.getFullYear()}-${String(receiptDate.getMonth() + 1).padStart(2, '0')}`
    return receiptMonth === selectedMonth.value
  })
})

// Month options for filter
const monthOptions = computed(() => {
  const months = new Set<string>()
  receipts.value.forEach((receipt) => {
    const date = new Date(receipt.scan_date)
    const month = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    months.add(month)
  })
  return Array.from(months).sort().reverse().map(month => ({
    label: new Date(`${month}-02`).toLocaleDateString('en-US', { year: 'numeric', month: 'long' }),
    value: month,
  }))
})

// Handlers
async function handleUploadSuccess() {
  console.log('[receipts] handleUploadSuccess called')
  isUploadModalOpen.value = false
  await loadData()
  console.log('[receipts] loadData done, adding toast now')
  toast.add({
    title: 'Success',
    description: 'Receipt uploaded and saved',
    color: 'green',
  })
  console.log('[receipts] toast.add called')
}

function handleUploadCancel() {
  isUploadModalOpen.value = false
}

function handleViewReceipt(receipt: Receipt) {
  selectedReceipt.value = receipt
  isDetailModalOpen.value = true
}

async function handleDeleteReceipt(id: number) {
  if (!confirm('Are you sure you want to delete this receipt?'))
    return

  try {
    await deleteReceipt(id, householdIdForApi.value)
    await loadData()
    toast.add({
      title: 'Success',
      description: 'Receipt deleted successfully',
      color: 'green',
    })
  }
  catch (error) {
    toast.add({
      title: 'Error',
      description: error instanceof Error ? error.message : 'Failed to delete receipt',
      color: 'red',
    })
  }
}

function openUploadModal() {
  isUploadModalOpen.value = true
}

async function handleReceiptVerified() {
  await loadData()
  isDetailModalOpen.value = false
  toast.add({
    title: 'Success',
    description: 'Receipt verified',
    color: 'green',
  })
}
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">
          Receipts
        </h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">
          Upload and manage receipt scans with AI-powered OCR.
        </p>
      </div>
      <BaseButton
        icon="i-heroicons-camera"
        size="sm"
        variant="primary"
        @click="openUploadModal"
      >
        Upload Receipt
      </BaseButton>
    </header>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="stat in stats"
        :key="stat.name"
        class="bg-card-black border border-border-gray rounded-lg shadow p-6 relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
        :class="{
          'hover:shadow-cyber-blue/10': stat.color === 'blue',
          'hover:shadow-electric-green/10': stat.color === 'green',
          'hover:shadow-warning-orange/10': stat.color === 'yellow',
        }"
      >
        <!-- Top gradient border -->
        <div
          class="absolute top-0 left-0 w-full h-0.5"
          :class="{
            'bg-gradient-to-r from-cyber-blue to-electric-green': stat.color === 'blue',
            'bg-gradient-to-r from-electric-green to-cyber-blue': stat.color === 'green',
            'bg-gradient-to-r from-warning-orange to-electric-green': stat.color === 'yellow',
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
                'text-warning-orange': stat.color === 'yellow',
              }"
            >
              {{ stat.value }}
            </p>
          </div>
          <div
            class="p-3 rounded-full border"
            :class="{
              'bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 border-cyber-blue/30': stat.color === 'blue',
              'bg-gradient-to-br from-electric-green/20 to-electric-green/5 border-electric-green/30': stat.color === 'green',
              'bg-gradient-to-br from-warning-orange/20 to-warning-orange/5 border-warning-orange/30': stat.color === 'yellow',
            }"
          >
            <UIcon
              :name="stat.icon"
              class="w-8 h-8"
              :class="{
                'text-cyber-blue': stat.color === 'blue',
                'text-electric-green': stat.color === 'green',
                'text-warning-orange': stat.color === 'yellow',
              }"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Filter -->
    <div v-if="monthOptions.length > 0" class="bg-card-black border border-border-gray rounded-lg shadow px-4 py-3">
      <div class="flex items-center space-x-3">
        <label for="month-filter" class="text-sm font-medium text-pure-white">
          Filter by month:
        </label>
        <select
          id="month-filter"
          v-model="selectedMonth"
          class="px-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
        >
          <option value="">All Months</option>
          <option
            v-for="option in monthOptions"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Main Content -->
    <main>
      <!-- Loading state -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 mx-auto text-gray-400 dark:text-gray-500 animate-spin" />
        <p class="mt-2 text-gray-500 dark:text-gray-400">
          Loading receipts...
        </p>
      </div>

      <!-- Error state -->
      <UCard v-else-if="receiptsError" class="text-center">
        <div class="p-8">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 mx-auto text-red-400" />
          <h3 class="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
            Failed to load receipts
          </h3>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {{ receiptsError }}
          </p>
          <BaseButton
            class="mt-6"
            icon="i-heroicons-arrow-path"
            variant="primary"
            @click="fetchReceipts()"
          >
            Retry
          </BaseButton>
        </div>
      </UCard>

      <!-- Empty state -->
      <UCard v-else-if="receipts.length === 0" class="text-center">
        <div class="p-8">
          <UIcon name="i-heroicons-photo" class="w-12 h-12 mx-auto text-gray-400" />
          <h3 class="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
            No receipts yet
          </h3>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Get started by uploading your first receipt.
          </p>
          <BaseButton
            class="mt-6"
            icon="i-heroicons-camera"
            variant="primary"
            @click="openUploadModal"
          >
            Upload First Receipt
          </BaseButton>
        </div>
      </UCard>

      <!-- Receipt grid -->
      <div v-else-if="filteredReceipts.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <ReceiptCard
          v-for="receipt in filteredReceipts"
          :key="receipt.id"
          :receipt="receipt"
          @view="handleViewReceipt"
          @delete="handleDeleteReceipt"
        />
      </div>

      <!-- No results for filter -->
      <UCard v-else class="text-center">
        <div class="p-8">
          <UIcon name="i-heroicons-funnel" class="w-12 h-12 mx-auto text-gray-400" />
          <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">
            No receipts found for the selected month.
          </p>
        </div>
      </UCard>
    </main>

    <!-- Upload Modal -->
    <BaseModal
      v-model="isUploadModalOpen"
      title="Upload Receipt"
      max-width="4xl"
    >
      <ReceiptUpload
        @success="handleUploadSuccess"
        @cancel="handleUploadCancel"
      />
    </BaseModal>

    <!-- Detail Modal -->
    <BaseModal
      v-model="isDetailModalOpen"
      title="Receipt Details"
      max-width="3xl"
    >
      <ReceiptDetail
        v-if="selectedReceipt"
        :receipt="selectedReceipt"
        @verified="handleReceiptVerified"
      />
    </BaseModal>
  </div>
</template>
