<script setup lang="ts">
import { useInvitations } from '~/composables/useInvitations'
import { useAuthStore } from '~/stores/auth'
import type { InvitationPreview } from '~/types/api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const token = computed(() => route.params.token as string)

const { getInvitationPreview, joinHousehold, loading, error } = useInvitations()

const invitation = ref<InvitationPreview | null>(null)
const loadingPreview = ref(true)
const previewError = ref<string | null>(null)
const joining = ref(false)

// Fetch invitation preview on mount
onMounted(async () => {
  try {
    invitation.value = await getInvitationPreview(token.value)
  } catch {
    previewError.value = error.value
  } finally {
    loadingPreview.value = false
  }
})

// Update SEO
watchEffect(() => {
  if (invitation.value) {
    useSeoMeta({
      title: `Join ${invitation.value.household_name} - LockIner`,
      description: `You've been invited to join ${invitation.value.household_name}`,
    })
  } else {
    useSeoMeta({
      title: 'Join Household - LockIner',
      description: 'Accept an invitation to join a household',
    })
  }
})

// Handle join
const handleJoin = async () => {
  if (!authStore.isLoggedIn) {
    // Redirect to login with return URL
    const returnUrl = encodeURIComponent(route.fullPath)
    await router.push(`/login?redirect=${returnUrl}`)
    return
  }

  joining.value = true

  try {
    const result = await joinHousehold(token.value)

    toast.add({
      title: 'Welcome!',
      description: `You've joined ${result.household_name}`,
      color: 'green',
    })

    // Redirect to the household page
    await router.push(`/households/${result.household_uid}`)
  } catch {
    toast.add({
      title: 'Error',
      description: error.value || 'Failed to join household',
      color: 'red',
    })
  } finally {
    joining.value = false
  }
}

// Redirect to login
const redirectToLogin = () => {
  const returnUrl = encodeURIComponent(route.fullPath)
  router.push(`/login?redirect=${returnUrl}`)
}
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Loading state -->
      <div v-if="loadingPreview" class="text-center py-12">
        <div class="w-12 h-12 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p class="text-pure-white/60">Loading invitation...</p>
      </div>

      <!-- Error state -->
      <div
        v-else-if="previewError"
        class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-border-gray relative">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-danger-red" />
          <h1 class="text-xl font-semibold text-pure-white">Invitation Unavailable</h1>
        </div>

        <div class="p-6 text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-danger-red/10 border border-danger-red/30 flex items-center justify-center">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-danger-red" />
          </div>

          <p class="text-pure-white/80 mb-6">{{ previewError }}</p>

          <div class="space-y-3">
            <NuxtLink to="/households">
              <BaseButton variant="primary" class="w-full">
                Go to Households
              </BaseButton>
            </NuxtLink>

            <NuxtLink to="/">
              <BaseButton variant="secondary" class="w-full">
                Go to Home
              </BaseButton>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Invitation preview -->
      <div
        v-else-if="invitation"
        class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-border-gray relative">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
          <h1 class="text-xl font-semibold text-pure-white">You're Invited!</h1>
        </div>

        <div class="p-6">
          <!-- Household info -->
          <div class="text-center mb-8">
            <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-cyber-blue/10 border border-cyber-blue/30 flex items-center justify-center">
              <span v-if="invitation.household_icon" class="text-4xl">{{ invitation.household_icon }}</span>
              <UIcon v-else name="i-heroicons-home" class="w-10 h-10 text-cyber-blue" />
            </div>

            <h2 class="text-2xl font-bold text-pure-white mb-2">
              {{ invitation.household_name }}
            </h2>

            <p class="text-pure-white/60">
              You've been invited to join this household
            </p>
          </div>

          <!-- Invitation details -->
          <div class="bg-background-black border border-border-gray rounded-lg p-4 mb-6">
            <div class="flex items-center justify-between text-sm">
              <span class="text-pure-white/40">Created by</span>
              <span class="text-pure-white">{{ invitation.created_by_name }}</span>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="space-y-3">
            <BaseButton
              v-if="authStore.isLoggedIn"
              variant="primary"
              class="w-full"
              icon="i-heroicons-user-plus"
              :loading="joining"
              @click="handleJoin"
            >
              Join Household
            </BaseButton>

            <template v-else>
              <BaseButton
                variant="primary"
                class="w-full"
                icon="i-heroicons-arrow-right-on-rectangle"
                @click="redirectToLogin"
              >
                Login to Join
              </BaseButton>

              <p class="text-center text-sm text-pure-white/40">
                You need to be logged in to join a household
              </p>

              <div class="text-center text-sm">
                <span class="text-pure-white/40">Don't have an account? </span>
                <NuxtLink
                  :to="`/register?redirect=${encodeURIComponent(route.fullPath)}`"
                  class="text-cyber-blue hover:text-cyber-blue/80"
                >
                  Register
                </NuxtLink>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
