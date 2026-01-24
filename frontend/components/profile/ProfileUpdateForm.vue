<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()
const toast = useToast()

const profileForm = ref({
  name: '',
})
const profileLoading = ref(false)
const profileErrors = ref({
  name: '',
  general: '',
})

onMounted(() => {
  if (authStore.user) {
    profileForm.value.name = authStore.user.name
  }
})

watch(() => authStore.user, (user) => {
  if (user) {
    profileForm.value.name = user.name
  }
}, { immediate: true })

const validateProfileForm = (): boolean => {
  profileErrors.value = { name: '', general: '' }

  if (!profileForm.value.name || profileForm.value.name.trim().length < 2) {
    profileErrors.value.name = 'Name must be at least 2 characters'
    return false
  }

  return true
}

const handleUpdateProfile = async () => {
  if (!validateProfileForm()) return

  profileLoading.value = true
  profileErrors.value.general = ''

  try {
    await authStore.updateProfile({
      name: profileForm.value.name.trim(),
    })

    toast.add({
      title: 'Profile updated',
      description: 'Your profile has been updated successfully',
      color: 'green',
    })
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    profileErrors.value.general = err.data?.detail || 'Failed to update profile'
  } finally {
    profileLoading.value = false
  }
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <div class="px-6 py-4 border-b border-border-gray">
      <h2 class="text-xl font-semibold text-pure-white">Update Profile</h2>
      <p class="mt-1 text-sm text-pure-white/60">Update your personal information</p>
    </div>

    <form @submit.prevent="handleUpdateProfile" class="px-6 py-6 space-y-5">
      <!-- General error -->
      <div
        v-if="profileErrors.general"
        class="p-4 bg-danger-red/10 border border-danger-red/30 rounded-lg"
      >
        <div class="flex items-center gap-2 text-danger-red">
          <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 flex-shrink-0" />
          <span class="text-sm">{{ profileErrors.general }}</span>
        </div>
      </div>

      <!-- Name -->
      <div class="max-w-md">
        <label for="profile-name" class="block text-sm font-medium text-pure-white mb-2">
          Name
        </label>
        <input
          id="profile-name"
          v-model="profileForm.name"
          type="text"
          :class="[
            'w-full px-4 py-2.5 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
            profileErrors.name
              ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
              : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30'
          ]"
        />
        <p v-if="profileErrors.name" class="mt-1 text-sm text-danger-red">{{ profileErrors.name }}</p>
      </div>

      <BaseButton
        type="submit"
        variant="primary"
        :loading="profileLoading"
      >
        Save Changes
      </BaseButton>
    </form>
  </div>
</template>
