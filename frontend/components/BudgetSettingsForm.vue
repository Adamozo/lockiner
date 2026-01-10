<script setup lang="ts">
import { z } from 'zod'
import type { BudgetSettings, BudgetSettingsUpdate } from '~/types/api'

const props = defineProps<{
  settings: BudgetSettings
}>()

const emit = defineEmits<{
  'settings-updated': [settings: BudgetSettings]
}>()

const { updateBudgetSettings } = useAnalytics()
const toast = useToast()

// Form validation schema
const schema = z.object({
  overall_monthly_limit: z.number().positive('Budget must be positive').optional().nullable(),
  alert_threshold_warning: z.number().min(0).max(100),
  alert_threshold_danger: z.number().min(0).max(100),
  enable_alerts: z.boolean(),
})

// Form state
const form = reactive<BudgetSettingsUpdate>({
  overall_monthly_limit: props.settings.overall_monthly_limit,
  alert_threshold_warning: props.settings.alert_threshold_warning,
  alert_threshold_danger: props.settings.alert_threshold_danger,
  enable_alerts: props.settings.enable_alerts,
})

const loading = ref(false)
const errors = ref<Record<string, string>>({})

// Handle form submission
const handleSubmit = async () => {
  errors.value = {}

  try {
    // Validate form
    schema.parse(form)

    loading.value = true

    // Update settings
    const updated = await updateBudgetSettings(form)

    toast.add({
      title: 'Success',
      description: 'Budget settings updated successfully',
      color: 'green',
    })

    emit('settings-updated', updated)
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.errors.forEach((err) => {
        if (err.path[0]) {
          errors.value[err.path[0] as string] = err.message
        }
      })
    } else {
      toast.add({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to update settings',
        color: 'red',
      })
    }
  } finally {
    loading.value = false
  }
}

// Watch for prop changes
watch(
  () => props.settings,
  (newSettings) => {
    form.overall_monthly_limit = newSettings.overall_monthly_limit
    form.alert_threshold_warning = newSettings.alert_threshold_warning
    form.alert_threshold_danger = newSettings.alert_threshold_danger
    form.enable_alerts = newSettings.enable_alerts
  }
)
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Overall Monthly Limit -->
    <div>
      <label for="overall_limit" class="block text-sm font-medium text-pure-white mb-2">
        Overall Monthly Budget Limit (PLN)
      </label>
      <input
        id="overall_limit"
        v-model.number="form.overall_monthly_limit"
        type="number"
        step="0.01"
        min="0"
        placeholder="e.g., 5000.00"
        class="block w-full rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 px-4 py-3 transition-all duration-300 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
        :class="{ 'border-danger-red': errors.overall_monthly_limit }"
      />
      <p class="mt-2 text-xs text-pure-white/60">
        Total spending limit across all categories for the month. Leave empty for no limit.
      </p>
      <p v-if="errors.overall_monthly_limit" class="mt-1 text-sm text-danger-red">
        {{ errors.overall_monthly_limit }}
      </p>
    </div>

    <!-- Alert Thresholds -->
    <div class="bg-card-black/50 border border-border-gray rounded-lg p-4 space-y-4">
      <h4 class="text-sm font-semibold text-pure-white flex items-center gap-2">
        <UIcon name="i-heroicons-bell" class="w-4 h-4" />
        Alert Thresholds
      </h4>

      <!-- Warning Threshold -->
      <div>
        <label for="warning_threshold" class="block text-sm font-medium text-pure-white mb-2">
          Warning Threshold (%)
        </label>
        <div class="flex items-center gap-3">
          <input
            id="warning_threshold"
            v-model.number="form.alert_threshold_warning"
            type="range"
            min="0"
            max="100"
            step="5"
            class="flex-1 h-2 bg-card-black rounded-lg appearance-none cursor-pointer accent-warning-orange"
          />
          <span class="text-warning-orange font-semibold min-w-[3rem] text-right">
            {{ form.alert_threshold_warning }}%
          </span>
        </div>
        <p class="mt-1 text-xs text-pure-white/60">
          Show warning when spending reaches this percentage
        </p>
      </div>

      <!-- Danger Threshold -->
      <div>
        <label for="danger_threshold" class="block text-sm font-medium text-pure-white mb-2">
          Danger Threshold (%)
        </label>
        <div class="flex items-center gap-3">
          <input
            id="danger_threshold"
            v-model.number="form.alert_threshold_danger"
            type="range"
            min="0"
            max="150"
            step="5"
            class="flex-1 h-2 bg-card-black rounded-lg appearance-none cursor-pointer accent-danger-red"
          />
          <span class="text-danger-red font-semibold min-w-[3rem] text-right">
            {{ form.alert_threshold_danger }}%
          </span>
        </div>
        <p class="mt-1 text-xs text-pure-white/60">
          Show danger alert when spending reaches this percentage
        </p>
      </div>
    </div>

    <!-- Enable Alerts Toggle -->
    <div class="flex items-center justify-between p-4 bg-card-black/50 border border-border-gray rounded-lg">
      <div>
        <p class="text-sm font-medium text-pure-white">Enable Budget Alerts</p>
        <p class="text-xs text-pure-white/60 mt-1">
          Receive notifications when approaching or exceeding budget limits
        </p>
      </div>
      <label class="relative inline-flex items-center cursor-pointer">
        <input v-model="form.enable_alerts" type="checkbox" class="sr-only peer" />
        <div
          class="w-11 h-6 bg-card-black peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyber-blue/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-electric-green"
        ></div>
      </label>
    </div>

    <!-- Submit Button -->
    <div class="flex justify-end">
      <BaseButton type="submit" variant="primary" :loading="loading" class="min-w-[150px]">
        Save Settings
      </BaseButton>
    </div>
  </form>
</template>
