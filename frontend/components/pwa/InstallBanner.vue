<script setup lang="ts">
const { isInstallable, isInstalled, isIOSSafari, isDismissed, installApp, dismissInstall } = usePWAInstall()

const showBanner = computed(() => {
  if (isInstalled.value || isDismissed.value) return false
  return isInstallable.value || isIOSSafari.value || !isInstalled.value
})

const isInstalling = ref(false)

const handleInstall = async () => {
  if (!isInstallable.value) return
  isInstalling.value = true
  try {
    await installApp()
  } finally {
    isInstalling.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="slide-down">
      <div
        v-if="showBanner"
        class="fixed top-4 left-4 right-4 z-50 flex justify-center"
      >
        <div
          class="w-full max-w-md rounded-xl overflow-hidden shadow-2xl shadow-cyber-blue/10"
          style="padding: 1px; background: linear-gradient(135deg, #00D4FF, #00FF88, #00D4FF)"
        >
          <div class="bg-card-black rounded-xl p-4">
            <div class="flex items-start gap-3">
              <div
                class="w-10 h-10 rounded-lg bg-gradient-to-br from-cyber-blue/20 to-electric-green/20 flex items-center justify-center flex-shrink-0"
              >
                <UIcon name="i-heroicons-device-phone-mobile" class="w-5 h-5 text-cyber-blue" />
              </div>

              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold text-pure-white">
                  Install LockIner
                </h3>

                <p v-if="isInstallable" class="text-xs text-pure-white/50 mt-0.5">
                  Get faster access, offline mode & push notifications
                </p>
                <p v-else-if="isIOSSafari" class="text-xs text-pure-white/50 mt-0.5">
                  Tap
                  <UIcon name="i-heroicons-arrow-up-on-square" class="inline w-3.5 h-3.5 text-cyber-blue align-text-bottom" />
                  Share, then <span class="text-pure-white/70 font-medium">Add to Home Screen</span>
                </p>
                <p v-else class="text-xs text-pure-white/50 mt-0.5">
                  Use <span class="text-pure-white/70 font-medium">Chrome</span> (Android) or <span class="text-pure-white/70 font-medium">Safari</span> (iOS) to install
                </p>
              </div>

            </div>

            <div class="flex items-center gap-2 mt-3">
              <button
                @click="dismissInstall"
                class="flex-1 px-4 py-2 text-sm font-medium text-pure-white/50 hover:text-pure-white rounded-lg border border-border-gray hover:border-pure-white/30 transition-colors"
              >
                Not Now
              </button>
              <button
                @click="handleInstall"
                :disabled="isInstalling || !isInstallable"
                class="flex-1 px-4 py-2 text-sm font-semibold rounded-lg flex items-center justify-center gap-2 transition-opacity"
                :class="isInstallable
                  ? 'text-background-black bg-gradient-to-r from-cyber-blue to-electric-green hover:opacity-90'
                  : 'text-pure-white/30 bg-pure-white/5 cursor-not-allowed'"
                :title="!isInstallable ? 'Installation not available in this browser. Try Chrome on Android or Safari on iOS.' : undefined"
              >
                <UIcon
                  v-if="isInstalling"
                  name="i-heroicons-arrow-path"
                  class="w-4 h-4 animate-spin"
                />
                <UIcon
                  v-else
                  name="i-heroicons-arrow-down-tray"
                  class="w-4 h-4"
                />
                {{ isInstalling ? 'Installing...' : 'Install App' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
