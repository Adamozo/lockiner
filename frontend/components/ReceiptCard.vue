<script setup lang="ts">
import type { Receipt } from '~/types/api'
import { formatCurrency, formatDate } from '~/utils/formatters'

const props = defineProps<{
  receipt: Receipt
}>()

const emit = defineEmits<{
  view: [receipt: Receipt]
  delete: [id: number]
  'category-updated': []
}>()

const { getReceiptImageUrl, updateReceiptCategory } = useReceipts()
const categoriesStore = useCategoriesStore()
const toast = useToast()

const imageUrl = computed(() => getReceiptImageUrl(props.receipt.image_path))

// Image viewer state
const isImageViewerOpen = ref(false)

const openImageViewer = (e: Event) => {
  e.stopPropagation()
  isImageViewerOpen.value = true
}

const status = computed(() => {
  if (props.receipt.verified)
    return { text: 'Verified', color: 'success' as const, icon: 'i-heroicons-check-circle' }
  return { text: 'Pending', color: 'warning' as const, icon: 'i-heroicons-clock' }
})

// Category management
const selectedCategory = ref(props.receipt.category || 'Inne')
const updatingCategory = ref(false)

// Update selected category when receipt prop changes
watch(() => props.receipt.category, (newCategory) => {
  selectedCategory.value = newCategory || 'Inne'
}, { immediate: true })

// Handle category change
const handleCategoryChange = async (event: Event) => {
  const target = event.target as HTMLSelectElement
  const newCategory = target.value

  if (newCategory === props.receipt.category) return

  updatingCategory.value = true

  try {
    await updateReceiptCategory(props.receipt.id, newCategory)
    toast.add({
      title: 'Success',
      description: 'Category updated successfully',
      color: 'green',
    })
    emit('category-updated')
  } catch (error) {
    toast.add({
      title: 'Error',
      description: error instanceof Error ? error.message : 'Failed to update category',
      color: 'red',
    })
    // Reset to original value on error
    selectedCategory.value = props.receipt.category || 'Inne'
  } finally {
    updatingCategory.value = false
  }
}

// Get category for display
const categoryInfo = computed(() => {
  const cat = categoriesStore.getCategoryByName(selectedCategory.value)
  return cat || { name: selectedCategory.value, icon: '📦', color: '#C7CEEA' }
})

// Payment method helper
const getPaymentMethodInfo = (method: string | null) => {
  const methods: Record<string, { label: string; icon: string }> = {
    card: { label: 'Card', icon: 'i-heroicons-credit-card' },
    cash: { label: 'Cash', icon: 'i-heroicons-banknotes' },
    blik: { label: 'BLIK', icon: 'i-heroicons-device-phone-mobile' },
    karta: { label: 'Card', icon: 'i-heroicons-credit-card' },
    'gotówka': { label: 'Cash', icon: 'i-heroicons-banknotes' },
    other: { label: 'Other', icon: 'i-heroicons-ellipsis-horizontal-circle' },
  }
  return method && methods[method.toLowerCase()] ? methods[method.toLowerCase()] : null
}
</script>

<template>
  <UCard
    :ui="{
      base: 'bg-card-black border border-border-gray rounded-lg overflow-hidden relative',
      ring: '',
      body: { padding: '' },
      footer: { padding: 'p-2 bg-card-black border-t border-border-gray' },
    }"
    class="transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-electric-green/10"
  >
    <!-- Top gradient border -->
    <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green z-10"></div>

    <div
      class="cursor-pointer"
      @click="emit('view', receipt)"
    >
      <!-- Image -->
      <div class="relative h-40 bg-card-black group/image">
        <img
          :src="imageUrl"
          :alt="`Receipt from ${receipt.merchant || 'Unknown'}`"
          class="w-full h-full object-cover cursor-pointer transition-opacity group-hover/image:opacity-75"
          loading="lazy"
          @click="openImageViewer"
        >
        <!-- Zoom overlay on hover -->
        <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover/image:opacity-100 transition-opacity bg-background-black/50">
          <div class="text-pure-white text-sm font-semibold flex items-center gap-2">
            <UIcon name="i-heroicons-magnifying-glass-plus" class="w-5 h-5" />
            View Full Size
          </div>
        </div>
        <!-- Photo count badge -->
        <div
          v-if="receipt.additional_images?.length"
          class="absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-semibold bg-background-black/80 text-pure-white border border-border-gray flex items-center gap-1"
        >
          <UIcon name="i-heroicons-photo" class="w-3 h-3" />
          {{ receipt.additional_images.length + 1 }}
        </div>
        <!-- Status Badge -->
        <div
          class="absolute top-2 right-2 px-3 py-1.5 rounded-full text-xs font-semibold backdrop-blur-md shadow-xl flex items-center gap-1.5"
          :class="status.color === 'success'
            ? 'bg-electric-green/90 text-background-black shadow-electric-green/50 border border-electric-green'
            : 'bg-warning-orange/90 text-background-black shadow-warning-orange/50 border border-warning-orange'"
        >
          <UIcon :name="status.icon" class="w-3.5 h-3.5" />
          {{ status.text }}
        </div>
      </div>

      <!-- Content -->
      <div class="p-4 space-y-2">
        <!-- Merchant -->
        <h3 class="font-semibold text-pure-white truncate">
          {{ receipt.merchant || 'Unknown Merchant' }}
        </h3>

        <!-- Date & Total -->
        <div class="flex items-center justify-between text-sm">
          <span class="text-pure-white/60">
            {{ formatDate(receipt.scan_date) }}
          </span>
          <span
            v-if="receipt.total"
            class="font-medium text-electric-green"
          >
            {{ formatCurrency(receipt.total) }}
          </span>
          <span v-else class="text-pure-white/40 italic">
            No total
          </span>
        </div>

        <!-- Payment Method -->
        <div v-if="getPaymentMethodInfo(receipt.payment_method)" class="flex items-center gap-1.5 text-xs text-pure-white/60">
          <UIcon :name="getPaymentMethodInfo(receipt.payment_method)!.icon" class="w-3.5 h-3.5" />
          <span>{{ getPaymentMethodInfo(receipt.payment_method)!.label }}</span>
        </div>

        <!-- Category -->
        <div @click.stop>
          <!-- Editable category dropdown for unverified receipts -->
          <select
            v-if="!receipt.verified"
            v-model="selectedCategory"
            :disabled="updatingCategory"
            class="w-full text-xs px-2 py-1.5 rounded-md border transition-all duration-200"
            :class="updatingCategory
              ? 'opacity-50 cursor-not-allowed bg-card-black/50 border-border-gray'
              : 'bg-card-black border-border-gray hover:border-cyber-blue focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none cursor-pointer'"
            :style="{ color: categoryInfo.color }"
            @change="handleCategoryChange"
          >
            <option
              v-for="cat in categoriesStore.categoryNames"
              :key="cat"
              :value="cat"
            >
              {{ cat }}
            </option>
          </select>

          <!-- Read-only category badge for verified receipts -->
          <div
            v-else
            class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium"
            :style="{
              backgroundColor: `${categoryInfo.color}20`,
              borderColor: categoryInfo.color,
              color: categoryInfo.color
            }"
            style="border-width: 1px;"
          >
            <CategoryIcon
              v-if="categoryInfo.icon"
              :icon="categoryInfo.icon"
              :size="14"
              :color="categoryInfo.color"
            />
            <span>{{ categoryInfo.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <template #footer>
      <div class="flex justify-end items-center gap-2">
        <BaseButton
          variant="ghost"
          size="sm"
          icon="i-heroicons-eye"
          @click.stop="emit('view', receipt)"
        />
        <BaseButton
          variant="danger"
          size="sm"
          icon="i-heroicons-trash"
          @click.stop="emit('delete', receipt.id)"
        />
      </div>
    </template>
  </UCard>

  <!-- Image Viewer Dialog -->
  <ImageViewerDialog
    v-model="isImageViewerOpen"
    :image-url="imageUrl"
    :title="`Receipt from ${receipt.merchant || 'Unknown'}`"
  />
</template>
