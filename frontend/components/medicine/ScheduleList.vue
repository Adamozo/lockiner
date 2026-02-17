<script setup lang="ts">
import type { MedicineSchedule } from '~/types/medicine'

defineProps<{
  schedules: MedicineSchedule[]
}>()

const emit = defineEmits<{
  add: []
  edit: [schedule: MedicineSchedule]
  delete: [scheduleId: number]
}>()

const DAY_LABELS: Record<number, string> = {
  0: 'Mon',
  1: 'Tue',
  2: 'Wed',
  3: 'Thu',
  4: 'Fri',
  5: 'Sat',
  6: 'Sun',
}

function formatFrequency(schedule: MedicineSchedule): string {
  const time = schedule.time_of_day

  switch (schedule.frequency_type) {
    case 'daily':
      return `Daily at ${time}`

    case 'every_n_days': {
      const n = schedule.frequency_value ?? 2
      return `Every ${n} day${n !== 1 ? 's' : ''} at ${time}`
    }

    case 'weekly': {
      const raw = schedule.days_of_week
      if (raw) {
        const dayNums = raw.split(',').map(Number).filter(d => d >= 0 && d <= 6)
        const dayStr = dayNums.map(d => DAY_LABELS[d]).join(', ')
        return `Weekly ${dayStr} at ${time}`
      }
      return `Weekly at ${time}`
    }

    case 'monthly': {
      const day = schedule.day_of_month ?? 1
      return `Monthly on day ${day} at ${time}`
    }

    default:
      return `At ${time}`
  }
}
</script>

<template>
  <div class="space-y-3">
    <!-- Empty state -->
    <div
      v-if="schedules.length === 0"
      class="flex flex-col items-center justify-center py-8 text-center border border-dashed border-border-gray rounded-xl"
    >
      <UIcon name="i-heroicons-clock" class="w-8 h-8 text-pure-white/20 mb-2" />
      <p class="text-sm text-pure-white/40">No schedules yet</p>
    </div>

    <!-- Schedule rows -->
    <div
      v-for="schedule in schedules"
      :key="schedule.id"
      class="flex items-center gap-3 bg-background-black border border-border-gray rounded-xl px-4 py-3 transition-colors hover:border-border-gray/60"
    >
      <!-- Clock icon -->
      <div class="flex-shrink-0 w-9 h-9 rounded-lg bg-cyber-blue/10 flex items-center justify-center">
        <UIcon name="i-heroicons-clock" class="w-5 h-5 text-cyber-blue" />
      </div>

      <!-- Frequency description -->
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-pure-white truncate">
          {{ formatFrequency(schedule) }}
        </p>
        <div class="flex items-center gap-2 mt-0.5">
          <!-- Active badge -->
          <span
            class="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full"
            :class="schedule.active
              ? 'bg-electric-green/10 text-electric-green'
              : 'bg-border-gray/30 text-pure-white/30'"
          >
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="schedule.active ? 'bg-electric-green' : 'bg-pure-white/30'"
            />
            {{ schedule.active ? 'Active' : 'Inactive' }}
          </span>

          <!-- Notifications badge -->
          <span
            v-if="schedule.notifications_enabled"
            class="inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full bg-warning-orange/10 text-warning-orange"
          >
            <UIcon name="i-heroicons-bell" class="w-3 h-3" />
            Notifications
          </span>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="flex items-center gap-1 flex-shrink-0">
        <button
          type="button"
          class="w-8 h-8 rounded-lg flex items-center justify-center text-pure-white/40 hover:text-cyber-blue hover:bg-cyber-blue/10 transition-colors"
          title="Edit schedule"
          @click="emit('edit', schedule)"
        >
          <UIcon name="i-heroicons-pencil" class="w-4 h-4" />
        </button>
        <button
          type="button"
          class="w-8 h-8 rounded-lg flex items-center justify-center text-pure-white/40 hover:text-danger-red hover:bg-danger-red/10 transition-colors"
          title="Delete schedule"
          @click="emit('delete', schedule.id)"
        >
          <UIcon name="i-heroicons-trash" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Add schedule button -->
    <button
      type="button"
      class="w-full py-3 rounded-xl border border-dashed border-border-gray text-sm text-pure-white/50 hover:text-electric-green hover:border-electric-green/40 transition-colors flex items-center justify-center gap-2"
      @click="emit('add')"
    >
      <UIcon name="i-heroicons-plus" class="w-4 h-4" />
      Add Schedule
    </button>
  </div>
</template>
