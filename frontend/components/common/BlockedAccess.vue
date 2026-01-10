<script setup lang="ts">
interface Props {
  householdName?: string
}

defineProps<Props>()

const router = useRouter()

const goToHouseholds = () => {
  router.push('/households')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-[50vh] flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
        <div class="px-6 py-4 border-b border-border-gray relative">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-danger-red to-orange-500" />
          <h1 class="text-xl font-semibold text-pure-white">Access Blocked</h1>
        </div>

        <div class="p-6 text-center">
          <div
            class="w-20 h-20 mx-auto mb-4 rounded-full bg-danger-red/10 border border-danger-red/30 flex items-center justify-center"
          >
            <UIcon name="i-heroicons-no-symbol" class="w-10 h-10 text-danger-red" />
          </div>

          <h2 class="text-lg font-medium text-pure-white mb-2">
            You've been blocked
          </h2>

          <p class="text-pure-white/60 mb-6">
            <template v-if="householdName">
              Your access to <strong class="text-pure-white">{{ householdName }}</strong> has been blocked by a household manager.
            </template>
            <template v-else>
              Your access to this household has been blocked by a household manager.
            </template>
          </p>

          <div class="bg-background-black border border-border-gray rounded-lg p-4 mb-6 text-left">
            <h3 class="text-sm font-medium text-pure-white/80 mb-2">What does this mean?</h3>
            <ul class="text-sm text-pure-white/60 space-y-1">
              <li class="flex items-start gap-2">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-danger-red mt-0.5 flex-shrink-0" />
                <span>You cannot view household transactions or receipts</span>
              </li>
              <li class="flex items-start gap-2">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-danger-red mt-0.5 flex-shrink-0" />
                <span>You cannot add new entries to this household</span>
              </li>
              <li class="flex items-start gap-2">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-danger-red mt-0.5 flex-shrink-0" />
                <span>You cannot view household analytics</span>
              </li>
              <li class="flex items-start gap-2">
                <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green mt-0.5 flex-shrink-0" />
                <span>You can still leave the household</span>
              </li>
            </ul>
          </div>

          <p class="text-sm text-pure-white/40 mb-6">
            If you believe this is a mistake, please contact a household manager.
          </p>

          <div class="space-y-3">
            <BaseButton
              variant="primary"
              class="w-full"
              icon="i-heroicons-home"
              @click="goToHouseholds"
            >
              My Households
            </BaseButton>

            <BaseButton
              variant="secondary"
              class="w-full"
              icon="i-heroicons-arrow-left"
              @click="goHome"
            >
              Go to Home
            </BaseButton>

            <slot name="actions" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
