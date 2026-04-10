<script setup lang="ts">
const props = defineProps<{
  recoveryKey: string
}>()

const emit = defineEmits<{
  proceed: []
}>()

const { t } = useI18n()
const copied = ref(false)

const downloadRecoveryKey = () => {
  const content = [
    'LockIner — Recovery Key',
    '=======================',
    '',
    'Keep this file in a safe place. You will need it if you forget your password.',
    'Anyone who has this key can reset your account password.',
    '',
    `Recovery Key: ${props.recoveryKey}`,
    '',
    `Generated: ${new Date().toISOString()}`,
  ].join('\n')

  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'lockins-recovery-key.txt'
  a.click()
  URL.revokeObjectURL(url)
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.recoveryKey)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Clipboard API not available
  }
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow-xl overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-5 border-b border-border-gray relative">
      <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-warning-orange to-danger-red" />
      <div class="flex items-center gap-3">
        <UIcon name="i-heroicons-key" class="w-6 h-6 text-warning-orange flex-shrink-0" />
        <h1 class="text-2xl font-bold text-pure-white">{{ $t('auth.recovery_key_title') }}</h1>
      </div>
    </div>

    <div class="px-6 py-6 space-y-6">
      <!-- Warning -->
      <div class="p-4 bg-warning-orange/10 border border-warning-orange/40 rounded-lg">
        <div class="flex gap-3">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-warning-orange flex-shrink-0 mt-0.5" />
          <div class="text-sm text-warning-orange space-y-1">
            <p class="font-semibold">{{ $t('auth.recovery_key_warning_title') }}</p>
            <p>{{ $t('auth.recovery_key_warning_desc') }}</p>
          </div>
        </div>
      </div>

      <!-- Recovery Key Display -->
      <div>
        <label class="block text-sm font-medium text-pure-white/70 mb-2">
          {{ $t('auth.recovery_key_label') }}
        </label>
        <div class="relative">
          <div
            class="w-full px-4 py-3 pr-12 border border-border-gray rounded-lg bg-background-black font-mono text-sm text-electric-green break-all select-all"
          >
            {{ recoveryKey }}
          </div>
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="copyToClipboard"
          >
            <UIcon
              :name="copied ? 'i-heroicons-check' : 'i-heroicons-clipboard-document'"
              class="w-5 h-5"
              :class="{ 'text-electric-green': copied }"
            />
          </button>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-col gap-3">
        <BaseButton
          type="button"
          variant="secondary"
          class="w-full"
          @click="downloadRecoveryKey"
        >
          <UIcon name="i-heroicons-arrow-down-tray" class="w-4 h-4 mr-2" />
          {{ $t('auth.recovery_key_download') }}
        </BaseButton>

        <BaseButton
          type="button"
          variant="primary"
          class="w-full"
          @click="emit('proceed')"
        >
          {{ $t('auth.recovery_key_proceed') }}
        </BaseButton>
      </div>
    </div>
  </div>
</template>
