<script setup lang="ts">
import type { FitnessStats } from '~/types/fitness'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Progress - LockIner',
  description: 'Track your fitness progress over time',
})

const { workouts, fetchWorkouts, fetchStats } = useWorkouts()
const { sortedEntries, currentWeight, weightChange, fetchEntries } = useWeight()

const stats = ref<FitnessStats>({
  total_workouts: 0,
  workouts_this_week: 0,
  workouts_this_month: 0,
  total_weight_lifted_kg: 0,
  current_weight_kg: null,
  weight_change_kg: null,
})

onMounted(async () => {
  await Promise.all([fetchWorkouts(), fetchEntries()])
  try {
    stats.value = await fetchStats()
  } catch {
    // Stats will remain at defaults
  }
})

// Calculate exercise progress (max weight per exercise over time)
const exerciseProgress = computed(() => {
  const exerciseMap = new Map<string, { date: string; weight: number }[]>()

  workouts.value.forEach(workout => {
    workout.exercises.forEach(exercise => {
      if (!exerciseMap.has(exercise.name)) {
        exerciseMap.set(exercise.name, [])
      }
      exerciseMap.get(exercise.name)!.push({
        date: workout.date,
        weight: exercise.weight_kg,
      })
    })
  })

  // Get top exercises by frequency
  return Array.from(exerciseMap.entries())
    .filter(([_, data]) => data.length >= 2)
    .map(([name, data]) => {
      const sorted = data.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      const firstWeight = sorted[0].weight
      const lastWeight = sorted[sorted.length - 1].weight
      const maxWeight = Math.max(...sorted.map(d => d.weight))

      return {
        name,
        entries: sorted.length,
        firstWeight,
        lastWeight,
        maxWeight,
        change: lastWeight - firstWeight,
        changePercent: firstWeight > 0 ? ((lastWeight - firstWeight) / firstWeight * 100) : 0,
      }
    })
    .sort((a, b) => b.entries - a.entries)
    .slice(0, 8)
})

// Weekly workout frequency
const weeklyStats = computed(() => {
  const weeks: { week: string; count: number }[] = []
  const now = new Date()

  for (let i = 0; i < 8; i++) {
    const weekStart = new Date(now)
    weekStart.setDate(now.getDate() - (now.getDay() + 7 * i))
    weekStart.setHours(0, 0, 0, 0)

    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 7)

    const count = workouts.value.filter(w => {
      const date = new Date(w.date)
      return date >= weekStart && date < weekEnd
    }).length

    weeks.unshift({
      week: weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      count,
    })
  }

  return weeks
})

const maxWeeklyCount = computed(() => Math.max(...weeklyStats.value.map(w => w.count), 1))
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <div>
      <h1 class="text-3xl font-bold text-pure-white">Progress</h1>
      <p class="mt-2 text-pure-white/60">Track your fitness journey over time</p>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-card-black border border-border-gray rounded-lg p-4">
        <p class="text-sm text-pure-white/60">Total Workouts</p>
        <p class="text-2xl font-bold text-warning-orange">{{ stats.total_workouts }}</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-4">
        <p class="text-sm text-pure-white/60">This Month</p>
        <p class="text-2xl font-bold text-cyber-blue">{{ stats.workouts_this_month }}</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-4">
        <p class="text-sm text-pure-white/60">Current Weight</p>
        <p class="text-2xl font-bold text-electric-green">{{ currentWeight ? `${currentWeight}kg` : 'N/A' }}</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-4">
        <p class="text-sm text-pure-white/60">Weight Change</p>
        <p
          class="text-2xl font-bold"
          :class="weightChange !== null && weightChange <= 0 ? 'text-electric-green' : 'text-danger-red'"
        >
          {{ weightChange !== null ? `${weightChange > 0 ? '+' : ''}${weightChange.toFixed(1)}kg` : 'N/A' }}
        </p>
      </div>
    </div>

    <!-- Weekly Activity -->
    <div class="bg-card-black border border-border-gray rounded-lg p-6">
      <h2 class="text-xl font-semibold text-pure-white mb-4">Weekly Activity</h2>
      <div class="flex items-end gap-2 h-40">
        <div
          v-for="week in weeklyStats"
          :key="week.week"
          class="flex-1 flex flex-col items-center"
        >
          <span class="text-xs text-pure-white/60 mb-1">{{ week.count }}</span>
          <div
            class="w-full bg-gradient-to-t from-warning-orange to-warning-orange/50 rounded-t-sm transition-all"
            :style="{ height: `${(week.count / maxWeeklyCount) * 100}%`, minHeight: week.count > 0 ? '8px' : '2px' }"
            :class="week.count === 0 ? 'bg-border-gray' : ''"
          />
          <span class="text-xs text-pure-white/40 mt-2 truncate w-full text-center">{{ week.week }}</span>
        </div>
      </div>
    </div>

    <!-- Exercise Progress -->
    <div class="bg-card-black border border-border-gray rounded-lg p-6">
      <h2 class="text-xl font-semibold text-pure-white mb-4">Strength Progress</h2>

      <div v-if="exerciseProgress.length > 0" class="space-y-4">
        <div
          v-for="exercise in exerciseProgress"
          :key="exercise.name"
          class="p-4 bg-background-black rounded-lg"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <UIcon name="i-heroicons-bolt" class="w-5 h-5 text-warning-orange" />
              <span class="font-medium text-pure-white">{{ exercise.name }}</span>
            </div>
            <span
              class="text-sm font-semibold"
              :class="exercise.change >= 0 ? 'text-electric-green' : 'text-danger-red'"
            >
              {{ exercise.change >= 0 ? '+' : '' }}{{ exercise.change.toFixed(1) }}kg
              ({{ exercise.changePercent >= 0 ? '+' : '' }}{{ exercise.changePercent.toFixed(0) }}%)
            </span>
          </div>
          <div class="flex items-center gap-4 text-sm text-pure-white/60">
            <span>First: {{ exercise.firstWeight }}kg</span>
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
            <span>Latest: {{ exercise.lastWeight }}kg</span>
            <span class="ml-auto">Max: {{ exercise.maxWeight }}kg</span>
          </div>
          <!-- Progress bar -->
          <div class="mt-2 h-2 bg-border-gray rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-warning-orange to-electric-green rounded-full transition-all"
              :style="{ width: `${Math.min(100, (exercise.lastWeight / exercise.maxWeight) * 100)}%` }"
            />
          </div>
        </div>
      </div>

      <div v-else class="text-center py-8">
        <UIcon name="i-heroicons-chart-bar" class="w-12 h-12 mx-auto text-pure-white/40 mb-3" />
        <p class="text-pure-white/60">Log more workouts to see your strength progress</p>
        <p class="text-sm text-pure-white/40 mt-1">Exercises need at least 2 logged sessions to show progress</p>
      </div>
    </div>

    <!-- Weight History -->
    <div v-if="sortedEntries.length > 0" class="bg-card-black border border-border-gray rounded-lg p-6">
      <h2 class="text-xl font-semibold text-pure-white mb-4">Weight History</h2>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="text-left text-sm text-pure-white/60">
              <th class="pb-3">Date</th>
              <th class="pb-3">Weight</th>
              <th class="pb-3">Body Fat</th>
              <th class="pb-3">Change</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(entry, index) in sortedEntries.slice(0, 10)"
              :key="entry.id"
              class="border-t border-border-gray"
            >
              <td class="py-3 text-pure-white">
                {{ new Date(entry.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}
              </td>
              <td class="py-3 font-semibold text-warning-orange">{{ entry.weight_kg }} kg</td>
              <td class="py-3 text-pure-white/60">
                {{ entry.body_fat_percentage ? `${entry.body_fat_percentage}%` : '-' }}
              </td>
              <td class="py-3">
                <span
                  v-if="index < sortedEntries.length - 1"
                  :class="entry.weight_kg <= sortedEntries[index + 1].weight_kg ? 'text-electric-green' : 'text-danger-red'"
                >
                  {{ entry.weight_kg <= sortedEntries[index + 1].weight_kg ? '' : '+' }}{{ (entry.weight_kg - sortedEntries[index + 1].weight_kg).toFixed(1) }}kg
                </span>
                <span v-else class="text-pure-white/40">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
