<script setup lang="ts">
/**
 * Modal for adding items to inventory
 */
import type { FoodCategory, FoodProduct, FoodInventoryLocation } from '~/types/food'

interface Props {
  modelValue: boolean
  categories: FoodCategory[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  add: [data: {
    product_id: number
    quantity: number
    unit: string
    expiry_date?: string
    location: FoodInventoryLocation
    notes?: string
  }]
}>()

const { searchProducts, createProduct } = useFood()

// Form state
const productSearch = ref('')
const selectedProduct = ref<FoodProduct | null>(null)
const quantity = ref(1)
const unit = ref('szt')
const expiryDate = ref('')
const location = ref<FoodInventoryLocation>('pantry')
const notes = ref('')
const isCreatingProduct = ref(false)
const newProductName = ref('')
const newProductCategory = ref<number | null>(null)

// Search results
const searchResults = ref<FoodProduct[]>([])
const isSearching = ref(false)

// Debounced search
let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(productSearch, (value) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!value || value.length < 2) {
    searchResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    isSearching.value = true
    try {
      searchResults.value = await searchProducts(value)
    } finally {
      isSearching.value = false
    }
  }, 300)
})

// Select product from search
const selectProduct = (product: FoodProduct) => {
  selectedProduct.value = product
  productSearch.value = product.name
  searchResults.value = []
  unit.value = product.default_unit

  // Set default expiry based on category
  if (product.food_category?.default_expiry_days) {
    const days = product.food_category.default_expiry_days
    const date = new Date()
    date.setDate(date.getDate() + days)
    expiryDate.value = date.toISOString().split('T')[0]
  }
}

// Create new product
const handleCreateProduct = async () => {
  if (!newProductName.value) return

  try {
    const product = await createProduct({
      name: newProductName.value,
      food_category_id: newProductCategory.value ?? undefined,
    })
    selectProduct(product)
    isCreatingProduct.value = false
    newProductName.value = ''
    newProductCategory.value = null
  } catch (e) {
    console.error('Failed to create product:', e)
  }
}

// Submit form
const handleSubmit = () => {
  if (!selectedProduct.value) return

  emit('add', {
    product_id: selectedProduct.value.id,
    quantity: quantity.value,
    unit: unit.value,
    expiry_date: expiryDate.value || undefined,
    location: location.value,
    notes: notes.value || undefined,
  })

  // Reset form
  resetForm()
  emit('update:modelValue', false)
}

const resetForm = () => {
  productSearch.value = ''
  selectedProduct.value = null
  quantity.value = 1
  unit.value = 'szt'
  expiryDate.value = ''
  location.value = 'pantry'
  notes.value = ''
  searchResults.value = []
}

const close = () => {
  emit('update:modelValue', false)
}

const locationOptions = [
  { value: 'fridge', label: 'Fridge', icon: 'i-heroicons-cube' },
  { value: 'freezer', label: 'Freezer', icon: 'i-heroicons-cube-transparent' },
  { value: 'pantry', label: 'Pantry', icon: 'i-heroicons-archive-box' },
]

const unitOptions = ['szt', 'kg', 'g', 'l', 'ml']
</script>

<template>
  <BaseModal :model-value="modelValue" title="Add to Inventory" max-width="lg" @update:model-value="emit('update:modelValue', $event)">
    <div class="space-y-4">
      <!-- Product Search -->
      <div v-if="!isCreatingProduct">
        <label class="block text-sm font-medium text-pure-white/80 mb-2">Product</label>
        <div class="relative">
          <div class="relative">
            <UIcon
              name="i-heroicons-magnifying-glass"
              class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-pure-white/40"
            />
            <input
              v-model="productSearch"
              type="text"
              placeholder="Search products..."
              class="w-full pl-10 pr-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none transition-all"
            />
            <UIcon
              v-if="isSearching"
              name="i-heroicons-arrow-path"
              class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-pure-white/40 animate-spin"
            />
          </div>
          <!-- Search Results Dropdown -->
          <div
            v-if="searchResults.length > 0"
            class="absolute z-10 w-full mt-1 bg-card-black border border-border-gray rounded-lg shadow-lg max-h-48 overflow-auto"
          >
            <button
              v-for="product in searchResults"
              :key="product.id"
              class="w-full px-4 py-2 text-left hover:bg-pure-white/5 text-pure-white"
              @click="selectProduct(product)"
            >
              <span class="font-medium">{{ product.name }}</span>
              <span v-if="product.food_category" class="text-pure-white/60 text-sm ml-2">
                {{ product.food_category.name }}
              </span>
            </button>
          </div>
        </div>
        <!-- Selected Product -->
        <div v-if="selectedProduct" class="mt-2 p-3 bg-electric-green/10 border border-electric-green/20 rounded-lg">
          <div class="flex items-center justify-between">
            <span class="text-electric-green font-medium">{{ selectedProduct.name }}</span>
            <button
              class="text-pure-white/60 hover:text-danger-red transition-colors p-1"
              @click="selectedProduct = null; productSearch = ''"
            >
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>
        </div>
        <!-- Create New Product Link -->
        <button
          class="mt-2 text-sm text-cyber-blue hover:underline"
          @click="isCreatingProduct = true; newProductName = productSearch"
        >
          + Create new product
        </button>
      </div>

      <!-- Create New Product Form -->
      <div v-else class="p-4 bg-pure-white/5 rounded-lg space-y-3">
        <h4 class="font-medium text-pure-white">Create New Product</h4>
        <input
          v-model="newProductName"
          type="text"
          placeholder="Product name"
          class="w-full px-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none transition-all"
        />
        <select
          v-model="newProductCategory"
          class="w-full px-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none transition-all"
        >
          <option :value="null">Select category</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
        <div class="flex gap-2">
          <BaseButton
            size="sm"
            variant="primary"
            :disabled="!newProductName"
            @click="handleCreateProduct"
          >
            Create
          </BaseButton>
          <BaseButton
            size="sm"
            variant="ghost"
            @click="isCreatingProduct = false"
          >
            Cancel
          </BaseButton>
        </div>
      </div>

      <!-- Quantity and Unit -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-pure-white/80 mb-2">Quantity</label>
          <input
            v-model.number="quantity"
            type="number"
            min="0.1"
            step="0.1"
            class="w-full px-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none transition-all"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-pure-white/80 mb-2">Unit</label>
          <select
            v-model="unit"
            class="w-full px-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none transition-all"
          >
            <option v-for="u in unitOptions" :key="u" :value="u">
              {{ u }}
            </option>
          </select>
        </div>
      </div>

      <!-- Expiry Date -->
      <div>
        <label class="block text-sm font-medium text-pure-white/80 mb-2">Expiry Date</label>
        <input
          v-model="expiryDate"
          type="date"
          class="w-full px-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none transition-all"
        />
      </div>

      <!-- Location -->
      <div>
        <label class="block text-sm font-medium text-pure-white/80 mb-2">Location</label>
        <div class="flex gap-2">
          <button
            v-for="loc in locationOptions"
            :key="loc.value"
            class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border transition-colors"
            :class="
              location === loc.value
                ? 'bg-electric-green/20 border-electric-green/30 text-electric-green'
                : 'border-border-gray text-pure-white/60 hover:border-pure-white/30'
            "
            @click="location = loc.value as FoodInventoryLocation"
          >
            <UIcon :name="loc.icon" class="w-4 h-4" />
            {{ loc.label }}
          </button>
        </div>
      </div>

      <!-- Notes -->
      <div>
        <label class="block text-sm font-medium text-pure-white/80 mb-2">Notes (optional)</label>
        <textarea
          v-model="notes"
          placeholder="Add notes..."
          rows="2"
          class="w-full px-4 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none transition-all resize-none"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <BaseButton variant="ghost" @click="close">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" :disabled="!selectedProduct" @click="handleSubmit">
          Add to Inventory
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>
