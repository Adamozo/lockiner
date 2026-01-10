<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'import-success': []
}>()

const { importCSV, loading } = useTransactions()
const toast = useToast()
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

// Handle file selection
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

// Handle file drop
const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

// Handle file import
const handleImport = async () => {
  if (!selectedFile.value) return

  try {
    const result = await importCSV(selectedFile.value)
    toast.add({
      title: 'Success',
      description: `Import successful! Imported: ${result.imported}, Failed: ${result.failed}`,
      color: 'green',
    })
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    emit('import-success')
    emit('update:modelValue', false)
  } catch (error) {
    toast.add({
      title: 'Error',
      description: error instanceof Error ? error.message : 'Failed to import CSV',
      color: 'red',
    })
  }
}

// Clear selection
const clearSelection = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Close modal
const close = () => {
  clearSelection()
  emit('update:modelValue', false)
}
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Import Transactions"
    max-width="3xl"
    @update:model-value="close"
  >
    <div class="space-y-6">
      <!-- Coming soon notice -->
      <div class="bg-warning-orange/10 border border-warning-orange/30 rounded-lg p-4 backdrop-blur-sm">
        <div class="flex items-center">
          <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-warning-orange mr-3 flex-shrink-0" />
          <p class="text-warning-orange text-sm">
            CSV import functionality is in development. File format validation and mapping coming soon.
          </p>
        </div>
      </div>

      <!-- Upload area -->
      <div>
        <h3 class="text-lg font-semibold text-pure-white mb-4">
          Upload CSV File
        </h3>

        <!-- Drop zone -->
        <div
          class="border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300"
          :class="isDragging
            ? 'border-cyber-blue bg-cyber-blue/10 shadow-lg shadow-cyber-blue/20'
            : selectedFile
              ? 'border-electric-green bg-electric-green/5'
              : 'border-border-gray bg-card-black/30 hover:border-electric-green/50'"
          @drop="handleDrop"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
        >
          <UIcon
            name="i-heroicons-arrow-up-tray"
            class="w-12 h-12 mx-auto mb-4"
            :class="selectedFile ? 'text-electric-green' : 'text-cyber-blue'"
          />

          <div v-if="!selectedFile">
            <p class="text-base font-medium text-pure-white mb-2">
              Drop your CSV file here
            </p>
            <p class="text-sm text-pure-white/60 mb-4">
              or click to browse
            </p>
            <input
              ref="fileInput"
              type="file"
              accept=".csv"
              class="hidden"
              @change="handleFileSelect"
            />
            <BaseButton
              icon="i-heroicons-folder-open"
              variant="primary"
              @click="fileInput?.click()"
            >
              Select File
            </BaseButton>
          </div>

          <div v-else>
            <p class="text-base font-medium text-electric-green mb-2">
              {{ selectedFile.name }}
            </p>
            <p class="text-sm text-pure-white/60 mb-4">
              {{ (selectedFile.size / 1024).toFixed(2) }} KB
            </p>
            <div class="flex justify-center gap-3">
              <BaseButton
                variant="secondary"
                @click="clearSelection"
              >
                Clear
              </BaseButton>
              <BaseButton
                icon="i-heroicons-arrow-up-tray"
                variant="primary"
                :loading="loading"
                @click="handleImport"
              >
                Import
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <!-- CSV format guide -->
      <div>
        <h3 class="text-lg font-semibold text-pure-white mb-3">
          CSV Format Guide
        </h3>
        <p class="text-pure-white/60 text-sm mb-3">
          Your CSV file should contain the following columns:
        </p>
        <div class="bg-background-black border border-border-gray rounded-lg p-4 font-mono text-sm">
          <div class="grid grid-cols-5 gap-2 text-xs font-semibold text-cyber-blue mb-2">
            <div>date</div>
            <div>amount</div>
            <div>description</div>
            <div>category</div>
            <div>notes</div>
          </div>
          <div class="grid grid-cols-5 gap-2 text-xs text-pure-white/80">
            <div>2026-01-10</div>
            <div>-45.99</div>
            <div>Grocery shopping</div>
            <div>Jedzenie</div>
            <div>Weekly groceries</div>
          </div>
        </div>
        <ul class="mt-3 space-y-2 text-sm text-pure-white/80">
          <li class="flex items-start">
            <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green mr-2 mt-0.5 flex-shrink-0" />
            <span><strong class="text-pure-white">date:</strong> Format YYYY-MM-DD (required)</span>
          </li>
          <li class="flex items-start">
            <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green mr-2 mt-0.5 flex-shrink-0" />
            <span><strong class="text-pure-white">amount:</strong> Negative for expenses, positive for income (required)</span>
          </li>
          <li class="flex items-start">
            <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green mr-2 mt-0.5 flex-shrink-0" />
            <span><strong class="text-pure-white">description:</strong> Transaction description (optional)</span>
          </li>
          <li class="flex items-start">
            <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green mr-2 mt-0.5 flex-shrink-0" />
            <span><strong class="text-pure-white">category:</strong> Category name, defaults to "Inne" (optional)</span>
          </li>
          <li class="flex items-start">
            <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green mr-2 mt-0.5 flex-shrink-0" />
            <span><strong class="text-pure-white">notes:</strong> Additional notes (optional)</span>
          </li>
        </ul>
      </div>
    </div>
  </BaseModal>
</template>
