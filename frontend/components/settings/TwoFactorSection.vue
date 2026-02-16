<script setup lang="ts">
const { setup2FA, verifySetup, disable2FA, get2FAStatus, regenerateRecoveryCodes } = useTwoFactor()
const toast = useToast()

// State
const loading = ref(false)
const status = ref<{ enabled: boolean; recovery_codes_remaining: number } | null>(null)

// Setup flow
type Step = 'status' | 'setup' | 'verify' | 'recovery' | 'disable' | 'regenerate'
const currentStep = ref<Step>('status')

const setupData = ref<{ secret: string; uri: string } | null>(null)
const recoveryCodes = ref<string[]>([])
const codeInput = ref('')
const stepError = ref('')

const loadStatus = async () => {
  try {
    status.value = await get2FAStatus()
  } catch {
    status.value = { enabled: false, recovery_codes_remaining: 0 }
  }
}

const startSetup = async () => {
  loading.value = true
  stepError.value = ''
  try {
    setupData.value = await setup2FA()
    currentStep.value = 'setup'
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({
      title: 'Error',
      description: err.data?.detail || 'Failed to start 2FA setup',
      color: 'red',
    })
  } finally {
    loading.value = false
  }
}

const confirmSetup = async () => {
  if (!codeInput.value || codeInput.value.length !== 6) {
    stepError.value = 'Please enter a 6-digit code'
    return
  }

  loading.value = true
  stepError.value = ''
  try {
    const result = await verifySetup(codeInput.value)
    recoveryCodes.value = result.recovery_codes
    currentStep.value = 'recovery'
    codeInput.value = ''
    await loadStatus()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    stepError.value = err.data?.detail || 'Invalid code. Please try again.'
    codeInput.value = ''
  } finally {
    loading.value = false
  }
}

const startDisable = () => {
  currentStep.value = 'disable'
  codeInput.value = ''
  stepError.value = ''
}

const confirmDisable = async () => {
  if (!codeInput.value) {
    stepError.value = 'Please enter a code'
    return
  }

  loading.value = true
  stepError.value = ''
  try {
    await disable2FA(codeInput.value)
    toast.add({
      title: 'Success',
      description: 'Two-factor authentication has been disabled',
      color: 'green',
    })
    currentStep.value = 'status'
    codeInput.value = ''
    await loadStatus()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    stepError.value = err.data?.detail || 'Invalid code. Please try again.'
    codeInput.value = ''
  } finally {
    loading.value = false
  }
}

const startRegenerate = () => {
  currentStep.value = 'regenerate'
  codeInput.value = ''
  stepError.value = ''
}

const confirmRegenerate = async () => {
  if (!codeInput.value || codeInput.value.length !== 6) {
    stepError.value = 'Please enter a 6-digit TOTP code'
    return
  }

  loading.value = true
  stepError.value = ''
  try {
    const result = await regenerateRecoveryCodes(codeInput.value)
    recoveryCodes.value = result.recovery_codes
    currentStep.value = 'recovery'
    codeInput.value = ''
    await loadStatus()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    stepError.value = err.data?.detail || 'Invalid code. Please try again.'
    codeInput.value = ''
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  currentStep.value = 'status'
  codeInput.value = ''
  stepError.value = ''
  setupData.value = null
  recoveryCodes.value = []
}

onMounted(() => {
  loadStatus()
})
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <!-- Section Header -->
    <div class="px-6 py-4 border-b border-border-gray relative">
      <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
      <h2 class="text-xl font-semibold text-pure-white">Two-Factor Authentication</h2>
      <p class="mt-1 text-sm text-pure-white/60">
        Add an extra layer of security to your account
      </p>
    </div>

    <div class="px-4 sm:px-6 py-6 space-y-4">
      <!-- Status View -->
      <template v-if="currentStep === 'status'">
        <div class="p-4 bg-background-black rounded-lg border border-border-gray">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="status?.enabled ? 'bg-electric-green/20' : 'bg-card-black'"
            >
              <UIcon
                :name="status?.enabled ? 'i-heroicons-shield-check' : 'i-heroicons-shield-exclamation'"
                class="w-5 h-5"
                :class="status?.enabled ? 'text-electric-green' : 'text-pure-white/60'"
              />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-pure-white font-medium">
                {{ status?.enabled ? '2FA Enabled' : '2FA Disabled' }}
              </p>
              <p class="text-sm text-pure-white/60">
                <template v-if="status?.enabled">
                  {{ status.recovery_codes_remaining }} recovery codes remaining
                </template>
                <template v-else>
                  Protect your account with an authenticator app
                </template>
              </p>
            </div>
            <div class="flex-shrink-0">
              <span
                v-if="status?.enabled"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-electric-green/20 text-electric-green"
              >
                Active
              </span>
              <span
                v-else
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-pure-white/10 text-pure-white/60"
              >
                Inactive
              </span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-wrap gap-3">
          <BaseButton
            v-if="!status?.enabled"
            variant="primary"
            icon="i-heroicons-shield-check"
            :loading="loading"
            @click="startSetup"
          >
            Enable 2FA
          </BaseButton>
          <template v-else>
            <BaseButton
              variant="secondary"
              icon="i-heroicons-arrow-path"
              @click="startRegenerate"
            >
              Regenerate Recovery Codes
            </BaseButton>
            <BaseButton
              variant="danger"
              icon="i-heroicons-shield-exclamation"
              @click="startDisable"
            >
              Disable 2FA
            </BaseButton>
          </template>
        </div>
      </template>

      <!-- Setup Flow: QR Code + Manual Secret -->
      <template v-if="currentStep === 'setup'">
        <div class="space-y-5">
          <p class="text-sm text-pure-white/80">
            Scan the QR code below with your authenticator app (Google Authenticator, Authy, etc.),
            then enter the 6-digit code to confirm setup.
          </p>

          <!-- QR Code -->
          <SettingsTwoFactorQRCode v-if="setupData" :value="setupData.uri" />

          <!-- Manual secret -->
          <div v-if="setupData" class="p-3 bg-background-black rounded-lg border border-border-gray">
            <p class="text-xs text-pure-white/60 mb-1">Manual entry key:</p>
            <p class="font-mono text-sm text-pure-white break-all select-all">{{ setupData.secret }}</p>
          </div>

          <!-- Verification input -->
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">
              Verification Code
            </label>
            <input
              v-model="codeInput"
              type="text"
              placeholder="000000"
              maxlength="6"
              autocomplete="one-time-code"
              class="w-full px-4 py-3 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30 text-center text-xl font-mono tracking-widest"
              @keyup.enter="confirmSetup"
            />
            <p v-if="stepError" class="mt-1 text-sm text-danger-red">{{ stepError }}</p>
          </div>

          <div class="flex gap-3">
            <BaseButton variant="ghost" @click="goBack">
              Cancel
            </BaseButton>
            <BaseButton
              variant="primary"
              :loading="loading"
              @click="confirmSetup"
            >
              Verify & Enable
            </BaseButton>
          </div>
        </div>
      </template>

      <!-- Recovery Codes Display -->
      <template v-if="currentStep === 'recovery'">
        <SettingsTwoFactorRecoveryCodes :codes="recoveryCodes" />

        <BaseButton variant="primary" @click="goBack">
          Done
        </BaseButton>
      </template>

      <!-- Disable Confirmation -->
      <template v-if="currentStep === 'disable'">
        <div class="space-y-4">
          <p class="text-sm text-pure-white/80">
            Enter your TOTP code or a recovery code to disable two-factor authentication.
          </p>

          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">
              Verification Code
            </label>
            <input
              v-model="codeInput"
              type="text"
              placeholder="000000 or XXXX-XXXX"
              maxlength="10"
              autocomplete="one-time-code"
              class="w-full px-4 py-3 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30 text-center text-xl font-mono tracking-widest"
              @keyup.enter="confirmDisable"
            />
            <p v-if="stepError" class="mt-1 text-sm text-danger-red">{{ stepError }}</p>
          </div>

          <div class="flex gap-3">
            <BaseButton variant="ghost" @click="goBack">
              Cancel
            </BaseButton>
            <BaseButton
              variant="danger"
              :loading="loading"
              @click="confirmDisable"
            >
              Disable 2FA
            </BaseButton>
          </div>
        </div>
      </template>

      <!-- Regenerate Recovery Codes -->
      <template v-if="currentStep === 'regenerate'">
        <div class="space-y-4">
          <p class="text-sm text-pure-white/80">
            Enter your current TOTP code to generate new recovery codes. This will invalidate all existing recovery codes.
          </p>

          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">
              TOTP Code
            </label>
            <input
              v-model="codeInput"
              type="text"
              placeholder="000000"
              maxlength="6"
              autocomplete="one-time-code"
              class="w-full px-4 py-3 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30 text-center text-xl font-mono tracking-widest"
              @keyup.enter="confirmRegenerate"
            />
            <p v-if="stepError" class="mt-1 text-sm text-danger-red">{{ stepError }}</p>
          </div>

          <div class="flex gap-3">
            <BaseButton variant="ghost" @click="goBack">
              Cancel
            </BaseButton>
            <BaseButton
              variant="primary"
              :loading="loading"
              @click="confirmRegenerate"
            >
              Regenerate Codes
            </BaseButton>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
