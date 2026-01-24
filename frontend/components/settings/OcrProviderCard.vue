<script setup lang="ts">
import type { APIProviderConfig } from "~/composables/useSettings";

const props = defineProps<{
  provider: APIProviderConfig;
  providerName: string;
}>();

const emit = defineEmits<{
  setActive: [provider: string];
  delete: [provider: string];
}>();

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString("pl-PL", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};
</script>

<template>
  <div
    class="flex items-center justify-between p-4 border rounded-lg transition-all"
    :class="{
      'border-electric-green bg-electric-green/10': provider.is_active,
      'border-border-gray bg-background-black': !provider.is_active,
    }"
  >
    <div class="flex-1">
      <div class="flex items-center gap-2 mb-1">
        <span class="font-medium text-pure-white capitalize">{{
          providerName
        }}</span>
        <UBadge v-if="provider.is_active" color="success" variant="solid">
          Active
        </UBadge>
      </div>
      <div class="text-sm text-pure-white/60">
        Key: {{ provider.key_preview }}
      </div>
      <div
        v-if="provider.configured_at"
        class="text-xs text-pure-white/40 mt-1"
      >
        Configured: {{ formatDate(provider.configured_at) }}
      </div>
    </div>

    <div class="flex items-center gap-2">
      <BaseButton
        v-if="!provider.is_active"
        variant="secondary"
        size="sm"
        @click="emit('setActive', provider.provider)"
      >
        Set Active
      </BaseButton>
      <BaseButton
        variant="danger"
        size="sm"
        icon="i-heroicons-trash"
        @click="emit('delete', provider.provider)"
      />
    </div>
  </div>
</template>
