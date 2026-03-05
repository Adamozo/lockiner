<script setup lang="ts">
const { state, handleConfirm, handleCancel } = useConfirm()

const iconMap = {
  danger: 'i-heroicons-exclamation-triangle',
  warning: 'i-heroicons-exclamation-circle',
  primary: 'i-heroicons-question-mark-circle',
}

const iconColorMap = {
  danger: 'text-danger-red',
  warning: 'text-warning-orange',
  primary: 'text-cyber-blue',
}
</script>

<template>
  <BaseModal
    :model-value="state.open"
    :title="state.title || undefined"
    max-width="sm"
    @update:model-value="handleCancel"
  >
    <div class="space-y-5">
      <div class="flex items-start gap-4">
        <div :class="['flex-shrink-0 mt-0.5', iconColorMap[state.variant]]">
          <UIcon :name="iconMap[state.variant]" class="w-6 h-6" />
        </div>
        <p class="text-pure-white/80 leading-relaxed">
          {{ state.message }}
        </p>
      </div>

      <div class="flex justify-end gap-2">
        <BaseButton variant="secondary" @click="handleCancel">
          {{ state.cancelText }}
        </BaseButton>
        <BaseButton :variant="state.variant === 'primary' ? 'primary' : 'danger'" @click="handleConfirm">
          {{ state.confirmText }}
        </BaseButton>
      </div>
    </div>
  </BaseModal>
</template>
