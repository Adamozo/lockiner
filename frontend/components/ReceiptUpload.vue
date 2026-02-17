<script setup lang="ts">
import type { OCRResponse, ReceiptItem, ReceiptUpdate, ReceiptUploadResult } from '~/types/api'

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const { uploadReceipt, updateReceipt } = useReceipts()
const { getGeminiKeyStatus, keyConfigured } = useSettings()
const categoriesStore = useCategoriesStore()
const toast = useToast()

// State
const file = ref<File | null>(null)
const filePreview = ref<string | null>(null)
const isUploading = ref(false)
const isProcessing = ref(false)
const uploadedReceiptId = ref<number | null>(null)
const useCustomKey = ref(false)
const customApiKey = ref('')

// OCR form data
const ocrData = ref<OCRResponse>({
  merchant: '',
  date: new Date().toISOString().split('T')[0],
  total: 0,
  payment_method: 'karta',
  items: [],
  tax_amount: 0,
  currency: 'PLN',
})

// Check API key status on mount
onMounted(async () => {
  await getGeminiKeyStatus()
})

// Payment method options
const paymentMethods = [
  { label: 'Karta', value: 'karta' },
  { label: 'Gotówka', value: 'gotówka' },
  { label: 'BLIK', value: 'blik' },
]

// File input refs
const fileInputRef = ref<HTMLInputElement | null>(null)
const cameraInputRef = ref<HTMLInputElement | null>(null)
const openFilePicker = () => fileInputRef.value?.click()

// Camera state
const showCamera = ref(false)
const cameraStream = ref<MediaStream | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)

const openCamera = async () => {
  // Try getUserMedia (works on desktop, may fail on mobile without HTTPS)
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
    })
    cameraStream.value = stream
    showCamera.value = true
    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch {
    // Fallback: use native file input with capture (opens camera app on mobile)
    cameraInputRef.value?.click()
  }
}

const capturePhoto = () => {
  if (!videoRef.value) return
  const video = videoRef.value
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d')!.drawImage(video, 0, 0)
  canvas.toBlob((blob) => {
    if (blob) {
      const capturedFile = new File([blob], `receipt-${Date.now()}.jpg`, { type: 'image/jpeg' })
      handleFileSelect(capturedFile)
    }
    closeCamera()
  }, 'image/jpeg', 0.92)
}

const closeCamera = () => {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach((t) => t.stop())
    cameraStream.value = null
  }
  showCamera.value = false
}

onUnmounted(() => {
  closeCamera()
})

// File drop zone handlers
const isDragging = ref(false)

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false

  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    handleFileSelect(files[0])
  }
}

const handleFileInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFileSelect(target.files[0])
  }
}

const handleFileSelect = (selectedFile: File) => {
  // Validate file type
  if (!selectedFile.type.startsWith('image/')) {
    toast.add({
      title: 'Invalid File',
      description: 'Please upload an image file (JPEG, PNG)',
      color: 'red',
    })
    return
  }

  file.value = selectedFile

  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    filePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(selectedFile)
}

// Upload and OCR handler
const handleUpload = async () => {
  if (!file.value) {
    toast.add({
      title: 'No File',
      description: 'Please select a file to upload',
      color: 'red',
    })
    return
  }

  // Check if we need an API key
  const needsKey = !keyConfigured.value && !useCustomKey.value
  if (needsKey) {
    toast.add({
      title: 'API Key Required',
      description: 'Please configure Gemini API key in Settings or provide a custom key',
      color: 'orange',
    })
    return
  }

  if (useCustomKey.value && !customApiKey.value.trim()) {
    toast.add({
      title: 'API Key Required',
      description: 'Please enter your custom API key',
      color: 'red',
    })
    return
  }

  isUploading.value = true
  isProcessing.value = true

  try {
    // Upload receipt with optional custom API key
    const apiKey = useCustomKey.value ? customApiKey.value : undefined
    const result = await uploadReceipt(file.value, apiKey)
    uploadedReceiptId.value = result.receipt_id

    // Use OCR data if available
    if (result.ocr_data) {
      ocrData.value = result.ocr_data

      // Ensure items array exists
      if (!ocrData.value.items || ocrData.value.items.length === 0) {
        ocrData.value.items = []
        addItem()
      }
    } else {
      // No OCR data, initialize with empty item
      addItem()
    }

    toast.add({
      title: 'Success',
      description: 'Receipt uploaded successfully',
      color: 'green',
    })
  } catch (error) {
    console.error('Upload error:', error)
    toast.add({
      title: 'Upload Failed',
      description: error instanceof Error ? error.message : 'Failed to upload receipt',
      color: 'red',
    })
  } finally {
    isUploading.value = false
    isProcessing.value = false
  }
}

// Item management
const addItem = () => {
  ocrData.value.items.push({
    name: '',
    quantity: 1,
    unit_price: 0,
    total_price: 0,
    category: 'Inne', // Default category
  })
}

const removeItem = (index: number) => {
  ocrData.value.items.splice(index, 1)
}

// Calculate item total
const calculateItemTotal = (item: ReceiptItem) => {
  item.total_price = item.quantity * item.unit_price
}

// Save handler
const handleSave = async () => {
  console.log('[ReceiptUpload] handleSave called, uploadedReceiptId:', uploadedReceiptId.value)

  if (!uploadedReceiptId.value) {
    console.log('[ReceiptUpload] No uploadedReceiptId — bailing out')
    toast.add({
      title: 'Error',
      description: 'No receipt to save',
      color: 'red',
    })
    return
  }

  try {
    const updates: ReceiptUpdate = {
      merchant: ocrData.value.merchant || null,
      total: ocrData.value.total || null,
      items_json: JSON.stringify(ocrData.value.items),
      verified: true,
    }

    console.log('[ReceiptUpload] calling updateReceipt with id:', uploadedReceiptId.value)
    await updateReceipt(uploadedReceiptId.value, updates)
    console.log('[ReceiptUpload] updateReceipt succeeded, emitting success')

    emit('success')
    handleReset()
  } catch (error) {
    console.error('[ReceiptUpload] handleSave error:', error)
    toast.add({
      title: 'Save Failed',
      description: error instanceof Error ? error.message : 'Failed to save receipt',
      color: 'red',
    })
  }
}

// Reset form
const handleReset = () => {
  file.value = null
  filePreview.value = null
  uploadedReceiptId.value = null
  useCustomKey.value = false
  customApiKey.value = ''
  ocrData.value = {
    merchant: '',
    date: new Date().toISOString().split('T')[0],
    total: 0,
    payment_method: 'karta',
    items: [],
    tax_amount: 0,
    currency: 'PLN',
  }
}

// Cancel handler
const handleCancel = () => {
  handleReset()
  emit('cancel')
}
</script>

<template>
  <div class="space-y-6">
    <!-- File Upload Section -->
    <div v-if="!uploadedReceiptId">
      <!-- API Key Warning -->
      <div v-if="!keyConfigured" class="mb-4 p-4 bg-orange-50 dark:bg-orange-900 border border-orange-200 dark:border-orange-700 rounded-lg">
        <div class="flex items-start">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-orange-600 dark:text-orange-400 mr-3 flex-shrink-0 mt-0.5" />
          <div class="flex-1">
            <p class="text-sm font-medium text-orange-800 dark:text-orange-200">
              Gemini API Key Not Configured
            </p>
            <p class="mt-1 text-sm text-orange-700 dark:text-orange-300">
              OCR processing requires a Gemini API key. Configure it in
              <NuxtLink to="/settings" class="font-medium underline">Settings</NuxtLink>
              or provide a custom key below.
            </p>
            <div class="mt-3">
              <label class="flex items-center space-x-2">
                <input
                  v-model="useCustomKey"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="text-sm text-orange-800 dark:text-orange-200">Use custom API key for this upload</span>
              </label>
            </div>
            <div v-if="useCustomKey" class="mt-3">
              <input
                v-model="customApiKey"
                type="password"
                placeholder="Enter Gemini API key"
                class="w-full px-3 py-2 border border-border-gray rounded-lg bg-card-black text-pure-white text-sm focus:ring-2 focus:ring-cyber-blue/30 focus:border-cyber-blue transition-all duration-300"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Drop Zone -->
      <div
        class="border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300"
        :class="
          isDragging
            ? 'border-cyber-blue bg-cyber-blue/10 shadow-lg shadow-cyber-blue/20'
            : 'border-border-gray bg-card-black/30 hover:border-electric-green/50'
        "
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          class="absolute w-px h-px opacity-0 overflow-hidden"
          @change="handleFileInput"
        />
        <input
          ref="cameraInputRef"
          type="file"
          accept="image/*"
          capture="environment"
          class="absolute w-px h-px opacity-0 overflow-hidden"
          @change="handleFileInput"
        />

        <div v-if="!file">
          <UIcon name="i-heroicons-photo" class="w-16 h-16 mx-auto text-cyber-blue mb-4" />
          <p class="text-lg font-medium text-pure-white mb-2">
            Drop receipt image here
          </p>
          <p class="text-sm text-pure-white/60 mb-4">
            or click to browse (JPEG, PNG)
          </p>
          <div class="flex justify-center gap-3">
            <BaseButton variant="primary" size="sm" icon="i-heroicons-document-arrow-up" @click="openFilePicker">
              Select File
            </BaseButton>
            <BaseButton variant="secondary" size="sm" icon="i-heroicons-camera" @click="openCamera">
              Take Photo
            </BaseButton>
          </div>
        </div>

        <div v-else class="space-y-4">
          <img
            :src="filePreview || ''"
            alt="Receipt preview"
            class="max-h-64 mx-auto rounded-lg shadow-lg border border-border-gray"
          />
          <p class="text-sm font-medium text-pure-white">
            {{ file.name }}
          </p>
          <div class="flex justify-center space-x-3">
            <BaseButton variant="secondary" size="sm" @click="openFilePicker">
              Change File
            </BaseButton>
            <BaseButton variant="secondary" size="sm" icon="i-heroicons-camera" @click="openCamera">
              Retake Photo
            </BaseButton>
            <BaseButton
              variant="primary"
              size="sm"
              :loading="isUploading"
              @click="handleUpload"
            >
              Upload & Process
            </BaseButton>
          </div>
        </div>
      </div>
    </div>

    <!-- OCR Results Form -->
    <div v-else class="space-y-6">
      <!-- Processing Indicator -->
      <div v-if="isProcessing" class="p-4 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg">
        <div class="flex items-center">
          <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
          <p class="text-sm text-blue-700 dark:text-blue-300">
            Processing receipt with AI...
          </p>
        </div>
      </div>

      <!-- Preview Image -->
      <div v-if="filePreview" class="flex justify-center">
        <img
          :src="filePreview"
          alt="Receipt"
          class="max-h-48 rounded-lg shadow"
        />
      </div>

      <!-- Basic Info -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="merchant" class="block text-sm font-medium text-pure-white/80 mb-2">
            Merchant
          </label>
          <input
            id="merchant"
            v-model="ocrData.merchant"
            type="text"
            placeholder="e.g., Biedronka"
            class="w-full px-3 py-2 border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 transition-all duration-300 rounded-lg"
          />
        </div>

        <div>
          <label for="date" class="block text-sm font-medium text-pure-white/80 mb-2">
            Date
          </label>
          <input
            id="date"
            v-model="ocrData.date"
            type="date"
            class="w-full px-3 py-2 border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 transition-all duration-300 rounded-lg"
          />
        </div>

        <div>
          <label for="total" class="block text-sm font-medium text-pure-white/80 mb-2">
            Total (PLN)
          </label>
          <input
            id="total"
            v-model.number="ocrData.total"
            type="number"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 transition-all duration-300 rounded-lg"
          />
        </div>

        <div>
          <label for="payment-method" class="block text-sm font-medium text-pure-white/80 mb-2">
            Payment Method
          </label>
          <select
            id="payment-method"
            v-model="ocrData.payment_method"
            class="w-full px-3 py-2 border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 transition-all duration-300 rounded-lg"
          >
            <option v-for="method in paymentMethods" :key="method.value" :value="method.value">
              {{ method.label }}
            </option>
          </select>
        </div>

        <div>
          <label for="tax" class="block text-sm font-medium text-pure-white/80 mb-2">
            Tax Amount (PLN)
          </label>
          <input
            id="tax"
            v-model.number="ocrData.tax_amount"
            type="number"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 transition-all duration-300 rounded-lg"
          />
        </div>
      </div>

      <!-- Items Table -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <label class="block text-sm font-medium text-pure-white/80">
            Items
          </label>
          <BaseButton
            icon="i-heroicons-plus"
            size="sm"
            variant="secondary"
            @click="addItem"
          >
            Add Item
          </BaseButton>
        </div>

        <div class="border border-border-gray rounded-lg overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-border-gray">
              <thead class="bg-card-black/50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                    Name
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                    Unit Price
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                    Total
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                    Category
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-card-black divide-y divide-border-gray">
                <tr v-for="(item, index) in ocrData.items" :key="index">
                  <td class="px-4 py-3">
                    <input
                      v-model="item.name"
                      type="text"
                      placeholder="Item name"
                      class="w-full px-2 py-1 border border-border-gray rounded bg-background-black text-pure-white text-sm focus:ring-2 focus:ring-cyber-blue/30 focus:border-cyber-blue transition-all duration-300"
                    />
                  </td>
                  <td class="px-4 py-3">
                    <input
                      v-model.number="item.quantity"
                      type="number"
                      min="1"
                      class="w-20 px-2 py-1 border border-border-gray rounded bg-background-black text-pure-white text-sm focus:ring-2 focus:ring-cyber-blue/30 focus:border-cyber-blue transition-all duration-300"
                      @input="calculateItemTotal(item)"
                    />
                  </td>
                  <td class="px-4 py-3">
                    <input
                      v-model.number="item.unit_price"
                      type="number"
                      step="0.01"
                      min="0"
                      class="w-24 px-2 py-1 border border-border-gray rounded bg-background-black text-pure-white text-sm focus:ring-2 focus:ring-cyber-blue/30 focus:border-cyber-blue transition-all duration-300"
                      @input="calculateItemTotal(item)"
                    />
                  </td>
                  <td class="px-4 py-3">
                    <span class="text-sm font-medium text-electric-green">
                      {{ item.total_price.toFixed(2) }} PLN
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <select
                      v-model="item.category"
                      class="w-full px-2 py-1 text-xs bg-card-black border border-border-gray rounded-md text-pure-white focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue focus:outline-none"
                    >
                      <option
                        v-for="cat in categoriesStore.categoryNames"
                        :key="cat"
                        :value="cat"
                      >
                        {{ cat }}
                      </option>
                    </select>
                  </td>
                  <td class="px-4 py-3">
                    <button
                      class="p-1 rounded text-pure-white/70 hover:text-danger-red hover:bg-white/5 transition-all"
                      @click="removeItem(index)"
                    >
                      <UIcon name="i-heroicons-trash" class="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-border-gray">
        <BaseButton
          variant="secondary"
          size="sm"
          @click="handleCancel"
        >
          Cancel
        </BaseButton>
        <BaseButton
          variant="primary"
          size="sm"
          @click="handleSave"
        >
          Save Receipt
        </BaseButton>
      </div>
    </div>

    <!-- Camera Overlay -->
    <Teleport to="body">
      <div
        v-if="showCamera"
        class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/95"
      >
        <div class="relative w-full max-w-2xl px-4">
          <video
            ref="videoRef"
            autoplay
            playsinline
            class="w-full rounded-lg"
          />
          <div class="flex justify-center gap-4 mt-6">
            <BaseButton variant="secondary" size="sm" @click="closeCamera">
              Anuluj
            </BaseButton>
            <BaseButton variant="primary" size="sm" icon="i-heroicons-camera" @click="capturePhoto">
              Zrób zdjęcie
            </BaseButton>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
