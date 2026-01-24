<script setup lang="ts">
defineProps<{
  modelValue: boolean;
  providerName: string;
  loading: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  confirm: [];
}>();

const handleClose = () => {
  emit("update:modelValue", false);
};
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Delete Provider"
    max-width="lg"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="space-y-6">
      <p class="text-pure-white/80">
        Are you sure you want to delete the
        <span class="font-semibold capitalize">{{ providerName }}</span>
        provider configuration?
      </p>

      <div class="flex justify-end gap-2">
        <BaseButton variant="secondary" @click="handleClose">
          Cancel
        </BaseButton>
        <BaseButton
          variant="danger"
          :loading="loading"
          @click="emit('confirm')"
        >
          Delete
        </BaseButton>
      </div>
    </div>
  </BaseModal>
</template>
