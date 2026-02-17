<script setup lang="ts">
import type { MedicineSchedule, MedicineScheduleCreate } from '~/types/medicine'

const props = defineProps<{
  schedule?: MedicineSchedule
}>()

const emit = defineEmits<{
  save: [data: MedicineScheduleCreate]
  cancel: []
}>()

type FrequencyType = 'daily' | 'every_n_days' | 'weekly' | 'monthly'

const FREQUENCY_OPTIONS: { value: FrequencyType; label: string }[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'every_n_days', label: 'Every N days' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
]

const DAY_OPTIONS = [
  { value: 0, label: 'Mon' },
  { value: 1, label: 'Tue' },
  { value: 2, label: 'Wed' },
  { value: 3, label: 'Thu' },
  { value: 4, label: 'Fri' },
  { value: 5, label: 'Sat' },
  { value: 6, label: 'Sun' },
]

// Parse initial days_of_week string into a Set
function parseDays(raw: string | null | undefined): Set<number> {
  if (!raw) return new Set()
  return new Set(raw.split(',').map(Number).filter(n => n >= 0 && n <= 6))
}

const frequencyType = ref<FrequencyType>(props.schedule?.frequency_type ?? 'daily')
const timeOfDay = ref<string>(props.schedule?.time_of_day ?? '08:00')
const frequencyValue = ref<number>(props.schedule?.frequency_value ?? 2)
const selectedDays = ref<Set<number>>(parseDays(props.schedule?.days_of_week))
const dayOfMonth = ref<number>(props.schedule?.day_of_month ?? 1)
const notificationsEnabled = ref<boolean>(props.schedule?.notifications_enabled ?? true)

const isEditMode = computed(() => !!props.schedule)

const labelClass = 'block text-xs font-medium text-pure-white/60 uppercase tracking-wider mb-1'
const inputClass = 'w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-pure-white text-sm focus:outline-none focus:border-cyber-blue/60 transition-colors'
const selectClass = 'w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-pure-white text-sm focus:outline-none focus:border-cyber-blue/60 transition-colors appearance-none cursor-pointer'

function toggleDay(day: number) {
  if (selectedDays.value.has(day)) {
    selectedDays.value.delete(day)
  } else {
    selectedDays.value.add(day)
  }
  // Trigger reactivity for Set
  selectedDays.value = new Set(selectedDays.value)
}

function buildPayload(): MedicineScheduleCreate {
  const base: MedicineScheduleCreate = {
    frequency_type: frequencyType.value,
    time_of_day: timeOfDay.value,
    notifications_enabled: notificationsEnabled.value,
  }

  if (frequencyType.value === 'every_n_days') {
    base.frequency_value = frequencyValue.value
  } else if (frequencyType.value === 'weekly') {
    base.days_of_week = Array.from(selectedDays.value).sort().join(',') || null
  } else if (frequencyType.value === 'monthly') {
    base.day_of_month = dayOfMonth.value
  }

  return base
}

const handleSubmit = () => {
  emit('save', buildPayload())
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <!-- Frequency type -->
    <div>
      <label for="freq-type" :class="labelClass">Frequency</label>
      <div class="relative">
        <select
          id="freq-type"
          v-model="frequencyType"
          :class="selectClass"
        >
          <option
            v-for="opt in FREQUENCY_OPTIONS"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </option>
        </select>
        <UIcon
          name="i-heroicons-chevron-down"
          class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-pure-white/40"
        />
      </div>
    </div>

    <!-- Time of day -->
    <div>
      <label for="time-of-day" :class="labelClass">Time of Day</label>
      <input
        id="time-of-day"
        v-model="timeOfDay"
        type="time"
        required
        :class="inputClass"
      />
    </div>

    <!-- Conditional: every_n_days -->
    <div v-if="frequencyType === 'every_n_days'">
      <label for="freq-value" :class="labelClass">Every How Many Days</label>
      <input
        id="freq-value"
        v-model.number="frequencyValue"
        type="number"
        min="2"
        max="365"
        required
        :class="inputClass"
      />
    </div>

    <!-- Conditional: weekly day checkboxes -->
    <div v-if="frequencyType === 'weekly'">
      <span :class="labelClass">Days of Week</span>
      <div class="flex flex-wrap gap-2 mt-1">
        <button
          v-for="day in DAY_OPTIONS"
          :key="day.value"
          type="button"
          class="px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors duration-150 focus:outline-none"
          :class="selectedDays.has(day.value)
            ? 'bg-cyber-blue/20 border-cyber-blue text-cyber-blue'
            : 'bg-background-black border-border-gray text-pure-white/50 hover:border-pure-white/30 hover:text-pure-white/80'"
          @click="toggleDay(day.value)"
        >
          {{ day.label }}
        </button>
      </div>
      <p v-if="selectedDays.size === 0" class="mt-1.5 text-xs text-danger-red/80">
        Select at least one day
      </p>
    </div>

    <!-- Conditional: monthly day of month -->
    <div v-if="frequencyType === 'monthly'">
      <label for="day-of-month" :class="labelClass">Day of Month</label>
      <input
        id="day-of-month"
        v-model.number="dayOfMonth"
        type="number"
        min="1"
        max="31"
        required
        :class="inputClass"
      />
    </div>

    <!-- Notifications toggle -->
    <div class="flex items-center justify-between py-1">
      <div>
        <p class="text-sm font-medium text-pure-white">Notifications</p>
        <p class="text-xs text-pure-white/40">Receive reminders for this schedule</p>
      </div>
      <button
        type="button"
        class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-warning-orange/50"
        :class="notificationsEnabled ? 'bg-warning-orange' : 'bg-border-gray'"
        role="switch"
        :aria-checked="notificationsEnabled"
        @click="notificationsEnabled = !notificationsEnabled"
      >
        <span
          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200"
          :class="notificationsEnabled ? 'translate-x-5' : 'translate-x-0'"
        />
      </button>
    </div>

    <!-- Actions -->
    <div class="flex gap-3 pt-2">
      <BaseButton
        type="submit"
        variant="primary"
        class="flex-1"
        :disabled="frequencyType === 'weekly' && selectedDays.size === 0"
      >
        <UIcon name="i-heroicons-check" class="w-4 h-4" />
        {{ isEditMode ? 'Update' : 'Add' }} Schedule
      </BaseButton>
      <BaseButton type="button" variant="secondary" class="flex-1" @click="emit('cancel')">
        Cancel
      </BaseButton>
    </div>
  </form>
</template>
