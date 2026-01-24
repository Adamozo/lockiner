<script setup lang="ts">
const { needRefresh, refreshApp } = usePWAInstall()

const isUpdating = ref(false)

const handleUpdate = async () => {
  isUpdating.value = true
  try {
    await refreshApp()
    // Reload the page to apply updates
    window.location.reload()
  } catch {
    isUpdating.value = false
  }
}

const dismissUpdate = () => {
  needRefresh.value = false
}
</script>

<template>
  <Transition name="slide-down">
    <div
      v-if="needRefresh"
      class="fixed top-4 left-4 right-4 z-50 md:left-auto md:right-4 md:max-w-md"
    >
      <div
        class="bg-card-dark border border-accent-cyan/30 rounded-xl shadow-lg overflow-hidden"
      >
        <div class="p-4">
          <div class="flex items-start gap-3">
            <div
              class="w-10 h-10 rounded-lg bg-accent-cyan/20 flex items-center justify-center flex-shrink-0"
            >
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 text-accent-cyan" />
            </div>

            <div class="flex-1 min-w-0">
              <h3 class="text-base font-semibold text-pure-white">
                Update Available
              </h3>
              <p class="text-sm text-text-gray mt-1">
                A new version of LockIner is ready. Update now for the latest features.
              </p>
            </div>

            <button
              @click="dismissUpdate"
              class="text-text-gray hover:text-pure-white transition-colors flex-shrink-0"
            >
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
            </button>
          </div>

          <div class="mt-4">
            <button
              @click="handleUpdate"
              :disabled="isUpdating"
              class="w-full px-4 py-2 text-sm font-medium text-background-black bg-gradient-to-r from-accent-cyan to-accent-green rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <UIcon
                v-if="isUpdating"
                name="i-heroicons-arrow-path"
                class="w-4 h-4 animate-spin"
              />
              {{ isUpdating ? 'Updating...' : 'Update Now' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
