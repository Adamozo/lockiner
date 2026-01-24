<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean;
  loading: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  submit: [provider: { provider: string; api_key: string; is_active: boolean }];
}>();

const availableProviders = [
  { value: "gemini", label: "Google Gemini" },
  { value: "claude", label: "Anthropic Claude" },
  { value: "openai", label: "OpenAI GPT-4" },
];

const newProvider = ref({
  provider: "",
  api_key: "",
  is_active: false,
});

const handleSubmit = () => {
  emit("submit", { ...newProvider.value });
};

const handleClose = () => {
  emit("update:modelValue", false);
};

// Reset form when dialog is closed
watch(
  () => props.modelValue,
  (isOpen) => {
    if (!isOpen) {
      newProvider.value = { provider: "", api_key: "", is_active: false };
    }
  }
);
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Add API Provider"
    max-width="2xl"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-pure-white mb-2">
          Provider
        </label>
        <select
          v-model="newProvider.provider"
          class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
        >
          <option value="" disabled>Select provider</option>
          <option
            v-for="option in availableProviders"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-pure-white mb-2">
          API Key
        </label>
        <input
          v-model="newProvider.api_key"
          type="password"
          placeholder="Enter API key"
          class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
        />
      </div>

      <div class="flex items-center gap-2">
        <input
          id="is-active"
          v-model="newProvider.is_active"
          type="checkbox"
          class="w-4 h-4 rounded border-border-gray bg-background-black text-cyber-blue focus:ring-2 focus:ring-cyber-blue/30"
        />
        <label for="is-active" class="text-sm text-pure-white">
          Set as active provider
        </label>
      </div>

      <div class="flex justify-end gap-2 pt-4">
        <BaseButton
          type="button"
          variant="secondary"
          @click="handleClose"
        >
          Cancel
        </BaseButton>
        <BaseButton
          type="submit"
          variant="primary"
          :loading="loading"
          :disabled="!newProvider.provider || !newProvider.api_key"
        >
          Add Provider
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
