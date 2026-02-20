<script setup lang="ts">
import type { TodoStats } from '~/types/todo'

definePageMeta({ layout: 'todo' })

useSeoMeta({ title: 'Todo – Stats – LockIner' })

const { fetchStats, fetchListsRange } = useTodo()

const stats = ref<TodoStats | null>(null)
const days = ref(30)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    stats.value = await fetchStats(days.value)
    const today = new Date().toISOString().split('T')[0]
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - days.value)
    await fetchListsRange(cutoff.toISOString().split('T')[0], today)
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(days, load)

function formatRate(v: number) {
  return `${v.toFixed(1)}%`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-pure-white">Todo statistics</h1>

      <select
        v-model="days"
        class="bg-card-black border border-border-gray rounded-lg px-3 py-1.5 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
      >
        <option :value="7">Last 7 days</option>
        <option :value="30">Last 30 days</option>
        <option :value="90">Last 90 days</option>
      </select>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <span class="i-heroicons-arrow-path animate-spin text-2xl text-border-gray" />
    </div>

    <template v-else-if="stats">
      <!-- Stat cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-card-black border border-border-gray rounded-xl p-4 space-y-1">
          <p class="text-xs text-border-gray">Completed</p>
          <p class="text-2xl font-bold text-electric-green">{{ formatRate(stats.completion_rate_pct) }}</p>
          <p class="text-xs text-border-gray">{{ stats.total_completed }}/{{ stats.total_created }} tasks</p>
        </div>

        <div class="bg-card-black border border-border-gray rounded-xl p-4 space-y-1">
          <p class="text-xs text-border-gray">Postponed</p>
          <p
            class="text-2xl font-bold"
            :class="stats.postpone_rate_pct > 20 ? 'text-danger-red' : 'text-warning-orange'"
          >
            {{ formatRate(stats.postpone_rate_pct) }}
          </p>
          <p class="text-xs text-border-gray">{{ stats.total_postponed }} postponements</p>
        </div>

        <div class="bg-card-black border border-border-gray rounded-xl p-4 space-y-1">
          <p class="text-xs text-border-gray">Streak</p>
          <p class="text-2xl font-bold text-cyber-blue">{{ stats.current_streak_days }}</p>
          <p class="text-xs text-border-gray">days at 100% in a row</p>
        </div>

        <div class="bg-card-black border border-border-gray rounded-xl p-4 space-y-1">
          <p class="text-xs text-border-gray">Total tasks</p>
          <p class="text-2xl font-bold text-pure-white">{{ stats.total_created }}</p>
          <p class="text-xs text-border-gray">over {{ days }} days</p>
        </div>
      </div>

      <!-- Motivation message -->
      <div
        v-if="stats.total_created > 0"
        class="p-4 rounded-xl border"
        :class="stats.postpone_rate_pct > 30
          ? 'bg-danger-red/5 border-danger-red/30'
          : stats.postpone_rate_pct > 10
            ? 'bg-warning-orange/5 border-warning-orange/30'
            : 'bg-electric-green/5 border-electric-green/30'"
      >
        <p
          class="text-sm font-medium"
          :class="stats.postpone_rate_pct > 30
            ? 'text-danger-red'
            : stats.postpone_rate_pct > 10
              ? 'text-warning-orange'
              : 'text-electric-green'"
        >
          <template v-if="stats.postpone_rate_pct > 30">
            {{ formatRate(stats.postpone_rate_pct) }} of tasks were postponed. Maybe worth thinking seriously about that?
          </template>
          <template v-else-if="stats.postpone_rate_pct > 10">
            {{ formatRate(stats.postpone_rate_pct) }} of tasks postponed. Getting closer to perfect!
          </template>
          <template v-else>
            Great work! Only {{ formatRate(stats.postpone_rate_pct) }} of tasks were postponed.
          </template>
        </p>
      </div>

      <!-- Empty state -->
      <div v-else class="text-center py-12 space-y-2">
        <span class="i-heroicons-chart-bar text-4xl text-border-gray" />
        <p class="text-border-gray text-sm">No data for the selected period.</p>
        <p class="text-border-gray text-xs">Start creating todo lists to see statistics.</p>
      </div>
    </template>
  </div>
</template>
