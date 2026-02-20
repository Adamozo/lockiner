<script setup lang="ts">
import type { BackupSettings, BackupScheduleUpdate } from '~/composables/useBackup'

const {
  getSettings,
  updateSchedule,
  getPassword,
  setPassword,
  downloadBackup,
  getGoogleDriveAuthUrl,
  disconnectGoogleDrive,
} = useBackup()

const toast = useToast()
const route = useRoute()
const router = useRouter()

// ─── State ────────────────────────────────────────────────────────────────

const settings = ref<BackupSettings | null>(null)
const passwordStatus = ref<{ password: string | null; configured: boolean }>({
  password: null,
  configured: false,
})

// Password sub-card
const newPassword = ref('')
const showPassword = ref(false)
const passwordLoading = ref(false)

// Download sub-card
const downloadLoading = ref(false)

// Google Drive sub-card
const driveLoading = ref(false)

// Schedule sub-card — draft state
const scheduleDraft = ref<BackupScheduleUpdate>({
  auto_backup_enabled: false,
  frequency: 'weekly',
  hour: 8,
  minute: 0,
  day_of_week: 0,
  day_of_month: null,
})
const scheduleLoading = ref(false)

const scheduleIsDirty = computed(() => {
  if (!settings.value) return false
  const s = settings.value
  const d = scheduleDraft.value
  return (
    d.auto_backup_enabled !== s.auto_backup_enabled ||
    d.frequency !== s.frequency ||
    d.hour !== s.hour ||
    d.minute !== s.minute ||
    d.day_of_week !== s.day_of_week ||
    d.day_of_month !== s.day_of_month
  )
})

// ─── Helpers ──────────────────────────────────────────────────────────────

const formatBytes = (bytes: number): string => {
  if (bytes < 1_048_576) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${(bytes / 1_048_576).toFixed(2)} MB`
}

const formatDate = (iso: string): string => {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Sync draft from server settings
const syncDraftFromSettings = (s: BackupSettings) => {
  scheduleDraft.value = {
    auto_backup_enabled: s.auto_backup_enabled,
    frequency: s.frequency,
    hour: s.hour,
    minute: s.minute,
    day_of_week: s.day_of_week,
    day_of_month: s.day_of_month,
  }
}

// ─── Load data ────────────────────────────────────────────────────────────

const loadSettings = async () => {
  try {
    settings.value = await getSettings()
    syncDraftFromSettings(settings.value)
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to load backup settings',
      color: 'red',
    })
  }
}

const loadPassword = async () => {
  try {
    passwordStatus.value = await getPassword()
  } catch {
    // Non-critical — silently ignore
    console.error('Failed to load backup password status')
  }
}

// ─── Password sub-card ────────────────────────────────────────────────────

const handleSetPassword = async () => {
  if (newPassword.value.length < 8) {
    toast.add({
      title: 'Invalid password',
      description: 'Password must be at least 8 characters',
      color: 'orange',
    })
    return
  }

  passwordLoading.value = true
  try {
    await setPassword(newPassword.value)
    toast.add({
      title: 'Password set',
      description: 'Your backup encryption password has been saved',
      color: 'green',
    })
    newPassword.value = ''
    await loadPassword()
    await loadSettings()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Error',
      description: err.data?.detail || 'Failed to set backup password',
      color: 'red',
    })
  } finally {
    passwordLoading.value = false
  }
}

// ─── Download sub-card ────────────────────────────────────────────────────

const handleDownload = async () => {
  downloadLoading.value = true
  try {
    await downloadBackup()
    toast.add({
      title: 'Download started',
      description: 'Your backup file is being downloaded',
      color: 'green',
    })
    // Refresh last_backup_at
    await loadSettings()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Download failed',
      description: err.data?.detail || 'Failed to download backup',
      color: 'red',
    })
  } finally {
    downloadLoading.value = false
  }
}

// ─── Google Drive sub-card ────────────────────────────────────────────────

const handleConnectDrive = async () => {
  driveLoading.value = true
  try {
    const authUrl = await getGoogleDriveAuthUrl()
    window.location.href = authUrl
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Error',
      description: err.data?.detail || 'Failed to get Google Drive auth URL',
      color: 'red',
    })
    driveLoading.value = false
  }
}

const handleDisconnectDrive = async () => {
  driveLoading.value = true
  try {
    await disconnectGoogleDrive()
    toast.add({
      title: 'Disconnected',
      description: 'Google Drive has been disconnected',
      color: 'green',
    })
    await loadSettings()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Error',
      description: err.data?.detail || 'Failed to disconnect Google Drive',
      color: 'red',
    })
  } finally {
    driveLoading.value = false
  }
}

// ─── Schedule sub-card ────────────────────────────────────────────────────

const handleSaveSchedule = async () => {
  scheduleLoading.value = true
  try {
    const updated = await updateSchedule(scheduleDraft.value)
    settings.value = updated
    syncDraftFromSettings(updated)
    toast.add({
      title: 'Saved',
      description: 'Auto-backup schedule updated',
      color: 'green',
    })
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Error',
      description: err.data?.detail || 'Failed to save schedule',
      color: 'red',
    })
  } finally {
    scheduleLoading.value = false
  }
}

const handleResetSchedule = () => {
  if (settings.value) {
    syncDraftFromSettings(settings.value)
  }
}

// Watch frequency changes to clear irrelevant day fields
watch(
  () => scheduleDraft.value.frequency,
  (freq) => {
    if (freq === 'daily') {
      scheduleDraft.value.day_of_week = null
      scheduleDraft.value.day_of_month = null
    } else if (freq === 'weekly') {
      scheduleDraft.value.day_of_month = null
      if (scheduleDraft.value.day_of_week === null) {
        scheduleDraft.value.day_of_week = 0
      }
    } else if (freq === 'monthly') {
      scheduleDraft.value.day_of_week = null
      if (scheduleDraft.value.day_of_month === null) {
        scheduleDraft.value.day_of_month = 1
      }
    }
  },
)

// ─── Mount: load data + handle OAuth callback query params ────────────────

onMounted(async () => {
  await Promise.all([loadSettings(), loadPassword()])

  // Handle OAuth redirect back from Google Drive
  if (route.query.backup_drive_connected === '1') {
    toast.add({
      title: 'Google Drive connected',
      description: 'Your Google Drive account has been linked successfully',
      color: 'green',
    })
  } else if (route.query.backup_drive_error === '1') {
    toast.add({
      title: 'Connection failed',
      description: 'Failed to connect Google Drive. Please try again.',
      color: 'red',
    })
  }

  // Clean up query params
  if (
    route.query.backup_drive_connected !== undefined ||
    route.query.backup_drive_error !== undefined
  ) {
    const { backup_drive_connected: _a, backup_drive_error: _b, ...rest } = route.query
    await router.replace({ query: rest })
  }
})

// ─── Computed helpers ─────────────────────────────────────────────────────

const scheduleCanBeEnabled = computed(
  () =>
    settings.value?.google_drive_connected === true &&
    settings.value?.password_configured === true,
)

const dayOfWeekOptions = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
]
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <!-- Section Header -->
    <div class="px-6 py-4 border-b border-border-gray relative">
      <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
      <h2 class="text-xl font-semibold text-pure-white">Backup &amp; Data Export</h2>
      <p class="mt-1 text-sm text-pure-white/60">Export and backup all your personal data</p>
    </div>

    <div class="px-4 sm:px-6 py-6 space-y-4">
      <!-- ── Sub-card 1: Backup Password ─────────────────────────────── -->
      <div class="p-4 bg-background-black rounded-lg border border-border-gray">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-cyber-blue/20 flex items-center justify-center flex-shrink-0">
            <UIcon name="i-heroicons-lock-closed" class="w-5 h-5 text-cyber-blue" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-pure-white font-medium">Backup Password</p>
            <p class="text-sm text-pure-white/60">AES-256 encryption key for your backups</p>
          </div>
          <!-- Badge when configured -->
          <span
            v-if="passwordStatus.configured"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-electric-green/20 text-electric-green flex-shrink-0"
          >
            Password set
          </span>
        </div>

        <!-- Stored password display -->
        <div
          v-if="passwordStatus.configured && passwordStatus.password"
          class="mb-4 p-3 bg-card-black rounded-lg border border-border-gray"
        >
          <p class="text-xs text-pure-white/60 mb-1">Stored password:</p>
          <p class="font-mono text-sm text-electric-green break-all select-all">
            {{ passwordStatus.password }}
          </p>
        </div>

        <!-- No-password warning -->
        <p v-if="!passwordStatus.configured" class="mb-3 text-sm text-warning-orange flex items-center gap-1.5">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 flex-shrink-0" />
          Set a password before downloading backups
        </p>

        <!-- Password input + button -->
        <div class="flex flex-col sm:flex-row gap-3">
          <div class="relative flex-1">
            <input
              v-model="newPassword"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Min. 8 characters"
              class="w-full px-3 py-2 pr-10 bg-card-black border border-border-gray text-pure-white placeholder-pure-white/40 rounded-md text-sm focus:outline-none focus:border-cyber-blue focus:ring-1 focus:ring-cyber-blue/30"
              @keyup.enter="handleSetPassword"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 px-3 text-pure-white/50 hover:text-pure-white transition-colors"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              @click="showPassword = !showPassword"
            >
              <UIcon
                :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                class="w-4 h-4"
              />
            </button>
          </div>
          <BaseButton
            variant="primary"
            size="sm"
            :loading="passwordLoading"
            @click="handleSetPassword"
          >
            Set Password
          </BaseButton>
        </div>
      </div>

      <!-- ── Sub-card 2: Manual Download ────────────────────────────── -->
      <div class="p-4 bg-background-black rounded-lg border border-border-gray">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-electric-green/20 flex items-center justify-center flex-shrink-0">
            <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5 text-electric-green" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-pure-white font-medium">Download Backup</p>
            <p class="text-sm text-pure-white/60">
              Download a complete AES-256 encrypted ZIP of all your data
            </p>
          </div>
        </div>

        <!-- Last backup info -->
        <div
          v-if="settings?.last_backup_at"
          class="mb-4 flex flex-wrap gap-4 text-sm"
        >
          <span class="text-pure-white/60">
            Last backup:
            <span class="text-pure-white ml-1">{{ formatDate(settings.last_backup_at) }}</span>
          </span>
          <span v-if="settings.last_backup_size_bytes" class="text-pure-white/60">
            Size:
            <span class="text-pure-white ml-1">{{ formatBytes(settings.last_backup_size_bytes) }}</span>
          </span>
        </div>

        <!-- Last backup error -->
        <div
          v-if="settings?.last_backup_error"
          class="mb-3 p-3 rounded-lg border border-danger-red/40 bg-danger-red/10 flex items-start gap-2"
        >
          <UIcon name="i-heroicons-x-circle" class="w-4 h-4 text-danger-red flex-shrink-0 mt-0.5" />
          <div>
            <p class="text-xs font-medium text-danger-red">Last backup failed</p>
            <p class="text-xs text-pure-white/70 mt-0.5">{{ settings.last_backup_error }}</p>
          </div>
        </div>

        <!-- Warning when no password -->
        <p
          v-if="!settings?.password_configured"
          class="mb-3 text-sm text-warning-orange flex items-center gap-1.5"
        >
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 flex-shrink-0" />
          Set a backup password above before downloading
        </p>

        <BaseButton
          variant="primary"
          icon="i-heroicons-arrow-down-tray"
          size="sm"
          :loading="downloadLoading"
          :disabled="!settings?.password_configured"
          @click="handleDownload"
        >
          Download
        </BaseButton>
      </div>

      <!-- ── Sub-card 3: Google Drive Integration ────────────────────── -->
      <div class="p-4 bg-background-black rounded-lg border border-border-gray">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
            :class="settings?.google_drive_connected ? 'bg-electric-green/20' : 'bg-card-black'"
          >
            <UIcon
              name="i-heroicons-cloud-arrow-up"
              class="w-5 h-5"
              :class="settings?.google_drive_connected ? 'text-electric-green' : 'text-pure-white/60'"
            />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-pure-white font-medium">Google Drive Sync</p>
            <p class="text-sm text-pure-white/60">
              Automatically save backups to your Google Drive
            </p>
          </div>
          <!-- Connected badge -->
          <span
            v-if="settings?.google_drive_connected"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-electric-green/20 text-electric-green flex-shrink-0"
          >
            Connected
          </span>
        </div>

        <div v-if="settings?.google_drive_connected" class="flex items-center gap-3">
          <p class="text-sm text-pure-white/60 flex-1">
            Backups will be uploaded automatically to your Google Drive folder.
          </p>
          <BaseButton
            variant="danger"
            size="sm"
            :loading="driveLoading"
            @click="handleDisconnectDrive"
          >
            Disconnect
          </BaseButton>
        </div>

        <!-- Drive auth error hint (token revoked) -->
        <div
          v-else-if="settings?.last_backup_error?.toLowerCase().includes('revoked') || settings?.last_backup_error?.toLowerCase().includes('denied')"
          class="mb-3 p-3 rounded-lg border border-warning-orange/40 bg-warning-orange/10 flex items-start gap-2"
        >
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 text-warning-orange flex-shrink-0 mt-0.5" />
          <p class="text-xs text-pure-white/70">
            Google Drive access was revoked. Please reconnect your account.
          </p>
        </div>

        <BaseButton
          v-if="!settings?.google_drive_connected"
          variant="secondary"
          icon="i-heroicons-cloud-arrow-up"
          size="sm"
          :loading="driveLoading"
          @click="handleConnectDrive"
        >
          Connect Google Drive
        </BaseButton>
      </div>

      <!-- ── Sub-card 4: Auto-backup Schedule ───────────────────────── -->
      <div class="p-4 bg-background-black rounded-lg border border-border-gray">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
            :class="scheduleDraft.auto_backup_enabled ? 'bg-cyber-blue/20' : 'bg-card-black'"
          >
            <UIcon
              name="i-heroicons-clock"
              class="w-5 h-5"
              :class="scheduleDraft.auto_backup_enabled ? 'text-cyber-blue' : 'text-pure-white/60'"
            />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-pure-white font-medium">Auto-backup Schedule</p>
            <p class="text-sm text-pure-white/60">
              Automatically back up your data on a recurring schedule
            </p>
          </div>
          <!-- Enable toggle -->
          <button
            type="button"
            role="switch"
            :aria-checked="scheduleDraft.auto_backup_enabled"
            :disabled="!scheduleCanBeEnabled"
            class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none disabled:opacity-40 disabled:cursor-not-allowed"
            :class="scheduleDraft.auto_backup_enabled ? 'bg-cyber-blue' : 'bg-border-gray'"
            @click="scheduleCanBeEnabled && (scheduleDraft.auto_backup_enabled = !scheduleDraft.auto_backup_enabled)"
          >
            <span
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200"
              :class="scheduleDraft.auto_backup_enabled ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>

        <!-- Requirements warning -->
        <p
          v-if="!scheduleCanBeEnabled"
          class="mb-4 text-sm text-warning-orange flex items-center gap-1.5"
        >
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 flex-shrink-0" />
          Connect Google Drive and set a password to enable auto-backup
        </p>

        <!-- Schedule options (visible when enabled) -->
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <div v-if="scheduleDraft.auto_backup_enabled" class="space-y-3">
            <!-- Frequency -->
            <div class="flex flex-wrap items-center gap-3">
              <label class="text-sm text-pure-white/70 w-28 flex-shrink-0">Frequency</label>
              <select
                v-model="scheduleDraft.frequency"
                class="bg-background-black border border-border-gray text-pure-white rounded-md px-2 py-1 text-sm focus:outline-none focus:border-cyber-blue"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <!-- Hour -->
            <div class="flex flex-wrap items-center gap-3">
              <label class="text-sm text-pure-white/70 w-28 flex-shrink-0">Hour</label>
              <select
                v-model.number="scheduleDraft.hour"
                class="bg-background-black border border-border-gray text-pure-white rounded-md px-2 py-1 text-sm focus:outline-none focus:border-cyber-blue"
              >
                <option v-for="h in 24" :key="h - 1" :value="h - 1">
                  {{ String(h - 1).padStart(2, '0') }}:00
                </option>
              </select>
            </div>

            <!-- Minute -->
            <div class="flex flex-wrap items-center gap-3">
              <label class="text-sm text-pure-white/70 w-28 flex-shrink-0">Minute</label>
              <select
                v-model.number="scheduleDraft.minute"
                class="bg-background-black border border-border-gray text-pure-white rounded-md px-2 py-1 text-sm focus:outline-none focus:border-cyber-blue"
              >
                <option :value="0">:00</option>
                <option :value="15">:15</option>
                <option :value="30">:30</option>
                <option :value="45">:45</option>
              </select>
            </div>

            <!-- Day of week (weekly only) -->
            <div v-if="scheduleDraft.frequency === 'weekly'" class="flex flex-wrap items-center gap-3">
              <label class="text-sm text-pure-white/70 w-28 flex-shrink-0">Day of week</label>
              <select
                v-model.number="scheduleDraft.day_of_week"
                class="bg-background-black border border-border-gray text-pure-white rounded-md px-2 py-1 text-sm focus:outline-none focus:border-cyber-blue"
              >
                <option
                  v-for="opt in dayOfWeekOptions"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <!-- Day of month (monthly only) -->
            <div v-if="scheduleDraft.frequency === 'monthly'" class="flex flex-wrap items-center gap-3">
              <label class="text-sm text-pure-white/70 w-28 flex-shrink-0">Day of month</label>
              <select
                v-model.number="scheduleDraft.day_of_month"
                class="bg-background-black border border-border-gray text-pure-white rounded-md px-2 py-1 text-sm focus:outline-none focus:border-cyber-blue"
              >
                <option v-for="d in 31" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>

            <!-- Dirty-state actions -->
            <div v-if="scheduleIsDirty" class="flex items-center gap-3 pt-2">
              <BaseButton
                variant="primary"
                size="sm"
                :loading="scheduleLoading"
                @click="handleSaveSchedule"
              >
                Save
              </BaseButton>
              <BaseButton
                variant="ghost"
                size="sm"
                :disabled="scheduleLoading"
                @click="handleResetSchedule"
              >
                Reset
              </BaseButton>
            </div>
            <p v-else class="text-xs text-pure-white/40 pt-1">
              No unsaved changes
            </p>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>
