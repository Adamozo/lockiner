<script setup lang="ts">
definePageMeta({
  layout: false,
})

const { isOnline } = useNetworkStatus()

const retry = () => {
  if (isOnline.value) {
    navigateTo('/')
  } else {
    window.location.reload()
  }
}
</script>

<template>
  <div class="min-h-screen bg-background-black flex items-center justify-center p-4">
    <div class="max-w-md w-full text-center">
      <div
        class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-card-dark border border-border-gray flex items-center justify-center"
      >
        <UIcon
          :name="isOnline ? 'i-heroicons-wifi' : 'i-heroicons-signal-slash'"
          class="w-10 h-10"
          :class="isOnline ? 'text-accent-green' : 'text-text-gray'"
        />
      </div>

      <h1 class="text-2xl font-bold text-pure-white mb-2">
        {{ isOnline ? 'Back Online' : 'You\'re Offline' }}
      </h1>

      <p class="text-text-gray mb-8">
        {{
          isOnline
            ? 'Your connection has been restored. You can continue using LockIner.'
            : 'Check your internet connection and try again. Some features may still be available offline.'
        }}
      </p>

      <button
        @click="retry"
        class="inline-flex items-center gap-2 px-6 py-3 text-sm font-medium rounded-lg transition-all"
        :class="
          isOnline
            ? 'text-background-black bg-gradient-to-r from-accent-cyan to-accent-green hover:opacity-90'
            : 'text-pure-white bg-card-dark border border-border-gray hover:border-text-gray'
        "
      >
        <UIcon
          :name="isOnline ? 'i-heroicons-home' : 'i-heroicons-arrow-path'"
          class="w-5 h-5"
        />
        {{ isOnline ? 'Go to Home' : 'Try Again' }}
      </button>

      <div
        v-if="!isOnline"
        class="mt-8 p-4 bg-card-dark border border-border-gray rounded-xl text-left"
      >
        <h2 class="text-sm font-semibold text-pure-white mb-2">
          While offline, you can:
        </h2>
        <ul class="text-sm text-text-gray space-y-1">
          <li class="flex items-center gap-2">
            <UIcon name="i-heroicons-check" class="w-4 h-4 text-accent-green" />
            View cached transactions
          </li>
          <li class="flex items-center gap-2">
            <UIcon name="i-heroicons-check" class="w-4 h-4 text-accent-green" />
            Browse cached analytics
          </li>
          <li class="flex items-center gap-2">
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-danger-red" />
            Add new transactions
          </li>
          <li class="flex items-center gap-2">
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4 text-danger-red" />
            Upload receipts
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
