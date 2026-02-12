<script setup lang="ts">
import type { NotificationSchedule, Frequency } from '~/composables/useNotificationSchedules'

const props = defineProps<{
  schedule: NotificationSchedule
  disabled: boolean
}>()

const emit = defineEmits<{
  'update:schedule': [schedule: NotificationSchedule]
  'delete': []
}>()

const local = computed(() => props.schedule)

const isCustom = computed(() => props.schedule.reminder_type.startsWith('custom_'))

const reminderConfig: Record<string, { label: string; icon: string; color: string }> = {
  workout: { label: 'Workout Reminder', icon: 'i-heroicons-fire', color: 'text-warning-orange' },
  weight: { label: 'Weight Reminder', icon: 'i-heroicons-scale', color: 'text-cyber-blue' },
  receipt: { label: 'Receipt Reminder', icon: 'i-heroicons-receipt-percent', color: 'text-electric-green' },
  finance: { label: 'Finance Reminder', icon: 'i-heroicons-banknotes', color: 'text-electric-green' },
}

const config = computed(() => {
  if (isCustom.value && props.schedule.custom_name) {
    return {
      label: props.schedule.custom_name,
      icon: props.schedule.custom_icon || 'i-heroicons-bell',
      color: 'text-warning-orange',
    }
  }
  return reminderConfig[props.schedule.reminder_type] ?? {
    label: props.schedule.reminder_type,
    icon: 'i-heroicons-bell',
    color: 'text-pure-white',
  }
})

const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const frequencyLabels: Frequency[] = ['daily', 'weekly', 'monthly']
const frequencyDisplay: Record<string, string> = { daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly' }

function patch(fields: Partial<NotificationSchedule>) {
  emit('update:schedule', { ...props.schedule, ...fields })
}

const onToggle = () => patch({ enabled: !local.value.enabled })

// Wrap-around stepper helpers
function stepHour(dir: number) {
  patch({ hour: (local.value.hour + dir + 24) % 24 })
}
function stepMinute(dir: number) {
  patch({ minute: (local.value.minute + dir * 5 + 60) % 60 })
}
function stepDayOfWeek(dir: number) {
  const cur = local.value.day_of_week ?? 0
  patch({ day_of_week: (cur + dir + 7) % 7 })
}
function stepDayOfMonth(dir: number) {
  const cur = local.value.day_of_month ?? 1
  // Wrap 1-31
  const next = ((cur - 1 + dir + 31) % 31) + 1
  patch({ day_of_month: next })
}
function stepFrequency(dir: number) {
  const idx = frequencyLabels.indexOf(local.value.frequency)
  const next = frequencyLabels[(idx + dir + frequencyLabels.length) % frequencyLabels.length]
  const updates: Partial<NotificationSchedule> = { frequency: next }
  if (next === 'daily') {
    updates.day_of_week = null
    updates.day_of_month = null
  } else if (next === 'weekly') {
    updates.day_of_month = null
    if (local.value.day_of_week == null) updates.day_of_week = 0
  } else if (next === 'monthly') {
    updates.day_of_week = null
    if (local.value.day_of_month == null) updates.day_of_month = 1
  }
  patch(updates)
}

const btnBase = 'w-7 h-7 flex items-center justify-center rounded border border-border-gray text-pure-white/60 hover:text-pure-white hover:border-pure-white/40 hover:bg-white/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed'
</script>

<template>
  <div class="p-4 bg-background-black rounded-lg border border-border-gray">
    <!-- Header row: icon + label + delete (custom only) + toggle -->
    <div class="flex items-center gap-3">
      <div
        class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
        :class="local.enabled ? 'bg-warning-orange/20' : 'bg-card-black'"
      >
        <UIcon
          :name="config.icon"
          class="w-5 h-5"
          :class="local.enabled ? config.color : 'text-pure-white/40'"
        />
      </div>

      <div class="flex-1 min-w-0">
        <p class="text-pure-white font-medium text-sm">{{ config.label }}</p>
      </div>

      <!-- Delete button for custom reminders -->
      <button
        v-if="isCustom"
        type="button"
        :disabled="disabled"
        class="p-1.5 rounded text-pure-white/40 hover:text-danger-red hover:bg-danger-red/10 transition-colors disabled:opacity-30"
        title="Delete reminder"
        @click="emit('delete')"
      >
        <UIcon name="i-heroicons-trash" class="w-4 h-4" />
      </button>

      <button
        type="button"
        :disabled="disabled"
        class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-warning-orange/50"
        :class="local.enabled ? 'bg-warning-orange' : 'bg-border-gray'"
        @click="onToggle"
      >
        <span
          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200"
          :class="local.enabled ? 'translate-x-5' : 'translate-x-0'"
        />
      </button>
    </div>

    <!-- Schedule config row (only when enabled) -->
    <div v-if="local.enabled" class="mt-3 ml-12 flex flex-wrap items-center gap-x-2 gap-y-2 text-sm text-pure-white/70">
      <!-- Frequency -->
      <div class="inline-flex items-center gap-1">
        <button :class="btnBase" :disabled="disabled" @click="stepFrequency(-1)">
          <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
        </button>
        <span class="w-16 text-center text-pure-white font-medium">{{ frequencyDisplay[local.frequency] }}</span>
        <button :class="btnBase" :disabled="disabled" @click="stepFrequency(1)">
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
        </button>
      </div>

      <!-- Day of week (weekly) -->
      <template v-if="local.frequency === 'weekly'">
        <span>every</span>
        <div class="inline-flex items-center gap-1">
          <button :class="btnBase" :disabled="disabled" @click="stepDayOfWeek(-1)">
            <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
          </button>
          <span class="w-10 text-center text-pure-white font-medium">{{ dayLabels[local.day_of_week ?? 0] }}</span>
          <button :class="btnBase" :disabled="disabled" @click="stepDayOfWeek(1)">
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
          </button>
        </div>
      </template>

      <!-- Day of month (monthly) -->
      <template v-if="local.frequency === 'monthly'">
        <span>on day</span>
        <div class="inline-flex items-center gap-1">
          <button :class="btnBase" :disabled="disabled" @click="stepDayOfMonth(-1)">
            <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
          </button>
          <span class="w-8 text-center text-pure-white font-medium">{{ local.day_of_month ?? 1 }}</span>
          <button :class="btnBase" :disabled="disabled" @click="stepDayOfMonth(1)">
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
          </button>
        </div>
      </template>

      <span>at</span>

      <!-- Hour -->
      <div class="inline-flex items-center gap-1">
        <button :class="btnBase" :disabled="disabled" @click="stepHour(-1)">
          <UIcon name="i-heroicons-minus-small" class="w-4 h-4" />
        </button>
        <span class="w-8 text-center text-pure-white font-medium">{{ String(local.hour).padStart(2, '0') }}</span>
        <button :class="btnBase" :disabled="disabled" @click="stepHour(1)">
          <UIcon name="i-heroicons-plus-small" class="w-4 h-4" />
        </button>
      </div>

      <span class="text-pure-white font-medium">:</span>

      <!-- Minute -->
      <div class="inline-flex items-center gap-1">
        <button :class="btnBase" :disabled="disabled" @click="stepMinute(-1)">
          <UIcon name="i-heroicons-minus-small" class="w-4 h-4" />
        </button>
        <span class="w-8 text-center text-pure-white font-medium">{{ String(local.minute).padStart(2, '0') }}</span>
        <button :class="btnBase" :disabled="disabled" @click="stepMinute(1)">
          <UIcon name="i-heroicons-plus-small" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
