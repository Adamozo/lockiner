<script setup lang="ts">
import type { FoodPendingImport } from '~/types/food'

definePageMeta({
  layout: 'food',
})

const { currentHouseholdId } = useHouseholdContext()
const { fetchCategories, categories } = useFood()
const {
  pendingImports,
  currentImport,
  loading,
  fetchPendingImports,
  getPendingImport,
  acceptItem,
  rejectItem,
  acceptAllMatched,
  matchedItemsCount,
  pendingItemsCount,
} = useFoodImport()

const toast = useToast()

// Selected import to view
const selectedImportId = ref<number | null>(null)

// Fetch data on mount
onMounted(async () => {
  await Promise.all([
    fetchCategories(),
    fetchPendingImports(currentHouseholdId.value),
  ])
})

// Reload when household changes
watch(currentHouseholdId, async () => {
  await fetchPendingImports(currentHouseholdId.value)
  selectedImportId.value = null
  currentImport.value = null
})

// Load specific import when selected
watch(selectedImportId, async (id) => {
  if (id) {
    await getPendingImport(id, currentHouseholdId.value)
  }
})

// Handle accept item
const handleAccept = async (data: { itemId: number; productId?: number; expiryDate?: string; quantity?: number }) => {
  if (!selectedImportId.value) return
  try {
    await acceptItem(
      selectedImportId.value,
      data.itemId,
      {
        final_product_id: data.productId,
        final_expiry_date: data.expiryDate,
        final_quantity: data.quantity,
      },
      currentHouseholdId.value
    )
    toast.add({ title: 'Item added to inventory', color: 'green' })
  } catch (e) {
    toast.add({ title: 'Failed to accept item', color: 'red' })
  }
}

// Handle reject item
const handleReject = async (itemId: number) => {
  if (!selectedImportId.value) return
  try {
    await rejectItem(selectedImportId.value, itemId, currentHouseholdId.value)
    toast.add({ title: 'Item skipped', color: 'gray' })
  } catch (e) {
    toast.add({ title: 'Failed to skip item', color: 'red' })
  }
}

// Handle accept all matched
const handleAcceptAllMatched = async () => {
  if (!selectedImportId.value) return
  try {
    const results = await acceptAllMatched(selectedImportId.value, currentHouseholdId.value)
    toast.add({ title: `${results.length} items added to inventory`, color: 'green' })
  } catch (e) {
    toast.add({ title: 'Failed to accept items', color: 'red' })
  }
}

// Handle create product (placeholder)
const handleCreateProduct = (data: { itemId: number; name: string }) => {
  toast.add({ title: 'Create product modal coming soon', color: 'yellow' })
}

// Go back to list
const goBack = () => {
  selectedImportId.value = null
  currentImport.value = null
}

// Get status badge
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'pending':
      return { label: 'Pending', class: 'bg-warning-orange/10 text-warning-orange' }
    case 'partially_accepted':
      return { label: 'Partial', class: 'bg-cyber-blue/10 text-cyber-blue' }
    case 'accepted':
      return { label: 'Completed', class: 'bg-electric-green/10 text-electric-green' }
    case 'rejected':
      return { label: 'Rejected', class: 'bg-danger-red/10 text-danger-red' }
    default:
      return { label: status, class: 'bg-pure-white/10 text-pure-white/60' }
  }
}

// Format date
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <BaseButton
          v-if="selectedImportId"
          icon="i-heroicons-arrow-left"
          variant="ghost"
          @click="goBack"
        />
        <div>
          <h1 class="text-2xl font-bold text-pure-white">
            {{ selectedImportId ? 'Import Details' : 'Pending Imports' }}
          </h1>
          <p class="text-pure-white/60 mt-1">
            {{ selectedImportId ? 'Review and accept items from receipt' : 'Review products from scanned receipts' }}
          </p>
        </div>
      </div>
      <BaseButton
        v-if="selectedImportId && matchedItemsCount > 0"
        icon="i-heroicons-check-circle"
        variant="primary"
        @click="handleAcceptAllMatched"
      >
        Accept All Matched ({{ matchedItemsCount }})
      </BaseButton>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-pure-white/40 animate-spin" />
    </div>

    <!-- Import Detail View -->
    <template v-else-if="selectedImportId && currentImport">
      <!-- Import Info -->
      <div class="bg-card-black border border-border-gray rounded-xl p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-lg bg-cyber-blue/10 flex items-center justify-center">
              <UIcon name="i-heroicons-receipt-percent" class="w-5 h-5 text-cyber-blue" />
            </div>
            <div>
              <p class="text-pure-white font-medium">Receipt #{{ currentImport.receipt_id }}</p>
              <p class="text-pure-white/60 text-sm">{{ formatDate(currentImport.created_at) }}</p>
            </div>
          </div>
          <span
            class="px-3 py-1 rounded-full text-sm font-medium"
            :class="getStatusBadge(currentImport.status).class"
          >
            {{ getStatusBadge(currentImport.status).label }}
          </span>
        </div>
      </div>

      <!-- Progress -->
      <div class="bg-card-black border border-border-gray rounded-xl p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-pure-white/60 text-sm">Progress</span>
          <span class="text-pure-white text-sm font-medium">
            {{ currentImport.items.filter(i => i.status !== 'pending').length }} / {{ currentImport.items.length }} items
          </span>
        </div>
        <div class="w-full bg-pure-white/10 rounded-full h-2">
          <div
            class="bg-electric-green h-2 rounded-full transition-all"
            :style="{ width: `${(currentImport.items.filter(i => i.status !== 'pending').length / currentImport.items.length) * 100}%` }"
          />
        </div>
      </div>

      <!-- Items List -->
      <div class="space-y-3">
        <FoodImportItemRow
          v-for="item in currentImport.items"
          :key="item.id"
          :item="item"
          :categories="categories"
          @accept="handleAccept"
          @reject="handleReject"
          @create-product="handleCreateProduct"
        />
      </div>
    </template>

    <!-- Imports List View -->
    <template v-else>
      <!-- Pending imports list -->
      <div v-if="pendingImports.length > 0" class="space-y-3">
        <button
          v-for="imp in pendingImports"
          :key="imp.id"
          class="w-full bg-card-black border border-border-gray rounded-xl p-4 hover:border-electric-green/30 transition-colors text-left"
          @click="selectedImportId = imp.id"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-lg bg-cyber-blue/10 flex items-center justify-center">
                <UIcon name="i-heroicons-receipt-percent" class="w-5 h-5 text-cyber-blue" />
              </div>
              <div>
                <p class="text-pure-white font-medium">Receipt #{{ imp.receipt_id }}</p>
                <p class="text-pure-white/60 text-sm">{{ formatDate(imp.created_at) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <span
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="getStatusBadge(imp.status).class"
              >
                {{ getStatusBadge(imp.status).label }}
              </span>
              <span class="text-pure-white/60 text-sm">
                {{ imp.items.length }} items
              </span>
              <UIcon name="i-heroicons-chevron-right" class="w-5 h-5 text-pure-white/40" />
            </div>
          </div>
        </button>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-card-black border border-border-gray rounded-xl p-12 text-center">
        <div class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-inbox" class="w-8 h-8 text-pure-white/40" />
        </div>
        <h3 class="text-lg font-medium text-pure-white mb-2">No Pending Imports</h3>
        <p class="text-pure-white/60 max-w-md mx-auto">
          When you scan and verify receipts in the Finance module, food items will appear here for review.
        </p>
        <NuxtLink to="/finance/receipts" class="mt-4 inline-block">
          <BaseButton variant="secondary">
            Go to Receipts
          </BaseButton>
        </NuxtLink>
      </div>
    </template>
  </div>
</template>
