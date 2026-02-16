<script setup lang="ts">
const props = defineProps<{
  codes: string[]
}>()

const toast = useToast()

const copyAll = async () => {
  try {
    await navigator.clipboard.writeText(props.codes.join('\n'))
    toast.add({
      title: 'Copied',
      description: 'Recovery codes copied to clipboard',
      color: 'green',
    })
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to copy codes',
      color: 'red',
    })
  }
}

const downloadCodes = () => {
  const content = `LockIner Recovery Codes\n${'='.repeat(30)}\n\nSave these codes in a safe place.\nEach code can only be used once.\n\n${props.codes.join('\n')}\n`
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'lockiner-recovery-codes.txt'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="space-y-4">
    <!-- Warning -->
    <div class="p-4 bg-warning-orange/10 border border-warning-orange/30 rounded-lg">
      <div class="flex items-start gap-2 text-warning-orange">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div class="text-sm">
          <p class="font-medium">Save these recovery codes</p>
          <p class="mt-1 text-warning-orange/80">
            Store them securely. Each code can only be used once. If you lose access to your authenticator app, you'll need these codes to log in.
          </p>
        </div>
      </div>
    </div>

    <!-- Codes grid -->
    <div class="grid grid-cols-2 gap-2">
      <div
        v-for="code in codes"
        :key="code"
        class="px-3 py-2 bg-background-black border border-border-gray rounded font-mono text-sm text-pure-white text-center"
      >
        {{ code }}
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-3">
      <BaseButton
        variant="secondary"
        icon="i-heroicons-clipboard-document"
        size="sm"
        @click="copyAll"
      >
        Copy all
      </BaseButton>
      <BaseButton
        variant="ghost"
        icon="i-heroicons-arrow-down-tray"
        size="sm"
        @click="downloadCodes"
      >
        Download
      </BaseButton>
    </div>
  </div>
</template>
