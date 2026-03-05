<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'import-success': []
}>()

const { t } = useI18n()
const { importBankPDF, loading } = useTransactions()
const toast = useToast()

const activeBank = ref<'velobank' | 'millennium'>('velobank')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

const banks = [
  { key: 'velobank', label: t('finance.import_bank_velobank') },
  { key: 'millennium', label: t('finance.import_bank_millennium') },
] as const

const bankInfo = computed(() => ({
  velobank: t('finance.import_velobank_info'),
  millennium: t('finance.import_millennium_info'),
}[activeBank.value]))

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files?.[0]) selectedFile.value = target.files[0]
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false
  if (event.dataTransfer?.files?.[0]) selectedFile.value = event.dataTransfer.files[0]
}

const handleImport = async () => {
  if (!selectedFile.value) return
  try {
    const result = await importBankPDF(selectedFile.value, activeBank.value)
    toast.add({
      title: t('finance.import_success_title'),
      description: t('finance.import_success_desc', { imported: result.imported, failed: result.failed }),
      color: result.failed === 0 ? 'green' : 'yellow',
    })
    clearSelection()
    emit('import-success')
    emit('update:modelValue', false)
  } catch (error) {
    toast.add({
      title: t('finance.import_error_title'),
      description: error instanceof Error ? error.message : t('common.error'),
      color: 'red',
    })
  }
}

const clearSelection = () => {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const switchBank = (bank: 'velobank' | 'millennium') => {
  activeBank.value = bank
  clearSelection()
}

const close = () => {
  clearSelection()
  emit('update:modelValue', false)
}
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    :title="$t('finance.import_dialog_title')"
    max-width="2xl"
    @update:model-value="close"
  >
    <div class="space-y-5">
      <!-- Bank tabs -->
      <div class="flex border-b border-border-gray">
        <button
          v-for="bank in banks"
          :key="bank.key"
          class="px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px"
          :class="activeBank === bank.key
            ? 'border-electric-green text-electric-green'
            : 'border-transparent text-pure-white/50 hover:text-pure-white'"
          @click="switchBank(bank.key)"
        >
          {{ bank.label }}
        </button>
      </div>

      <!-- Bank info banner -->
      <div class="flex items-start gap-3 bg-electric-green/5 border border-electric-green/20 rounded-lg p-4">
        <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-electric-green mt-0.5 shrink-0" />
        <p class="text-sm text-pure-white/80">{{ bankInfo }}</p>
      </div>

      <!-- Drop zone -->
      <div
        class="border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 cursor-pointer select-none"
        :class="isDragging
          ? 'border-cyber-blue bg-cyber-blue/10 shadow-lg shadow-cyber-blue/20'
          : selectedFile
            ? 'border-electric-green bg-electric-green/5'
            : 'border-border-gray bg-card-black/30 hover:border-electric-green/50'"
        @drop="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @click="!selectedFile && fileInput?.click()"
      >
        <UIcon
          name="i-heroicons-document-text"
          class="w-12 h-12 mx-auto mb-4"
          :class="selectedFile ? 'text-electric-green' : 'text-cyber-blue'"
        />

        <template v-if="!selectedFile">
          <p class="text-base font-medium text-pure-white mb-1">
            {{ $t('finance.import_drop_hint') }}
          </p>
          <p class="text-sm text-pure-white/50 mb-4">
            {{ $t('finance.import_drop_or_browse') }}
          </p>
          <input ref="fileInput" type="file" accept=".pdf" class="hidden" @change="handleFileSelect" />
          <BaseButton icon="i-heroicons-folder-open" variant="primary" @click.stop="fileInput?.click()">
            {{ $t('finance.import_select_file') }}
          </BaseButton>
        </template>

        <template v-else>
          <p class="text-base font-medium text-electric-green mb-1">
            {{ selectedFile.name }}
          </p>
          <p class="text-sm text-pure-white/50 mb-4">
            {{ (selectedFile.size / 1024).toFixed(1) }} KB
          </p>
          <div class="flex justify-center gap-3">
            <BaseButton variant="secondary" @click.stop="clearSelection">
              {{ $t('finance.import_remove') }}
            </BaseButton>
            <BaseButton
              icon="i-heroicons-arrow-up-tray"
              variant="primary"
              :loading="loading"
              @click.stop="handleImport"
            >
              {{ $t('finance.import_do_import') }}
            </BaseButton>
          </div>
        </template>
      </div>

      <!-- What gets detected -->
      <div>
        <p class="text-xs font-semibold text-pure-white/50 uppercase tracking-wider mb-3">
          {{ $t('finance.import_auto_detected') }}
        </p>
        <ul class="space-y-2 text-sm text-pure-white/80">
          <li
            v-for="key in ['import_detected_card', 'import_detected_transfer', 'import_detected_categories', 'import_detected_method']"
            :key="key"
            class="flex items-start gap-2"
          >
            <UIcon name="i-heroicons-check-circle" class="w-4 h-4 text-electric-green mt-0.5 shrink-0" />
            <span>{{ $t(`finance.${key}`) }}</span>
          </li>
        </ul>
      </div>
    </div>
  </BaseModal>
</template>
