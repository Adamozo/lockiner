<script setup lang="ts">
const { isInstallable, isInstalled, isDismissed, installApp, dismissInstall } = usePWAInstall()

const showBanner = computed(() => {
  return isInstallable.value && !isInstalled.value && !isDismissed.value
})

const handleInstall = async () => {
  await installApp()
}
</script>

<template>
  <Transition name="slide-up">
    <div
      v-if="showBanner"
      class="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-4 md:max-w-md"
    >
      <div
        class="bg-card-dark border border-border-gray rounded-xl shadow-lg overflow-hidden"
      >
        <div class="p-4">
          <div class="flex items-start gap-3">
            <div
              class="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-green flex items-center justify-center flex-shrink-0"
            >
              <UIcon name="i-heroicons-arrow-down-tray" class="w-6 h-6 text-background-black" />
            </div>

            <div class="flex-1 min-w-0">
              <h3 class="text-base font-semibold text-pure-white">
                Install LockIner
              </h3>
              <p class="text-sm text-text-gray mt-1">
                Add to your home screen for quick access and offline use.
              </p>
            </div>
          </div>

          <div class="flex items-center gap-3 mt-4">
            <button
              @click="dismissInstall"
              class="flex-1 px-4 py-2 text-sm font-medium text-text-gray hover:text-pure-white transition-colors rounded-lg hover:bg-pure-white/5"
            >
              Not Now
            </button>
            <button
              @click="handleInstall"
              class="flex-1 px-4 py-2 text-sm font-medium text-background-black bg-gradient-to-r from-accent-cyan to-accent-green rounded-lg hover:opacity-90 transition-opacity"
            >
              Install
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
