<script setup lang="ts">
import type { APIProviderConfig } from "~/composables/useSettings";

definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: "Settings - LockIner",
  description: "Configure application settings and API providers",
});

const { getAPIProviders, addAPIProvider, setActiveProvider, deleteAPIProvider } =
  useSettings();
const toast = useToast();

// State
const providers = ref<APIProviderConfig[]>([]);
const activeProvider = ref<string | null>(null);
const loading = ref(false);
const showAddDialog = ref(false);
const showDeleteDialog = ref(false);
const providerToDelete = ref<string | null>(null);

// Methods
const loadProviders = async () => {
  try {
    const response = await getAPIProviders();
    providers.value = response.providers;
    activeProvider.value = response.active_provider;
  } catch (error) {
    toast.add({
      title: "Error",
      description: "Failed to load API providers",
      color: "red",
    });
  }
};

const handleAddProvider = async (newProvider: {
  provider: string;
  api_key: string;
  is_active: boolean;
}) => {
  loading.value = true;
  try {
    await addAPIProvider(newProvider);
    toast.add({
      title: "Success",
      description: "API provider added successfully",
      color: "green",
    });
    showAddDialog.value = false;
    await loadProviders();
  } catch (error) {
    toast.add({
      title: "Error",
      description: "Failed to add API provider",
      color: "red",
    });
  } finally {
    loading.value = false;
  }
};

const setActive = async (provider: string) => {
  loading.value = true;
  try {
    await setActiveProvider(provider);
    toast.add({
      title: "Success",
      description: `${getProviderName(provider)} set as active provider`,
      color: "green",
    });
    await loadProviders();
  } catch (error) {
    toast.add({
      title: "Error",
      description: "Failed to set active provider",
      color: "red",
    });
  } finally {
    loading.value = false;
  }
};

const confirmDelete = (provider: string) => {
  providerToDelete.value = provider;
  showDeleteDialog.value = true;
};

const handleDelete = async () => {
  if (!providerToDelete.value) return;

  loading.value = true;
  try {
    await deleteAPIProvider(providerToDelete.value);
    toast.add({
      title: "Success",
      description: "API provider deleted successfully",
      color: "green",
    });
    showDeleteDialog.value = false;
    providerToDelete.value = null;
    await loadProviders();
  } catch (error) {
    toast.add({
      title: "Error",
      description: "Failed to delete API provider",
      color: "red",
    });
  } finally {
    loading.value = false;
  }
};

const getProviderName = (provider: string): string => {
  const names: Record<string, string> = {
    gemini: "Google Gemini",
    claude: "Anthropic Claude",
    openai: "OpenAI GPT-4",
  };
  return names[provider] || provider;
};

// Load providers on mount
onMounted(() => {
  loadProviders();
});
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <SettingsHeader
      title="Settings"
      description="Configure your LockIner application"
    />

    <!-- OCR Provider Configuration Section -->
    <div
      class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden"
    >
      <!-- Section Header -->
      <div class="px-6 py-4 border-b border-border-gray relative">
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
        />
        <h2 class="text-xl font-semibold text-pure-white">
          OCR API Configuration
        </h2>
        <p class="mt-1 text-sm text-pure-white/60">
          Configure API providers for receipt OCR processing
        </p>
      </div>

      <div class="px-6 py-6 space-y-6">
        <!-- Active Provider Display -->
        <SettingsOcrActiveProviderBanner
          v-if="activeProvider"
          :provider-name="getProviderName(activeProvider)"
        />

        <!-- Providers List -->
        <div class="space-y-4">
          <SettingsOcrProviderCard
            v-for="provider in providers"
            :key="provider.provider"
            :provider="provider"
            :provider-name="getProviderName(provider.provider)"
            @set-active="setActive"
            @delete="confirmDelete"
          />

          <div
            v-if="providers.length === 0"
            class="text-center py-12 text-pure-white/60"
          >
            <UIcon
              name="i-heroicons-key"
              class="w-12 h-12 mx-auto text-pure-white/40 mb-3"
            />
            <p>No API providers configured yet</p>
            <p class="text-sm mt-1">Add a provider to enable OCR processing</p>
          </div>
        </div>

        <!-- Add Provider Button -->
        <BaseButton
          variant="primary"
          icon="i-heroicons-plus"
          @click="showAddDialog = true"
        >
          Add API Provider
        </BaseButton>

        <!-- Info box -->
        <SettingsOcrInfoBox />
      </div>
    </div>

    <!-- Add Provider Dialog -->
    <SettingsAddProviderDialog
      v-model="showAddDialog"
      :loading="loading"
      @submit="handleAddProvider"
    />

    <!-- Delete Confirmation Dialog -->
    <SettingsDeleteProviderDialog
      v-model="showDeleteDialog"
      :provider-name="getProviderName(providerToDelete || '')"
      :loading="loading"
      @confirm="handleDelete"
    />
  </div>
</template>
