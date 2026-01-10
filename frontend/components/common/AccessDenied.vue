<script setup lang="ts">
import type { PermissionErrorType } from '~/composables/usePermissions'

interface Props {
  type?: PermissionErrorType
  message?: string
  showHomeButton?: boolean
  showBackButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'not_household_member',
  showHomeButton: true,
  showBackButton: true,
})

const router = useRouter()

const defaultMessages: Record<PermissionErrorType, string> = {
  not_authenticated: 'You must be logged in to access this page',
  not_household_member: 'You are not a member of this household',
  household_access_blocked: 'Your access to this household has been blocked',
  not_household_manager: 'Only household managers can access this page',
  household_not_found: 'This household does not exist',
}

const displayMessage = computed(() => {
  return props.message || defaultMessages[props.type]
})

const iconName = computed(() => {
  switch (props.type) {
    case 'not_authenticated':
      return 'i-heroicons-lock-closed'
    case 'household_access_blocked':
      return 'i-heroicons-no-symbol'
    case 'not_household_manager':
      return 'i-heroicons-shield-exclamation'
    case 'household_not_found':
      return 'i-heroicons-magnifying-glass'
    default:
      return 'i-heroicons-exclamation-triangle'
  }
})

const title = computed(() => {
  switch (props.type) {
    case 'not_authenticated':
      return 'Authentication Required'
    case 'household_access_blocked':
      return 'Access Blocked'
    case 'not_household_manager':
      return 'Manager Access Required'
    case 'household_not_found':
      return 'Not Found'
    default:
      return 'Access Denied'
  }
})

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

const goToLogin = () => {
  const currentPath = router.currentRoute.value.fullPath
  router.push(`/login?redirect=${encodeURIComponent(currentPath)}`)
}
</script>

<template>
  <div class="min-h-[50vh] flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
        <div class="px-6 py-4 border-b border-border-gray relative">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-danger-red" />
          <h1 class="text-xl font-semibold text-pure-white">{{ title }}</h1>
        </div>

        <div class="p-6 text-center">
          <div
            class="w-16 h-16 mx-auto mb-4 rounded-full bg-danger-red/10 border border-danger-red/30 flex items-center justify-center"
          >
            <UIcon :name="iconName" class="w-8 h-8 text-danger-red" />
          </div>

          <p class="text-pure-white/80 mb-6">{{ displayMessage }}</p>

          <div class="space-y-3">
            <BaseButton
              v-if="type === 'not_authenticated'"
              variant="primary"
              class="w-full"
              icon="i-heroicons-arrow-right-on-rectangle"
              @click="goToLogin"
            >
              Go to Login
            </BaseButton>

            <template v-else>
              <BaseButton
                v-if="showHomeButton"
                variant="primary"
                class="w-full"
                icon="i-heroicons-home"
                @click="goHome"
              >
                Go to Home
              </BaseButton>

              <BaseButton
                v-if="showBackButton"
                variant="secondary"
                class="w-full"
                icon="i-heroicons-arrow-left"
                @click="goBack"
              >
                Go Back
              </BaseButton>
            </template>

            <slot name="actions" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
