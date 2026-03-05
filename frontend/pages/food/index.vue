<script setup lang="ts">
import type { FoodInventoryItem, FoodInventoryLocation } from '~/types/food'

definePageMeta({
  layout: 'food',
})

const { currentHouseholdId } = useHouseholdContext()
const { fetchCategories, categories } = useFood()
const {
  inventory,
  expiringSoon,
  loading,
  fetchInventory,
  fetchExpiringSoon,
  addToInventory,
  deleteInventoryItem,
  consumeItem,
  openItem,
  getDaysUntilExpiry,
} = useFoodInventory()

const toast = useToast()

// Filters
const locationFilter = ref<FoodInventoryLocation | null>(null)
const statusFilter = ref<'all' | 'expiring' | 'expired'>('all')

// Modals
const showAddModal = ref(false)
const showConsumeModal = ref(false)
const selectedItem = ref<FoodInventoryItem | null>(null)

// Page title
const pageTitle = computed(() => {
  return currentHouseholdId.value ? 'Shared Pantry' : 'My Inventory'
})

// Fetch data on mount
onMounted(async () => {
  await Promise.all([
    fetchCategories(),
    loadInventory(),
    fetchExpiringSoon(currentHouseholdId.value, 3),
  ])
})

// Reload when household changes
watch(currentHouseholdId, async () => {
  await loadInventory()
  await fetchExpiringSoon(currentHouseholdId.value, 3)
})

// Load inventory with current filters
const loadInventory = async () => {
  await fetchInventory(currentHouseholdId.value, {
    location: locationFilter.value ?? undefined,
    status: statusFilter.value === 'all' ? undefined : 'available',
  })
}

// Watch filter changes
watch([locationFilter], loadInventory)

// Filtered inventory based on status filter
const filteredInventory = computed(() => {
  if (statusFilter.value === 'all') {
    return inventory.value.filter(i => i.status === 'available' || i.status === 'opened')
  }
  if (statusFilter.value === 'expiring') {
    return inventory.value.filter(i => {
      const days = getDaysUntilExpiry(i)
      return days !== null && days >= 0 && days <= 3 && (i.status === 'available' || i.status === 'opened')
    })
  }
  if (statusFilter.value === 'expired') {
    return inventory.value.filter(i => {
      const days = getDaysUntilExpiry(i)
      return days !== null && days < 0
    })
  }
  return inventory.value
})

// Stats
const stats = computed(() => {
  const all = inventory.value.filter(i => i.status === 'available' || i.status === 'opened')
  const expiring = all.filter(i => {
    const days = getDaysUntilExpiry(i)
    return days !== null && days >= 0 && days <= 3
  })
  const expired = inventory.value.filter(i => {
    const days = getDaysUntilExpiry(i)
    return days !== null && days < 0
  })
  return {
    total: all.length,
    expiring: expiring.length,
    expired: expired.length,
  }
})

// Handle add to inventory
const handleAdd = async (data: any) => {
  try {
    await addToInventory(data, currentHouseholdId.value)
    toast.add({ title: 'Added to inventory', color: 'green' })
    await loadInventory()
  } catch (e) {
    toast.add({ title: 'Failed to add item', color: 'red' })
  }
}

// Handle consume
const handleConsume = (item: FoodInventoryItem) => {
  selectedItem.value = item
  showConsumeModal.value = true
}

const confirmConsume = async (quantity?: number) => {
  if (!selectedItem.value) return
  try {
    await consumeItem(selectedItem.value.id, { quantity }, currentHouseholdId.value)
    toast.add({ title: 'Item consumed', color: 'green' })
    showConsumeModal.value = false
    selectedItem.value = null
    await loadInventory()
  } catch (e) {
    toast.add({ title: 'Failed to consume item', color: 'red' })
  }
}

// Handle open
const handleOpen = async (item: FoodInventoryItem) => {
  try {
    await openItem(item.id, currentHouseholdId.value)
    toast.add({ title: 'Marked as opened', color: 'green' })
  } catch (e) {
    toast.add({ title: 'Failed to update item', color: 'red' })
  }
}

const { confirm } = useConfirm()

// Handle delete
const handleDelete = async (item: FoodInventoryItem) => {
  if (!await confirm({ message: `Remove "${item.product.name}" from inventory?`, confirmText: 'Remove' })) return
  try {
    await deleteInventoryItem(item.id, currentHouseholdId.value)
    toast.add({ title: 'Removed from inventory', color: 'green' })
  } catch (e) {
    toast.add({ title: 'Failed to remove item', color: 'red' })
  }
}

// Handle edit (placeholder)
const handleEdit = (item: FoodInventoryItem) => {
  toast.add({ title: 'Edit coming soon', color: 'yellow' })
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-pure-white">{{ pageTitle }}</h1>
        <p class="text-pure-white/60 text-sm sm:text-base mt-1">Manage your food inventory and track expiration dates</p>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        variant="primary"
        size="sm"
        class="self-start sm:self-auto"
        @click="showAddModal = true"
      >
        Add Item
      </BaseButton>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <button
        class="bg-card-black border rounded-xl p-6 text-left transition-colors"
        :class="statusFilter === 'all' ? 'border-electric-green' : 'border-border-gray hover:border-electric-green/50'"
        @click="statusFilter = 'all'"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-electric-green/10 flex items-center justify-center">
            <UIcon name="i-heroicons-archive-box" class="w-5 h-5 text-electric-green" />
          </div>
          <div>
            <p class="text-pure-white/60 text-sm">All Products</p>
            <p class="text-2xl font-bold text-pure-white">{{ stats.total }}</p>
          </div>
        </div>
      </button>

      <button
        class="bg-card-black border rounded-xl p-6 text-left transition-colors"
        :class="statusFilter === 'expiring' ? 'border-warning-orange' : 'border-border-gray hover:border-warning-orange/50'"
        @click="statusFilter = 'expiring'"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-warning-orange/10 flex items-center justify-center">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-warning-orange" />
          </div>
          <div>
            <p class="text-pure-white/60 text-sm">Expiring Soon (3 days)</p>
            <p class="text-2xl font-bold text-pure-white">{{ stats.expiring }}</p>
          </div>
        </div>
      </button>

      <button
        class="bg-card-black border rounded-xl p-6 text-left transition-colors"
        :class="statusFilter === 'expired' ? 'border-danger-red' : 'border-border-gray hover:border-danger-red/50'"
        @click="statusFilter = 'expired'"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-danger-red/10 flex items-center justify-center">
            <UIcon name="i-heroicons-x-circle" class="w-5 h-5 text-danger-red" />
          </div>
          <div>
            <p class="text-pure-white/60 text-sm">Expired</p>
            <p class="text-2xl font-bold text-pure-white">{{ stats.expired }}</p>
          </div>
        </div>
      </button>
    </div>

    <!-- Location Filter -->
    <FoodLocationFilter v-model="locationFilter" />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-pure-white/40 animate-spin" />
    </div>

    <!-- Inventory List -->
    <div v-else-if="filteredInventory.length > 0" class="space-y-3">
      <FoodInventoryCard
        v-for="item in filteredInventory"
        :key="item.id"
        :item="item"
        @consume="handleConsume"
        @open="handleOpen"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="bg-card-black border border-border-gray rounded-xl p-12 text-center">
      <div class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-shopping-cart" class="w-8 h-8 text-pure-white/40" />
      </div>
      <h3 class="text-lg font-medium text-pure-white mb-2">
        {{ statusFilter === 'all' ? 'No Products' : statusFilter === 'expiring' ? 'No Expiring Items' : 'No Expired Items' }}
      </h3>
      <p class="text-pure-white/60 max-w-md mx-auto mb-4">
        {{ statusFilter === 'all'
          ? 'Add products to your inventory to track expiration dates.'
          : statusFilter === 'expiring'
          ? 'Great! No products are expiring soon.'
          : 'Great! No expired products in your inventory.'
        }}
      </p>
      <BaseButton
        v-if="statusFilter === 'all'"
        icon="i-heroicons-plus"
        variant="primary"
        @click="showAddModal = true"
      >
        Add Your First Item
      </BaseButton>
    </div>

    <!-- Add Modal -->
    <FoodAddToInventoryModal
      v-model="showAddModal"
      :categories="categories"
      @add="handleAdd"
    />

    <!-- Consume Modal -->
    <BaseModal v-model="showConsumeModal" title="Consume Item" max-width="md">
      <div v-if="selectedItem" class="space-y-4">
        <p class="text-pure-white">
          How much of <strong>{{ selectedItem.product.name }}</strong> did you consume?
        </p>
        <p class="text-pure-white/60 text-sm">
          Current quantity: {{ selectedItem.quantity }} {{ selectedItem.unit }}
        </p>
        <div class="flex gap-3">
          <BaseButton variant="primary" @click="confirmConsume()">
            Consume All
          </BaseButton>
          <BaseButton variant="ghost" @click="showConsumeModal = false">
            Cancel
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>
