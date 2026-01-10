<script setup lang="ts">
import type { BudgetAlert } from '~/types/api'

const props = defineProps<{
  alerts: BudgetAlert[]
}>()

const emit = defineEmits<{
  dismiss: []
}>()

const showBanner = ref(true)

const dismissBanner = () => {
  showBanner.value = false
  emit('dismiss')
}

// Auto-show when alerts change
watch(
  () => props.alerts,
  () => {
    if (props.alerts.length > 0) {
      showBanner.value = true
    }
  }
)

const criticalCount = computed(() => props.alerts.filter((a) => a.severity === 'over').length)

const warningCount = computed(() => props.alerts.filter((a) => a.severity === 'warning').length)
</script>

<template>
  <Transition name="slide-down">
    <div
      v-if="showBanner && alerts.length > 0"
      class="mb-6 bg-gradient-to-r from-danger-red/20 to-warning-orange/20 border-l-4 rounded-lg overflow-hidden"
      :class="criticalCount > 0 ? 'border-danger-red' : 'border-warning-orange'"
    >
      <div class="p-4 flex items-start justify-between gap-4">
        <div class="flex items-start gap-3 flex-1">
          <UIcon
            :name="
              criticalCount > 0 ? 'i-heroicons-exclamation-circle' : 'i-heroicons-exclamation-triangle'
            "
            class="w-6 h-6 flex-shrink-0 mt-0.5"
            :class="criticalCount > 0 ? 'text-danger-red' : 'text-warning-orange'"
          />

          <div class="flex-1">
            <h3 class="text-lg font-semibold text-pure-white mb-2">
              Budget Alerts
              <span class="ml-2 text-sm font-normal text-pure-white/60">
                ({{ criticalCount }} critical, {{ warningCount }} warning)
              </span>
            </h3>

            <div class="space-y-2">
              <div v-for="(alert, index) in alerts" :key="index" class="flex items-start gap-2 text-sm">
                <CategoryIcon
                  v-if="alert.icon"
                  :icon="alert.icon"
                  :size="18"
                  :color="alert.color || (alert.severity === 'over' ? '#ff4757' : '#ffa502')"
                  class="flex-shrink-0 mt-0.5"
                />
                <UIcon
                  v-else
                  :name="alert.severity === 'over' ? 'i-heroicons-x-circle' : 'i-heroicons-exclamation-triangle'"
                  class="w-4 h-4 flex-shrink-0 mt-0.5"
                  :class="alert.severity === 'over' ? 'text-danger-red' : 'text-warning-orange'"
                />
                <p class="text-pure-white/90">{{ alert.message }}</p>
              </div>
            </div>
          </div>
        </div>

        <button
          @click="dismissBanner"
          class="text-pure-white/60 hover:text-pure-white transition-colors flex-shrink-0"
        >
          <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
        </button>
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
  transform: translateY(-20px);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>
