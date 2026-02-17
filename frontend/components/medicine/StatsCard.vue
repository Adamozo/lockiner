<script setup lang="ts">
import type { MedicineStats } from '~/types/medicine'

interface Props {
  stats: MedicineStats | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const adherenceColor = computed(() => {
  if (!props.stats) return 'text-pure-white/40'
  const pct = props.stats.weekly_adherence_pct
  if (pct >= 80) return 'text-electric-green'
  if (pct >= 50) return 'text-warning-orange'
  return 'text-danger-red'
})

const adherenceBarColor = computed(() => {
  if (!props.stats) return 'bg-border-gray'
  const pct = props.stats.weekly_adherence_pct
  if (pct >= 80) return 'bg-electric-green'
  if (pct >= 50) return 'bg-warning-orange'
  return 'bg-danger-red'
})
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-xl p-5 hover:border-cyber-blue/30 transition-colors">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-4">
      <div class="p-2.5 rounded-xl bg-cyber-blue/20 border border-cyber-blue/30">
        <UIcon name="i-heroicons-beaker" class="w-5 h-5 text-cyber-blue" />
      </div>
      <div>
        <h3 class="font-semibold text-pure-white leading-tight">Medicines Today</h3>
        <p class="text-xs text-pure-white/50">Adherence overview</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="space-y-3">
      <div class="h-10 w-24 bg-pure-white/5 rounded-lg animate-pulse" />
      <div class="h-2 bg-pure-white/5 rounded-full animate-pulse" />
      <div class="grid grid-cols-2 gap-3">
        <div class="h-14 bg-pure-white/5 rounded-lg animate-pulse" />
        <div class="h-14 bg-pure-white/5 rounded-lg animate-pulse" />
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="stats">
      <!-- Large today fraction -->
      <div class="mb-4">
        <p
          class="text-4xl font-bold text-pure-white leading-none"
          aria-label="`${stats.today_taken} of ${stats.today_total} doses taken today`"
        >
          {{ stats.today_taken }}
          <span class="text-2xl text-pure-white/40">/{{ stats.today_total }}</span>
        </p>
        <p class="text-xs text-pure-white/50 mt-1">doses taken today</p>
      </div>

      <!-- Weekly adherence bar -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs text-pure-white/50">Weekly adherence</span>
          <span class="text-xs font-semibold" :class="adherenceColor">
            {{ stats.weekly_adherence_pct.toFixed(0) }}%
          </span>
        </div>
        <div class="h-1.5 bg-background-black rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="adherenceBarColor"
            :style="{ width: `${Math.min(stats.weekly_adherence_pct, 100)}%` }"
            role="progressbar"
            :aria-valuenow="stats.weekly_adherence_pct"
            aria-valuemin="0"
            aria-valuemax="100"
          />
        </div>
      </div>

      <!-- Stat tiles -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-background-black rounded-lg p-3">
          <div class="flex items-center gap-1.5 mb-1">
            <UIcon name="i-heroicons-chart-bar" class="w-3.5 h-3.5 text-cyber-blue" />
            <span class="text-[10px] uppercase tracking-wider text-pure-white/40">Adherence</span>
          </div>
          <p class="text-lg font-bold" :class="adherenceColor">
            {{ stats.weekly_adherence_pct.toFixed(0) }}%
          </p>
          <p class="text-[10px] text-pure-white/40">this week</p>
        </div>

        <div class="bg-background-black rounded-lg p-3">
          <div class="flex items-center gap-1.5 mb-1">
            <UIcon name="i-heroicons-fire" class="w-3.5 h-3.5 text-warning-orange" />
            <span class="text-[10px] uppercase tracking-wider text-pure-white/40">Streak</span>
          </div>
          <p class="text-lg font-bold text-warning-orange">
            {{ stats.current_streak_days }}
          </p>
          <p class="text-[10px] text-pure-white/40">{{ stats.current_streak_days === 1 ? 'day' : 'days' }}</p>
        </div>
      </div>
    </div>

    <!-- Empty/no data -->
    <div v-else class="py-4 text-center">
      <UIcon name="i-heroicons-beaker" class="w-8 h-8 text-pure-white/20 mx-auto mb-2" />
      <p class="text-sm text-pure-white/40">No data available</p>
    </div>
  </div>
</template>
