<script setup lang="ts">
import type { MedicineLog } from '~/types/medicine'

defineProps<{
  logs: MedicineLog[]
}>()

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
}

function formatTime(timeStr: string): string {
  // timeStr is HH:MM or HH:MM:SS
  const parts = timeStr.split(':')
  const h = parseInt(parts[0], 10)
  const m = parts[1]
  const ampm = h >= 12 ? 'PM' : 'AM'
  const hour12 = h % 12 || 12
  return `${hour12}:${m} ${ampm}`
}

function formatTakenAt(isoStr: string | null): string {
  if (!isoStr) return '—'
  const d = new Date(isoStr)
  return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
}
</script>

<template>
  <div class="flex flex-col gap-0">
    <!-- Empty state -->
    <div
      v-if="logs.length === 0"
      class="flex flex-col items-center justify-center py-10 text-center"
    >
      <UIcon name="i-heroicons-clipboard-document-list" class="w-10 h-10 text-pure-white/15 mb-3" />
      <p class="text-sm text-pure-white/40">No log entries yet</p>
    </div>

    <!-- Table (shown when logs exist) -->
    <template v-else>
      <!-- Header -->
      <div class="grid grid-cols-4 gap-2 px-3 py-2 border-b border-border-gray">
        <span class="text-xs font-medium uppercase tracking-wider text-pure-white/40">Date</span>
        <span class="text-xs font-medium uppercase tracking-wider text-pure-white/40">Time</span>
        <span class="text-xs font-medium uppercase tracking-wider text-pure-white/40">Status</span>
        <span class="text-xs font-medium uppercase tracking-wider text-pure-white/40">Taken At</span>
      </div>

      <!-- Scrollable rows -->
      <div class="overflow-y-auto max-h-80 divide-y divide-border-gray/40">
        <div
          v-for="log in logs"
          :key="log.id"
          class="grid grid-cols-4 gap-2 px-3 py-3 items-center hover:bg-white/[0.02] transition-colors"
        >
          <!-- Date -->
          <span class="text-sm text-pure-white/80">
            {{ formatDate(log.scheduled_date) }}
          </span>

          <!-- Scheduled time -->
          <span class="text-sm text-pure-white/60">
            {{ formatTime(log.scheduled_time) }}
          </span>

          <!-- Status -->
          <div class="flex items-center gap-1.5">
            <div
              v-if="log.taken"
              class="flex items-center gap-1 text-electric-green"
            >
              <UIcon name="i-heroicons-check-circle-solid" class="w-4 h-4 flex-shrink-0" />
              <span class="text-xs font-medium">Taken</span>
            </div>
            <div
              v-else
              class="flex items-center gap-1 text-danger-red"
            >
              <UIcon name="i-heroicons-x-circle-solid" class="w-4 h-4 flex-shrink-0" />
              <span class="text-xs font-medium">Missed</span>
            </div>
          </div>

          <!-- Taken at -->
          <span class="text-sm" :class="log.taken_at ? 'text-pure-white/60' : 'text-pure-white/20'">
            {{ formatTakenAt(log.taken_at) }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>
