<script setup lang="ts">
import type { APIProviderConfig } from "~/composables/useSettings";

definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: "Settings - LockIner",
  description: "Configure application settings and API providers",
});

const route = useRoute()
const router = useRouter()

const { getAPIProviders, addAPIProvider, setActiveProvider, deleteAPIProvider } =
  useSettings();
const { isInstallable, isInstalled, needRefresh, installApp, refreshApp } = usePWAInstall();
const toast = useToast();

// ─── Tabs ─────────────────────────────────────────────────────────────────

const TABS = [
  { id: 'general',       label: 'General',       icon: 'i-heroicons-cog-6-tooth' },
  { id: 'notifications', label: 'Notifications',  icon: 'i-heroicons-bell' },
  { id: 'backup',        label: 'Backup',         icon: 'i-heroicons-archive-box-arrow-down' },
  { id: 'integrations',  label: 'Integrations',   icon: 'i-heroicons-puzzle-piece' },
] as const

type TabId = typeof TABS[number]['id']

const activeTab = computed<TabId>(() => {
  // If backup-related query params present, land on backup tab
  if (route.query.backup_drive_connected || route.query.backup_drive_error) {
    return 'backup'
  }
  const q = route.query.tab as string
  return (TABS.some(t => t.id === q) ? q : 'general') as TabId
})

const setTab = (id: TabId) => {
  router.replace({ query: { ...route.query, tab: id } })
  mobileDropdownOpen.value = false
}

const mobileDropdownOpen = ref(false)
const currentTabDef = computed(() => TABS.find(t => t.id === activeTab.value)!)

if (import.meta.client) {
  document.addEventListener('click', (e) => {
    if (mobileDropdownOpen.value) {
      const target = e.target as HTMLElement
      if (!target.closest('.mobile-tab-dropdown')) {
        mobileDropdownOpen.value = false
      }
    }
  })
}

// ─── PWA ──────────────────────────────────────────────────────────────────

const isInstallingPWA = ref(false);
const isUpdatingPWA = ref(false);

const handleInstallPWA = async () => {
  isInstallingPWA.value = true;
  try {
    const success = await installApp();
    if (success) {
      toast.add({ title: "Success", description: "LockIner has been installed!", color: "green" });
    }
  } finally {
    isInstallingPWA.value = false;
  }
};

const handleUpdatePWA = async () => {
  isUpdatingPWA.value = true;
  try {
    await refreshApp();
    toast.add({ title: "Updating...", description: "The app will reload with the latest version", color: "green" });
    setTimeout(() => window.location.reload(), 1000);
  } catch {
    toast.add({ title: "Error", description: "Failed to update the app", color: "red" });
    isUpdatingPWA.value = false;
  }
};

// ─── OCR providers ────────────────────────────────────────────────────────

const providers = ref<APIProviderConfig[]>([]);
const activeProvider = ref<string | null>(null);
const loading = ref(false);
const showAddDialog = ref(false);
const showDeleteDialog = ref(false);
const providerToDelete = ref<string | null>(null);

const loadProviders = async () => {
  try {
    const response = await getAPIProviders();
    providers.value = response.providers;
    activeProvider.value = response.active_provider;
  } catch {
    toast.add({ title: "Error", description: "Failed to load API providers", color: "red" });
  }
};

const handleAddProvider = async (newProvider: { provider: string; api_key: string; is_active: boolean }) => {
  loading.value = true;
  try {
    await addAPIProvider(newProvider);
    toast.add({ title: "Success", description: "API provider added successfully", color: "green" });
    showAddDialog.value = false;
    await loadProviders();
  } catch {
    toast.add({ title: "Error", description: "Failed to add API provider", color: "red" });
  } finally {
    loading.value = false;
  }
};

const setActive = async (provider: string) => {
  loading.value = true;
  try {
    await setActiveProvider(provider);
    toast.add({ title: "Success", description: `${getProviderName(provider)} set as active provider`, color: "green" });
    await loadProviders();
  } catch {
    toast.add({ title: "Error", description: "Failed to set active provider", color: "red" });
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
    toast.add({ title: "Success", description: "API provider deleted successfully", color: "green" });
    showDeleteDialog.value = false;
    providerToDelete.value = null;
    await loadProviders();
  } catch {
    toast.add({ title: "Error", description: "Failed to delete API provider", color: "red" });
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

onMounted(() => {
  loadProviders();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <SettingsHeader
      title="Settings"
      description="Configure your LockIner application"
    />

    <!-- Tab bar -->
    <div class="bg-card-black border border-border-gray rounded-lg overflow-hidden">
      <!-- Mobile: custom dropdown -->
      <div class="mobile-tab-dropdown sm:hidden relative border-b border-border-gray">
        <!-- Trigger -->
        <button
          class="w-full flex items-center justify-between gap-3 px-4 py-3.5 text-sm font-medium focus:outline-none"
          @click="mobileDropdownOpen = !mobileDropdownOpen"
        >
          <span class="flex items-center gap-2">
            <UIcon :name="currentTabDef.icon" class="w-4 h-4 text-cyber-blue" />
            <span class="text-pure-white">{{ currentTabDef.label }}</span>
          </span>
          <UIcon
            name="i-heroicons-chevron-down"
            class="w-4 h-4 text-pure-white/50 transition-transform"
            :class="mobileDropdownOpen ? 'rotate-180' : ''"
          />
        </button>

        <!-- Dropdown options -->
        <div
          v-if="mobileDropdownOpen"
          class="absolute top-full left-0 right-0 z-50 bg-card-black border border-border-gray border-t-0 rounded-b-lg overflow-hidden shadow-lg"
        >
          <button
            v-for="tab in TABS"
            :key="tab.id"
            class="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors text-left"
            :class="activeTab === tab.id
              ? 'text-cyber-blue bg-cyber-blue/10'
              : 'text-pure-white/70 hover:text-pure-white hover:bg-white/5'"
            @click="setTab(tab.id)"
          >
            <UIcon :name="tab.icon" class="w-4 h-4 flex-shrink-0" />
            {{ tab.label }}
            <UIcon
              v-if="activeTab === tab.id"
              name="i-heroicons-check"
              class="w-4 h-4 ml-auto text-cyber-blue"
            />
          </button>
        </div>
      </div>

      <!-- Desktop: tabs -->
      <div class="hidden sm:block">
        <nav class="flex border-b border-border-gray" role="tablist">
          <button
            v-for="tab in TABS"
            :key="tab.id"
            role="tab"
            :aria-selected="activeTab === tab.id"
            class="relative flex items-center gap-2 px-5 py-3.5 text-sm font-medium whitespace-nowrap transition-colors focus:outline-none"
            :class="activeTab === tab.id
              ? 'text-cyber-blue'
              : 'text-pure-white/50 hover:text-pure-white/80'"
            @click="setTab(tab.id)"
          >
            <UIcon :name="tab.icon" class="w-4 h-4 flex-shrink-0" />
            {{ tab.label }}
            <span
              v-if="activeTab === tab.id"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-cyber-blue"
            />
          </button>
        </nav>
      </div>

      <!-- Tab content -->
      <div class="p-4 sm:p-6">

        <!-- ── GENERAL ───────────────────────────────────────────────── -->
        <div v-show="activeTab === 'general'" class="space-y-6">

          <!-- App Installation -->
          <div>
            <h3 class="text-base font-semibold text-pure-white mb-3">App Installation</h3>
            <div class="space-y-3">
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
                    <p class="text-pure-white font-medium">{{ isInstalled ? 'App Installed' : 'Install App' }}</p>
                    <p class="text-sm text-pure-white/60">{{ isInstalled ? 'Installed on device' : 'Add to home screen' }}</p>
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
                    <span v-else-if="isInstalled" class="text-sm text-electric-green font-medium">Installed</span>
                    <span v-else class="text-sm text-pure-white/40">N/A</span>
                  </div>
                </div>
              </div>

              <!-- Update -->
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
                    <p class="text-pure-white font-medium">{{ needRefresh ? 'Update Ready' : 'Updates' }}</p>
                    <p class="text-sm text-pure-white/60">{{ needRefresh ? 'New version available' : 'Up to date' }}</p>
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

          <!-- 2FA -->
          <div>
            <h3 class="text-base font-semibold text-pure-white mb-3">Security</h3>
            <SettingsTwoFactorSection />
          </div>
        </div>

        <!-- ── NOTIFICATIONS ──────────────────────────────────────────── -->
        <div v-show="activeTab === 'notifications'">
          <SettingsReminderScheduleSection />
        </div>

        <!-- ── BACKUP ─────────────────────────────────────────────────── -->
        <div v-show="activeTab === 'backup'">
          <SettingsBackupSection />
        </div>

        <!-- ── INTEGRATIONS ───────────────────────────────────────────── -->
        <div v-show="activeTab === 'integrations'" class="space-y-6">
          <div>
            <h3 class="text-base font-semibold text-pure-white mb-1">OCR API Configuration</h3>
            <p class="text-sm text-pure-white/60 mb-4">Configure API providers for receipt OCR processing</p>

            <div class="space-y-4">
              <SettingsOcrActiveProviderBanner
                v-if="activeProvider"
                :provider-name="getProviderName(activeProvider)"
              />

              <SettingsOcrProviderCard
                v-for="provider in providers"
                :key="provider.provider"
                :provider="provider"
                :provider-name="getProviderName(provider.provider)"
                @set-active="setActive"
                @delete="confirmDelete"
              />

              <div v-if="providers.length === 0" class="text-center py-10 text-pure-white/60">
                <UIcon name="i-heroicons-key" class="w-12 h-12 mx-auto text-pure-white/40 mb-3" />
                <p>No API providers configured yet</p>
                <p class="text-sm mt-1">Add a provider to enable OCR processing</p>
              </div>
            </div>

            <div class="mt-4 space-y-4">
              <BaseButton variant="primary" icon="i-heroicons-plus" @click="showAddDialog = true">
                Add API Provider
              </BaseButton>
              <SettingsOcrInfoBox />
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Dialogs (outside tabs so they stay mounted) -->
    <SettingsAddProviderDialog
      v-model="showAddDialog"
      :loading="loading"
      @submit="handleAddProvider"
    />
    <SettingsDeleteProviderDialog
      v-model="showDeleteDialog"
      :provider-name="getProviderName(providerToDelete || '')"
      :loading="loading"
      @confirm="handleDelete"
    />
  </div>
</template>
