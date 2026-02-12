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
const { isInstallable, isInstalled, needRefresh, installApp, refreshApp } = usePWAInstall();
const toast = useToast();

// PWA handlers
const isInstallingPWA = ref(false);
const isUpdatingPWA = ref(false);

const handleInstallPWA = async () => {
  isInstallingPWA.value = true;
  try {
    const success = await installApp();
    if (success) {
      toast.add({
        title: "Success",
        description: "LockIner has been installed!",
        color: "green",
      });
    }
  } finally {
    isInstallingPWA.value = false;
  }
};

const handleUpdatePWA = async () => {
  isUpdatingPWA.value = true;
  try {
    await refreshApp();
    toast.add({
      title: "Updating...",
      description: "The app will reload with the latest version",
      color: "green",
    });
    // Reload to apply updates
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  } catch {
    toast.add({
      title: "Error",
      description: "Failed to update the app",
      color: "red",
    });
    isUpdatingPWA.value = false;
  }
};

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

    <!-- PWA Settings Section -->
    <div
      class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden"
    >
      <!-- Section Header -->
      <div class="px-6 py-4 border-b border-border-gray relative">
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
        />
        <h2 class="text-xl font-semibold text-pure-white">
          App Installation
        </h2>
        <p class="mt-1 text-sm text-pure-white/60">
          Install LockIner as an app for quick access and offline use
        </p>
      </div>

      <div class="px-4 sm:px-6 py-6 space-y-4">
        <!-- Install Status -->
        <div class="p-4 bg-background-black rounded-lg border border-border-gray">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="isInstalled ? 'bg-electric-green/20' : 'bg-cyber-blue/20'"
            >
              <UIcon
                :name="isInstalled ? 'i-heroicons-check-circle' : 'i-heroicons-device-phone-mobile'"
                class="w-5 h-5"
                :class="isInstalled ? 'text-electric-green' : 'text-cyber-blue'"
              />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-pure-white font-medium">
                {{ isInstalled ? 'App Installed' : 'Install App' }}
              </p>
              <p class="text-sm text-pure-white/60">
                {{ isInstalled ? 'Installed on device' : 'Add to home screen' }}
              </p>
            </div>
            <div class="flex-shrink-0">
              <BaseButton
                v-if="isInstallable && !isInstalled"
                variant="primary"
                icon="i-heroicons-arrow-down-tray"
                size="sm"
                :loading="isInstallingPWA"
                @click="handleInstallPWA"
              >
                Install
              </BaseButton>
              <span v-else-if="isInstalled" class="text-sm text-electric-green font-medium whitespace-nowrap">
                Installed
              </span>
              <span v-else class="text-sm text-pure-white/40 whitespace-nowrap">
                N/A
              </span>
            </div>
          </div>
        </div>

        <!-- Update Section -->
        <div class="p-4 bg-background-black rounded-lg border border-border-gray">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="needRefresh ? 'bg-warning-orange/20' : 'bg-card-black'"
            >
              <UIcon
                name="i-heroicons-arrow-path"
                class="w-5 h-5"
                :class="needRefresh ? 'text-warning-orange' : 'text-pure-white/60'"
              />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-pure-white font-medium">
                {{ needRefresh ? 'Update Ready' : 'Updates' }}
              </p>
              <p class="text-sm text-pure-white/60">
                {{ needRefresh ? 'New version available' : 'Up to date' }}
              </p>
            </div>
            <div class="flex-shrink-0">
              <BaseButton
                v-if="needRefresh"
                variant="primary"
                icon="i-heroicons-arrow-path"
                size="sm"
                :loading="isUpdatingPWA"
                @click="handleUpdatePWA"
              >
                Update
              </BaseButton>
              <BaseButton
                v-else
                variant="ghost"
                icon="i-heroicons-arrow-path"
                size="sm"
                :loading="isUpdatingPWA"
                @click="handleUpdatePWA"
              >
                Check
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reminder Notifications Section -->
    <SettingsReminderScheduleSection />

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
