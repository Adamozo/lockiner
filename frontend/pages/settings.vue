<script setup lang="ts">
import type { APIProviderConfig } from "~/composables/useSettings";

definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: "Settings - LockIner",
  description: "Configure application settings and API providers",
});

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const { getAPIProviders, addAPIProvider, setActiveProvider, deleteAPIProvider } =
  useSettings();
const { isInstallable, isInstalled, needRefresh, installApp, refreshApp } = usePWAInstall();
const toast = useToast();

// ─── Tabs ─────────────────────────────────────────────────────────────────

const TABS = [
  { id: 'general',       labelKey: 'settings.tab_general',       icon: 'i-heroicons-cog-6-tooth' },
  { id: 'notifications', labelKey: 'settings.tab_notifications',  icon: 'i-heroicons-bell' },
  { id: 'backup',        labelKey: 'settings.tab_backup',         icon: 'i-heroicons-archive-box-arrow-down' },
  { id: 'integrations',  labelKey: 'settings.tab_integrations',   icon: 'i-heroicons-puzzle-piece' },
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
      toast.add({ title: t('common.success'), description: t('settings.install_success'), color: "green" });
    }
  } finally {
    isInstallingPWA.value = false;
  }
};

const handleUpdatePWA = async () => {
  isUpdatingPWA.value = true;
  try {
    await refreshApp();
    toast.add({ title: t('settings.updating_title'), description: t('settings.updating_desc'), color: "green" });
    setTimeout(() => window.location.reload(), 1000);
  } catch {
    toast.add({ title: t('common.error'), description: t('settings.update_failed'), color: "red" });
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
    toast.add({ title: t('common.error'), description: t('settings.providers_failed'), color: "red" });
  }
};

const handleAddProvider = async (newProvider: { provider: string; api_key: string; is_active: boolean }) => {
  loading.value = true;
  try {
    await addAPIProvider(newProvider);
    toast.add({ title: t('common.success'), description: t('settings.provider_added'), color: "green" });
    showAddDialog.value = false;
    await loadProviders();
  } catch {
    toast.add({ title: t('common.error'), description: t('settings.provider_add_failed'), color: "red" });
  } finally {
    loading.value = false;
  }
};

const setActive = async (provider: string) => {
  loading.value = true;
  try {
    await setActiveProvider(provider);
    toast.add({ title: t('common.success'), description: t('settings.provider_set_active', { name: getProviderName(provider) }), color: "green" });
    await loadProviders();
  } catch {
    toast.add({ title: t('common.error'), description: t('settings.provider_set_active_failed'), color: "red" });
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
    toast.add({ title: t('common.success'), description: t('settings.provider_deleted'), color: "green" });
    showDeleteDialog.value = false;
    providerToDelete.value = null;
    await loadProviders();
  } catch {
    toast.add({ title: t('common.error'), description: t('settings.provider_delete_failed'), color: "red" });
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
      :title="$t('settings.title')"
      :description="$t('settings.description')"
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
            <span class="text-pure-white">{{ $t(currentTabDef.labelKey) }}</span>
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
            {{ $t(tab.labelKey) }}
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
            {{ $t(tab.labelKey) }}
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
            <h3 class="text-base font-semibold text-pure-white mb-3">{{ $t('settings.app_installation') }}</h3>
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
                    <p class="text-pure-white font-medium">{{ isInstalled ? $t('settings.app_installed') : $t('settings.install_app') }}</p>
                    <p class="text-sm text-pure-white/60">{{ isInstalled ? $t('settings.installed_on_device') : $t('settings.add_to_home_screen') }}</p>
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
                      {{ $t('settings.install') }}
                    </BaseButton>
                    <span v-else-if="isInstalled" class="text-sm text-electric-green font-medium">{{ $t('settings.installed') }}</span>
                    <span v-else class="text-sm text-pure-white/40">{{ $t('common.na') }}</span>
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
                    <p class="text-pure-white font-medium">{{ needRefresh ? $t('settings.update_ready') : $t('settings.updates') }}</p>
                    <p class="text-sm text-pure-white/60">{{ needRefresh ? $t('settings.new_version') : $t('settings.up_to_date') }}</p>
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
                      {{ $t('settings.update') }}
                    </BaseButton>
                    <BaseButton
                      v-else
                      variant="ghost"
                      icon="i-heroicons-arrow-path"
                      size="sm"
                      :loading="isUpdatingPWA"
                      @click="handleUpdatePWA"
                    >
                      {{ $t('common.check') }}
                    </BaseButton>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Language -->
          <div>
            <h3 class="text-base font-semibold text-pure-white mb-3">{{ $t('settings.language') }}</h3>
            <p class="text-sm text-pure-white/60 mb-3">{{ $t('settings.language_desc') }}</p>
            <LanguageSwitcher />
          </div>

          <!-- 2FA -->
          <div>
            <h3 class="text-base font-semibold text-pure-white mb-3">{{ $t('settings.security') }}</h3>
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
            <h3 class="text-base font-semibold text-pure-white mb-1">{{ $t('settings.ocr_api_config') }}</h3>
            <p class="text-sm text-pure-white/60 mb-4">{{ $t('settings.ocr_api_desc') }}</p>

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
                <p>{{ $t('settings.no_providers') }}</p>
                <p class="text-sm mt-1">{{ $t('settings.no_providers_hint') }}</p>
              </div>
            </div>

            <div class="mt-4 space-y-4">
              <BaseButton variant="primary" icon="i-heroicons-plus" @click="showAddDialog = true">
                {{ $t('settings.add_provider') }}
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
