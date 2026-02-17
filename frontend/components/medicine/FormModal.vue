<script setup lang="ts">
import type { Medicine, MedicineCreate, MedicineScheduleCreate } from '~/types/medicine'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  created: [medicine: Medicine]
}>()

const { createMedicine, addSchedule } = useMedicines()

// --- Form state ---

const name = ref('')
const description = ref('')
const dosage = ref('')
const unit = ref('')
const color = ref<string | null>(null)

// Optional first schedule
const addScheduleInline = ref(false)
const scheduleFrequencyType = ref<'daily' | 'every_n_days' | 'weekly' | 'monthly'>('daily')
const scheduleFrequencyValue = ref<number>(2)
const scheduleTimeOfDay = ref('08:00')
const selectedWeekDays = ref<Set<number>>(new Set())
const scheduleDayOfMonth = ref<number>(1)
const scheduleNotifications = ref(true)

const DAY_OPTIONS = [
  { value: 0, label: 'Mon' },
  { value: 1, label: 'Tue' },
  { value: 2, label: 'Wed' },
  { value: 3, label: 'Thu' },
  { value: 4, label: 'Fri' },
  { value: 5, label: 'Sat' },
  { value: 6, label: 'Sun' },
]

const toggleWeekDay = (day: number) => {
  if (selectedWeekDays.value.has(day)) {
    selectedWeekDays.value.delete(day)
  } else {
    selectedWeekDays.value.add(day)
  }
  selectedWeekDays.value = new Set(selectedWeekDays.value)
}

// UI state
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

// --- Color options ---

const presetColors = [
  { label: 'White', value: '#e5e5e5' },
  { label: 'Red', value: '#ef4444' },
  { label: 'Orange', value: '#f97316' },
  { label: 'Yellow', value: '#eab308' },
  { label: 'Green', value: '#22c55e' },
  { label: 'Teal', value: '#14b8a6' },
  { label: 'Blue', value: '#3b82f6' },
  { label: 'Indigo', value: '#6366f1' },
  { label: 'Purple', value: '#a855f7' },
  { label: 'Pink', value: '#ec4899' },
]

// --- Frequency type labels ---

const frequencyTypeOptions: { value: MedicineScheduleCreate['frequency_type']; label: string }[] = [
  { value: 'daily', label: 'Every day' },
  { value: 'every_n_days', label: 'Every N days' },
  { value: 'weekly', label: 'Weekly (specific days)' },
  { value: 'monthly', label: 'Monthly (specific day)' },
]

// --- Computed validation ---

const isNameValid = computed(() => name.value.trim().length > 0)

const isScheduleValid = computed(() => {
  if (!addScheduleInline.value) return true
  if (!scheduleTimeOfDay.value) return false
  if (scheduleFrequencyType.value === 'every_n_days' && (!scheduleFrequencyValue.value || scheduleFrequencyValue.value < 1)) return false
  if (scheduleFrequencyType.value === 'weekly' && selectedWeekDays.value.size === 0) return false
  if (scheduleFrequencyType.value === 'monthly' && !scheduleDayOfMonth.value) return false
  return true
})

const canSubmit = computed(() => isNameValid.value && isScheduleValid.value && !isSubmitting.value)

// --- Actions ---

const close = () => {
  emit('update:modelValue', false)
}

const resetForm = () => {
  name.value = ''
  description.value = ''
  dosage.value = ''
  unit.value = ''
  color.value = null
  addScheduleInline.value = false
  scheduleFrequencyType.value = 'daily'
  scheduleFrequencyValue.value = 2
  scheduleTimeOfDay.value = '08:00'
  selectedWeekDays.value = new Set()
  scheduleDayOfMonth.value = 1
  scheduleNotifications.value = true
  errorMessage.value = null
}

const handleClose = () => {
  resetForm()
  close()
}

const handleSubmit = async () => {
  if (!canSubmit.value) return

  errorMessage.value = null
  isSubmitting.value = true

  try {
    const payload: MedicineCreate = {
      name: name.value.trim(),
      description: description.value.trim() || null,
      dosage: dosage.value.trim() || null,
      unit: unit.value.trim() || null,
      color: color.value || null,
    }

    const created = await createMedicine(payload)

    // Optionally attach first schedule
    if (addScheduleInline.value) {
      const schedulePayload: MedicineScheduleCreate = {
        frequency_type: scheduleFrequencyType.value,
        time_of_day: scheduleTimeOfDay.value,
        notifications_enabled: scheduleNotifications.value,
      }

      if (scheduleFrequencyType.value === 'every_n_days') {
        schedulePayload.frequency_value = scheduleFrequencyValue.value
      }
      if (scheduleFrequencyType.value === 'weekly') {
        schedulePayload.days_of_week = Array.from(selectedWeekDays.value).sort().join(',') || null
      }
      if (scheduleFrequencyType.value === 'monthly') {
        schedulePayload.day_of_month = scheduleDayOfMonth.value
      }

      await addSchedule(created.id, schedulePayload)
    }

    emit('created', created)
    resetForm()
    close()
  } catch (e) {
    errorMessage.value = e instanceof Error ? e.message : 'Failed to create medicine'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Add Medicine"
    max-width="md"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <form class="space-y-5" @submit.prevent="handleSubmit">
      <!-- Error message -->
      <div
        v-if="errorMessage"
        class="flex items-start gap-2 p-3 bg-danger-red/10 border border-danger-red/30 rounded-lg"
        role="alert"
      >
        <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 text-danger-red flex-shrink-0 mt-0.5" />
        <p class="text-sm text-danger-red">{{ errorMessage }}</p>
      </div>

      <!-- Name (required) -->
      <div>
        <label for="med-name" class="block text-sm font-medium text-pure-white/80 mb-1.5">
          Name <span class="text-danger-red">*</span>
        </label>
        <input
          id="med-name"
          v-model="name"
          type="text"
          placeholder="e.g. Vitamin D3"
          required
          autocomplete="off"
          class="w-full px-4 py-2.5 rounded-lg border bg-card-black text-pure-white placeholder-pure-white/30 focus:outline-none focus:ring-2 transition-all"
          :class="
            name.trim().length > 0
              ? 'border-electric-green/40 focus:border-electric-green focus:ring-electric-green/20'
              : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/20'
          "
        />
      </div>

      <!-- Description -->
      <div>
        <label for="med-description" class="block text-sm font-medium text-pure-white/80 mb-1.5">
          Description
        </label>
        <textarea
          id="med-description"
          v-model="description"
          placeholder="Optional notes or description"
          rows="2"
          class="w-full px-4 py-2.5 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/30 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/20 focus:outline-none transition-all resize-none"
        />
      </div>

      <!-- Dosage + Unit -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label for="med-dosage" class="block text-sm font-medium text-pure-white/80 mb-1.5">
            Dosage
          </label>
          <input
            id="med-dosage"
            v-model="dosage"
            type="text"
            placeholder="e.g. 1000"
            class="w-full px-4 py-2.5 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/30 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/20 focus:outline-none transition-all"
          />
        </div>
        <div>
          <label for="med-unit" class="block text-sm font-medium text-pure-white/80 mb-1.5">
            Unit
          </label>
          <input
            id="med-unit"
            v-model="unit"
            type="text"
            placeholder="e.g. mg, IU, ml"
            class="w-full px-4 py-2.5 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/30 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/20 focus:outline-none transition-all"
          />
        </div>
      </div>

      <!-- Color picker -->
      <div>
        <label class="block text-sm font-medium text-pure-white/80 mb-2">
          Color
        </label>
        <div class="flex flex-wrap gap-2">
          <!-- No color option -->
          <button
            type="button"
            class="w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-card-black focus:ring-cyber-blue"
            :class="
              color === null
                ? 'border-cyber-blue bg-background-black'
                : 'border-border-gray bg-background-black hover:border-pure-white/40'
            "
            title="No color"
            aria-label="No color"
            @click="color = null"
          >
            <UIcon v-if="color === null" name="i-heroicons-check" class="w-3.5 h-3.5 text-cyber-blue" />
            <UIcon v-else name="i-heroicons-x-mark" class="w-3 h-3 text-pure-white/30" />
          </button>

          <!-- Preset colors -->
          <button
            v-for="preset in presetColors"
            :key="preset.value"
            type="button"
            class="w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-card-black"
            :class="
              color === preset.value
                ? 'border-pure-white scale-110 shadow-lg'
                : 'border-transparent hover:border-pure-white/50 hover:scale-105'
            "
            :style="{ backgroundColor: preset.value, '--tw-ring-color': preset.value }"
            :title="preset.label"
            :aria-label="preset.label"
            :aria-pressed="color === preset.value"
            @click="color = preset.value"
          >
            <UIcon
              v-if="color === preset.value"
              name="i-heroicons-check"
              class="w-3.5 h-3.5 text-background-black drop-shadow"
            />
          </button>
        </div>
      </div>

      <!-- Schedule toggle -->
      <div class="border-t border-border-gray pt-4">
        <button
          type="button"
          class="flex items-center gap-2 text-sm font-medium text-pure-white/70 hover:text-pure-white transition-colors w-full text-left"
          :aria-expanded="addScheduleInline"
          @click="addScheduleInline = !addScheduleInline"
        >
          <UIcon
            :name="addScheduleInline ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
            class="w-4 h-4 text-cyber-blue flex-shrink-0 transition-transform"
          />
          <span>Add first schedule</span>
          <span class="ml-auto text-xs text-pure-white/40">optional</span>
        </button>

        <!-- Schedule fields -->
        <div
          v-if="addScheduleInline"
          class="mt-4 space-y-4 pl-6 border-l-2 border-border-gray"
        >
          <!-- Frequency type -->
          <div>
            <label for="sched-freq-type" class="block text-sm font-medium text-pure-white/80 mb-1.5">
              Frequency
            </label>
            <select
              id="sched-freq-type"
              v-model="scheduleFrequencyType"
              class="w-full px-4 py-2.5 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/20 focus:outline-none transition-all"
            >
              <option
                v-for="opt in frequencyTypeOptions"
                :key="opt.value"
                :value="opt.value"
              >
                {{ opt.label }}
              </option>
            </select>
          </div>

          <!-- Conditional: every N days -->
          <div v-if="scheduleFrequencyType === 'every_n_days'">
            <label for="sched-freq-val" class="block text-sm font-medium text-pure-white/80 mb-1.5">
              Every how many days?
            </label>
            <input
              id="sched-freq-val"
              v-model.number="scheduleFrequencyValue"
              type="number"
              min="1"
              max="365"
              class="w-full px-4 py-2.5 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/20 focus:outline-none transition-all"
            />
          </div>

          <!-- Conditional: days of week -->
          <div v-if="scheduleFrequencyType === 'weekly'">
            <span class="block text-sm font-medium text-pure-white/80 mb-2">Days of week</span>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="day in DAY_OPTIONS"
                :key="day.value"
                type="button"
                class="px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-card-black focus:ring-cyber-blue"
                :class="
                  selectedWeekDays.has(day.value)
                    ? 'bg-cyber-blue/20 border-cyber-blue text-cyber-blue'
                    : 'bg-background-black border-border-gray text-pure-white/50 hover:border-pure-white/30 hover:text-pure-white/80'
                "
                :aria-pressed="selectedWeekDays.has(day.value)"
                @click="toggleWeekDay(day.value)"
              >
                {{ day.label }}
              </button>
            </div>
            <p v-if="selectedWeekDays.size === 0" class="mt-1.5 text-xs text-danger-red/80">
              Select at least one day
            </p>
          </div>

          <!-- Conditional: day of month -->
          <div v-if="scheduleFrequencyType === 'monthly'">
            <label for="sched-day-month" class="block text-sm font-medium text-pure-white/80 mb-1.5">
              Day of month
            </label>
            <input
              id="sched-day-month"
              v-model.number="scheduleDayOfMonth"
              type="number"
              min="1"
              max="31"
              placeholder="e.g. 1"
              class="w-full px-4 py-2.5 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/30 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/20 focus:outline-none transition-all"
            />
          </div>

          <!-- Time of day -->
          <div>
            <label for="sched-time" class="block text-sm font-medium text-pure-white/80 mb-1.5">
              Time of day
            </label>
            <input
              id="sched-time"
              v-model="scheduleTimeOfDay"
              type="time"
              class="w-full px-4 py-2.5 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/20 focus:outline-none transition-all"
            />
          </div>

          <!-- Notifications -->
          <label class="flex items-center gap-3 cursor-pointer select-none">
            <div
              class="relative w-10 h-5 rounded-full transition-colors"
              :class="scheduleNotifications ? 'bg-electric-green' : 'bg-border-gray'"
            >
              <div
                class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform"
                :class="scheduleNotifications ? 'translate-x-5' : 'translate-x-0'"
              />
              <input
                v-model="scheduleNotifications"
                type="checkbox"
                class="sr-only"
                aria-label="Enable notifications"
              />
            </div>
            <span class="text-sm text-pure-white/80">Enable notifications</span>
          </label>
        </div>
      </div>
    </form>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <BaseButton variant="ghost" :disabled="isSubmitting" @click="handleClose">
          Cancel
        </BaseButton>
        <BaseButton
          variant="primary"
          icon="i-heroicons-plus"
          :loading="isSubmitting"
          :disabled="!canSubmit"
          @click="handleSubmit"
        >
          Add Medicine
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>
