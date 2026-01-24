<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()
const toast = useToast()

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const passwordLoading = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const passwordErrors = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
  general: '',
})

const passwordStrength = computed(() => {
  const password = passwordForm.value.newPassword
  if (!password) return { score: 0, label: '', color: '' }

  let score = 0
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
  if (/\d/.test(password)) score++
  if (/[^a-zA-Z0-9]/.test(password)) score++

  if (score <= 1) return { score, label: 'Weak', color: 'bg-danger-red' }
  if (score <= 2) return { score, label: 'Fair', color: 'bg-warning-orange' }
  if (score <= 3) return { score, label: 'Good', color: 'bg-cyber-blue' }
  return { score, label: 'Strong', color: 'bg-electric-green' }
})

const validatePasswordForm = (): boolean => {
  passwordErrors.value = { currentPassword: '', newPassword: '', confirmPassword: '', general: '' }
  let valid = true

  if (!passwordForm.value.currentPassword) {
    passwordErrors.value.currentPassword = 'Current password is required'
    valid = false
  }

  if (!passwordForm.value.newPassword) {
    passwordErrors.value.newPassword = 'New password is required'
    valid = false
  } else if (passwordForm.value.newPassword.length < 8) {
    passwordErrors.value.newPassword = 'Password must be at least 8 characters'
    valid = false
  }

  if (!passwordForm.value.confirmPassword) {
    passwordErrors.value.confirmPassword = 'Please confirm your new password'
    valid = false
  } else if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordErrors.value.confirmPassword = 'Passwords do not match'
    valid = false
  }

  return valid
}

const handleChangePassword = async () => {
  if (!validatePasswordForm()) return

  passwordLoading.value = true
  passwordErrors.value.general = ''

  try {
    await authStore.changePassword({
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword,
    })

    toast.add({
      title: 'Password changed',
      description: 'Your password has been changed successfully',
      color: 'green',
    })

    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    }
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }, statusCode?: number }

    if (err.statusCode === 400 || err.statusCode === 401) {
      passwordErrors.value.currentPassword = 'Current password is incorrect'
    } else {
      passwordErrors.value.general = err.data?.detail || 'Failed to change password'
    }
  } finally {
    passwordLoading.value = false
  }
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <div class="px-6 py-4 border-b border-border-gray">
      <h2 class="text-xl font-semibold text-pure-white">Change Password</h2>
      <p class="mt-1 text-sm text-pure-white/60">Update your password to keep your account secure</p>
    </div>

    <form @submit.prevent="handleChangePassword" class="px-6 py-6 space-y-5">
      <!-- General error -->
      <div
        v-if="passwordErrors.general"
        class="p-4 bg-danger-red/10 border border-danger-red/30 rounded-lg"
      >
        <div class="flex items-center gap-2 text-danger-red">
          <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 flex-shrink-0" />
          <span class="text-sm">{{ passwordErrors.general }}</span>
        </div>
      </div>

      <!-- Current Password -->
      <div class="max-w-md">
        <label for="current-password" class="block text-sm font-medium text-pure-white mb-2">
          Current Password
        </label>
        <div class="relative">
          <input
            id="current-password"
            v-model="passwordForm.currentPassword"
            :type="showCurrentPassword ? 'text' : 'password'"
            autocomplete="current-password"
            :class="[
              'w-full px-4 py-2.5 pr-12 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              passwordErrors.currentPassword
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30'
            ]"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="showCurrentPassword = !showCurrentPassword"
          >
            <UIcon
              :name="showCurrentPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
              class="w-5 h-5"
            />
          </button>
        </div>
        <p v-if="passwordErrors.currentPassword" class="mt-1 text-sm text-danger-red">{{ passwordErrors.currentPassword }}</p>
      </div>

      <!-- New Password -->
      <div class="max-w-md">
        <label for="new-password" class="block text-sm font-medium text-pure-white mb-2">
          New Password
        </label>
        <div class="relative">
          <input
            id="new-password"
            v-model="passwordForm.newPassword"
            :type="showNewPassword ? 'text' : 'password'"
            autocomplete="new-password"
            :class="[
              'w-full px-4 py-2.5 pr-12 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              passwordErrors.newPassword
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30'
            ]"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="showNewPassword = !showNewPassword"
          >
            <UIcon
              :name="showNewPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
              class="w-5 h-5"
            />
          </button>
        </div>
        <p v-if="passwordErrors.newPassword" class="mt-1 text-sm text-danger-red">{{ passwordErrors.newPassword }}</p>

        <!-- Password strength indicator -->
        <div v-if="passwordForm.newPassword" class="mt-2">
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

      <!-- Confirm New Password -->
      <div class="max-w-md">
        <label for="confirm-new-password" class="block text-sm font-medium text-pure-white mb-2">
          Confirm New Password
        </label>
        <div class="relative">
          <input
            id="confirm-new-password"
            v-model="passwordForm.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            autocomplete="new-password"
            :class="[
              'w-full px-4 py-2.5 pr-12 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              passwordErrors.confirmPassword
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30'
            ]"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            <UIcon
              :name="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
              class="w-5 h-5"
            />
          </button>
        </div>
        <p v-if="passwordErrors.confirmPassword" class="mt-1 text-sm text-danger-red">{{ passwordErrors.confirmPassword }}</p>
      </div>

      <BaseButton
        type="submit"
        variant="primary"
        :loading="passwordLoading"
      >
        Change Password
      </BaseButton>
    </form>
  </div>
</template>
