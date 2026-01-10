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

const newProvider = ref({
  provider: "",
  api_key: "",
  is_active: false,
});

const availableProviders = [
  { value: "gemini", label: "Google Gemini" },
  { value: "claude", label: "Anthropic Claude" },
  { value: "openai", label: "OpenAI GPT-4" },
];

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

const handleAddProvider = async () => {
  loading.value = true;
  try {
    await addAPIProvider(newProvider.value);
    toast.add({
      title: "Success",
      description: "API provider added successfully",
      color: "green",
    });
    showAddDialog.value = false;
    newProvider.value = { provider: "", api_key: "", is_active: false };
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

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString("pl-PL", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

// Load providers on mount
onMounted(() => {
  loadProviders();
});
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header>
      <h1 class="text-3xl font-bold text-pure-white">Settings</h1>
      <p class="mt-2 text-pure-white/60">
        Configure your LockIner application
      </p>
    </header>

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
        <div
          v-if="activeProvider"
          class="p-4 bg-electric-green/10 border border-electric-green/30 rounded-lg backdrop-blur-sm"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-3 h-3 rounded-full bg-electric-green shadow-lg shadow-electric-green/50"
            />
            <span class="font-medium text-pure-white">Active Provider:</span>
            <span class="text-pure-white capitalize">{{
              getProviderName(activeProvider)
            }}</span>
          </div>
        </div>

        <!-- Providers List -->
        <div class="space-y-4">
          <div
            v-for="provider in providers"
            :key="provider.provider"
            class="flex items-center justify-between p-4 border rounded-lg transition-all"
            :class="{
              'border-electric-green bg-electric-green/10': provider.is_active,
              'border-border-gray bg-background-black': !provider.is_active,
            }"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-pure-white capitalize">{{
                  getProviderName(provider.provider)
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
                @click="setActive(provider.provider)"
              >
                Set Active
              </BaseButton>
              <BaseButton
                variant="danger"
                size="sm"
                icon="i-heroicons-trash"
                @click="confirmDelete(provider.provider)"
              />
            </div>
          </div>

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
        <div
          class="p-4 bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg backdrop-blur-sm"
        >
          <div class="flex">
            <UIcon
              name="i-heroicons-information-circle"
              class="w-5 h-5 text-cyber-blue mr-3 flex-shrink-0 mt-0.5"
            />
            <div class="text-sm text-pure-white/80">
              <p class="font-medium text-pure-white mb-1">
                About OCR Providers
              </p>
              <p>
                Configure multiple AI providers for receipt OCR processing. Only
                one provider can be active at a time. Your API keys are stored
                securely and encrypted.
              </p>
              <ul class="mt-2 space-y-1 list-disc list-inside">
                <li>
                  <strong>Gemini:</strong> Get API key from
                  <a
                    href="https://aistudio.google.com/app/apikey"
                    target="_blank"
                    class="text-cyber-blue hover:underline"
                    >Google AI Studio</a
                  >
                </li>
                <li>
                  <strong>Claude:</strong> Get API key from
                  <a
                    href="https://console.anthropic.com/"
                    target="_blank"
                    class="text-cyber-blue hover:underline"
                    >Anthropic Console</a
                  >
                </li>
                <li>
                  <strong>OpenAI:</strong> Get API key from
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    class="text-cyber-blue hover:underline"
                    >OpenAI Platform</a
                  >
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Provider Dialog -->
    <BaseModal
      v-model="showAddDialog"
      title="Add API Provider"
      max-width="2xl"
    >
      <form @submit.prevent="handleAddProvider" class="space-y-4">
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
            @click="showAddDialog = false"
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

    <!-- Delete Confirmation Dialog -->
    <BaseModal
      v-model="showDeleteDialog"
      title="Delete Provider"
      max-width="lg"
    >
      <div class="space-y-6">
        <p class="text-pure-white/80">
          Are you sure you want to delete the
          <span class="font-semibold capitalize">{{
            getProviderName(providerToDelete || "")
          }}</span>
          provider configuration?
        </p>

        <div class="flex justify-end gap-2">
          <BaseButton
            variant="secondary"
            @click="showDeleteDialog = false"
          >
            Cancel
          </BaseButton>
          <BaseButton variant="danger" :loading="loading" @click="handleDelete">
            Delete
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>
