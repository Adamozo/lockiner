<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: 'guest',
})

const { t } = useI18n()

useSeoMeta({
  title: 'Recover Account - LockIner',
  description: 'Reset your password using your recovery key',
})

const router = useRouter()
const toast = useToast()

const form = ref({
  email: '',
  recoveryKey: '',
  newPassword: '',
  confirmPassword: '',
})
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const errors = ref({
  email: '',
  recoveryKey: '',
  newPassword: '',
  confirmPassword: '',
  general: '',
})
const success = ref(false)

const passwordStrength = computed(() => {
  const password = form.value.newPassword
  if (!password) return { score: 0, label: '', color: '' }

  let score = 0
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
  if (/\d/.test(password)) score++
  if (/[^a-zA-Z0-9]/.test(password)) score++

  if (score <= 1) return { score, label: t('auth.password_strength_weak'), color: 'bg-danger-red' }
  if (score <= 2) return { score, label: t('auth.password_strength_fair'), color: 'bg-warning-orange' }
  if (score <= 3) return { score, label: t('auth.password_strength_good'), color: 'bg-cyber-blue' }
  return { score, label: t('auth.password_strength_strong'), color: 'bg-electric-green' }
})

const validate = (): boolean => {
  errors.value = { email: '', recoveryKey: '', newPassword: '', confirmPassword: '', general: '' }
  let valid = true

  if (!form.value.email) {
    errors.value.email = t('auth.email_required')
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = t('auth.email_invalid')
    valid = false
  }

  if (!form.value.recoveryKey || form.value.recoveryKey.trim().length === 0) {
    errors.value.recoveryKey = t('auth.recovery_key_required')
    valid = false
  } else if (!/^[0-9a-fA-F]{64}$/.test(form.value.recoveryKey.trim())) {
    errors.value.recoveryKey = t('auth.recovery_key_invalid_format')
    valid = false
  }

  if (!form.value.newPassword) {
    errors.value.newPassword = t('auth.password_required')
    valid = false
  } else if (form.value.newPassword.length < 8) {
    errors.value.newPassword = t('auth.password_min')
    valid = false
  }

  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = t('auth.confirm_password_required')
    valid = false
  } else if (form.value.newPassword !== form.value.confirmPassword) {
    errors.value.confirmPassword = t('auth.passwords_mismatch')
    valid = false
  }

  return valid
}

const handleSubmit = async () => {
  if (!validate()) return

  loading.value = true
  errors.value.general = ''

  try {
    const { importDekFromHex, generateSalt, deriveKek, encryptDek } = useDek()

    const dek = await importDekFromHex(form.value.recoveryKey.trim().toLowerCase())
    const newSalt = generateSalt()
    const newKek = await deriveKek(form.value.newPassword, newSalt)
    const newEncryptedDek = await encryptDek(dek, newKek)

    await $fetch('/api/v1/auth/reset-password-with-dek', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        email: form.value.email,
        new_password: form.value.newPassword,
        encrypted_dek: newEncryptedDek,
        dek_salt: newSalt,
      },
    })

    success.value = true
    toast.add({
      title: t('auth.recover_success_title'),
      description: t('auth.recover_success_desc'),
      color: 'green',
    })

    setTimeout(() => router.push('/login'), 2000)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }; statusCode?: number }
    if (err.statusCode === 400) {
      errors.value.email = t('auth.recover_user_not_found')
    } else {
      errors.value.general = err.data?.detail || t('auth.error_generic')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow-xl overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-5 border-b border-border-gray relative">
      <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
      <h1 class="text-2xl font-bold text-pure-white">{{ $t('auth.recover_title') }}</h1>
      <p class="mt-1 text-sm text-pure-white/60">{{ $t('auth.recover_desc') }}</p>
    </div>

    <!-- Success state -->
    <div v-if="success" class="px-6 py-8 text-center space-y-4">
      <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-electric-green mx-auto" />
      <p class="text-pure-white font-medium">{{ $t('auth.recover_success_title') }}</p>
      <p class="text-pure-white/60 text-sm">{{ $t('auth.recover_success_desc') }}</p>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="px-6 py-6 space-y-5">
      <!-- General error -->
      <div
        v-if="errors.general"
        class="p-4 bg-danger-red/10 border border-danger-red/30 rounded-lg"
      >
        <div class="flex items-center gap-2 text-danger-red">
          <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 flex-shrink-0" />
          <span class="text-sm">{{ errors.general }}</span>
        </div>
      </div>

      <!-- Email -->
      <div>
        <label for="email" class="block text-sm font-medium text-pure-white mb-2">
          {{ $t('auth.email') }}
        </label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          autocomplete="email"
          :placeholder="$t('auth.email_placeholder')"
          :class="[
            'w-full px-4 py-2.5 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
            errors.email
              ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
              : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30',
          ]"
        />
        <p v-if="errors.email" class="mt-1 text-sm text-danger-red">{{ errors.email }}</p>
      </div>

      <!-- Recovery Key -->
      <div>
        <label for="recoveryKey" class="block text-sm font-medium text-pure-white mb-2">
          {{ $t('auth.recovery_key_label') }}
        </label>
        <input
          id="recoveryKey"
          v-model="form.recoveryKey"
          type="text"
          autocomplete="off"
          :placeholder="$t('auth.recovery_key_placeholder')"
          :class="[
            'w-full px-4 py-2.5 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors font-mono text-sm',
            errors.recoveryKey
              ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
              : 'border-border-gray focus:border-electric-green focus:ring-electric-green/30',
          ]"
        />
        <p v-if="errors.recoveryKey" class="mt-1 text-sm text-danger-red">{{ errors.recoveryKey }}</p>
        <p v-else class="mt-1 text-xs text-pure-white/40">{{ $t('auth.recovery_key_hint') }}</p>
      </div>

      <!-- New Password -->
      <div>
        <label for="newPassword" class="block text-sm font-medium text-pure-white mb-2">
          {{ $t('auth.recover_new_password') }}
        </label>
        <div class="relative">
          <input
            id="newPassword"
            v-model="form.newPassword"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="new-password"
            :placeholder="$t('auth.password_create_placeholder')"
            :class="[
              'w-full px-4 py-2.5 pr-12 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              errors.newPassword
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30',
            ]"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="showPassword = !showPassword"
          >
            <UIcon :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
          </button>
        </div>
        <p v-if="errors.newPassword" class="mt-1 text-sm text-danger-red">{{ errors.newPassword }}</p>
        <div v-if="form.newPassword" class="mt-2">
          <div class="flex items-center gap-2">
            <div class="flex-1 h-1.5 bg-border-gray rounded-full overflow-hidden">
              <div
                class="h-full transition-all duration-300"
                :class="passwordStrength.color"
                :style="{ width: `${(passwordStrength.score / 5) * 100}%` }"
              />
            </div>
            <span class="text-xs" :class="passwordStrength.color.replace('bg-', 'text-')">
              {{ passwordStrength.label }}
            </span>
          </div>
        </div>
      </div>

      <!-- Confirm Password -->
      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-pure-white mb-2">
          {{ $t('auth.confirm_password') }}
        </label>
        <div class="relative">
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            autocomplete="new-password"
            :placeholder="$t('auth.confirm_password_placeholder')"
            :class="[
              'w-full px-4 py-2.5 pr-12 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              errors.confirmPassword
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30',
            ]"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            <UIcon :name="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
          </button>
        </div>
        <p v-if="errors.confirmPassword" class="mt-1 text-sm text-danger-red">{{ errors.confirmPassword }}</p>
      </div>

      <BaseButton type="submit" variant="primary" :loading="loading" class="w-full">
        {{ $t('auth.recover_submit') }}
      </BaseButton>

      <p class="text-center text-sm text-pure-white/60">
        {{ $t('auth.already_account') }}
        <NuxtLink to="/login" class="text-cyber-blue hover:text-cyber-blue/80 font-medium transition-colors">
          {{ $t('auth.sign_in') }}
        </NuxtLink>
      </p>
    </form>
  </div>
</template>
