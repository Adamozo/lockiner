<script setup lang="ts">
import type { FitnessStats } from '~/types/fitness'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Fitness Dashboard - LockIner',
  description: 'Track your workout progress and fitness goals',
})

const { workouts, recentWorkouts, completedWorkouts, fetchWorkouts } = useWorkouts()
const { currentWeight, weightChange, sortedEntries, fetchEntries } = useWeight()

const stats = ref<FitnessStats>({
  total_workouts: 0,
  workouts_this_week: 0,
  workouts_this_month: 0,
  total_weight_lifted_kg: 0,
  current_weight_kg: null,
  weight_change_kg: null,
})
const loading = ref(true)

onMounted(async () => {
  try {
    const { fetchStats } = useWorkouts()
    await Promise.all([fetchWorkouts(), fetchEntries()])
    stats.value = await fetchStats()
  } catch {
    // Stats will remain at defaults
  } finally {
    loading.value = false
  }
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

const formatWeight = (kg: number) => {
  return kg >= 1000 ? `${(kg / 1000).toFixed(1)}t` : `${kg.toFixed(0)}kg`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div>
      <h1 class="text-3xl font-bold text-pure-white">Fitness Dashboard</h1>
      <p class="mt-2 text-pure-white/60">Track your workouts and monitor your progress</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-warning-orange animate-spin" />
    </div>

    <template v-else>
      <!-- Stats cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Workouts This Week -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-warning-orange to-electric-green" />
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-pure-white/60">This Week</p>
              <p class="mt-2 text-3xl font-bold text-warning-orange">{{ stats.workouts_this_week }}</p>
              <p class="text-xs text-pure-white/40 mt-1">workouts</p>
            </div>
            <div class="p-3 bg-gradient-to-br from-warning-orange/20 to-warning-orange/5 rounded-full border border-warning-orange/30">
              <UIcon name="i-heroicons-fire" class="w-8 h-8 text-warning-orange" />
            </div>
          </div>
        </div>

        <!-- Total Workouts -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-pure-white/60">Total Workouts</p>
              <p class="mt-2 text-3xl font-bold text-cyber-blue">{{ stats.total_workouts }}</p>
              <p class="text-xs text-pure-white/40 mt-1">all time</p>
            </div>
            <div class="p-3 bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 rounded-full border border-cyber-blue/30">
              <UIcon name="i-heroicons-trophy" class="w-8 h-8 text-cyber-blue" />
            </div>
          </div>
        </div>

        <!-- Current Weight -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-electric-green to-cyber-blue" />
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-pure-white/60">Current Weight</p>
              <p class="mt-2 text-3xl font-bold text-electric-green">
                {{ stats.current_weight_kg ? `${stats.current_weight_kg}kg` : 'N/A' }}
              </p>
              <p v-if="stats.weight_change_kg !== null" class="text-xs mt-1" :class="stats.weight_change_kg <= 0 ? 'text-electric-green' : 'text-danger-red'">
                {{ stats.weight_change_kg > 0 ? '+' : '' }}{{ stats.weight_change_kg.toFixed(1) }}kg
              </p>
            </div>
            <div class="p-3 bg-gradient-to-br from-electric-green/20 to-electric-green/5 rounded-full border border-electric-green/30">
              <UIcon name="i-heroicons-scale" class="w-8 h-8 text-electric-green" />
            </div>
          </div>
        </div>

        <!-- Weight Lifted -->
        <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-danger-red to-warning-orange" />
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-pure-white/60">Total Weight Lifted</p>
              <p class="mt-2 text-3xl font-bold text-pure-white">{{ formatWeight(stats.total_weight_lifted_kg) }}</p>
              <p class="text-xs text-pure-white/40 mt-1">all time</p>
            </div>
            <div class="p-3 bg-gradient-to-br from-pure-white/10 to-pure-white/5 rounded-full border border-pure-white/20">
              <UIcon name="i-heroicons-bolt" class="w-8 h-8 text-pure-white" />
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Workouts -->
      <div class="bg-card-black border border-border-gray rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-pure-white">Recent Workouts</h2>
          <NuxtLink to="/fitness/workouts" class="text-sm text-warning-orange hover:text-warning-orange/80 transition-colors">
            View all
          </NuxtLink>
        </div>

        <div v-if="completedWorkouts.length > 0" class="space-y-3">
          <div
            v-for="workout in completedWorkouts.slice(0, 5)"
            :key="workout.id"
            class="flex items-center gap-4 p-3 rounded-lg hover:bg-background-black/50 transition-colors"
          >
            <div class="p-2 bg-warning-orange/10 rounded-lg flex-shrink-0">
              <UIcon name="i-heroicons-fire" class="w-5 h-5 text-warning-orange" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-pure-white truncate">{{ workout.name }}</p>
              <p class="text-xs text-pure-white/40">
                {{ formatDate(workout.date) }} &middot; {{ workout.exercises.length }} exercises
                <span v-if="workout.duration_minutes"> &middot; {{ workout.duration_minutes }}min</span>
              </p>
            </div>
            <NuxtLink
              :to="`/fitness/workouts/${workout.id}`"
              class="text-pure-white/30 hover:text-pure-white transition-colors"
            >
              <UIcon name="i-heroicons-chevron-right" class="w-5 h-5" />
            </NuxtLink>
          </div>
        </div>

        <div v-else class="text-center py-8">
          <div class="w-12 h-12 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-3">
            <UIcon name="i-heroicons-fire" class="w-6 h-6 text-pure-white/40" />
          </div>
          <p class="text-pure-white/60 mb-3">No workouts yet</p>
          <BaseButton variant="primary" size="sm" icon="i-heroicons-plus" @click="navigateTo('/fitness/workouts/new')">
            Log Workout
          </BaseButton>
        </div>
      </div>

      <!-- Weight History -->
      <div class="bg-card-black border border-border-gray rounded-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-pure-white">Weight Tracking</h2>
          <NuxtLink to="/fitness/weight" class="text-sm text-warning-orange hover:text-warning-orange/80 transition-colors">
            View all
          </NuxtLink>
        </div>

        <div v-if="sortedEntries.length > 0" class="space-y-3">
          <div
            v-for="(entry, index) in sortedEntries.slice(0, 5)"
            :key="entry.id"
            class="flex items-center gap-4 p-3 rounded-lg hover:bg-background-black/50 transition-colors"
          >
            <div class="p-2 bg-electric-green/10 rounded-lg flex-shrink-0">
              <UIcon name="i-heroicons-scale" class="w-5 h-5 text-electric-green" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-pure-white">{{ entry.weight_kg }} kg</p>
              <p class="text-xs text-pure-white/40">{{ formatDate(entry.date) }}</p>
            </div>
            <span
              v-if="index < sortedEntries.length - 1"
              class="text-sm font-medium"
              :class="entry.weight_kg <= sortedEntries[index + 1].weight_kg ? 'text-electric-green' : 'text-danger-red'"
            >
              {{ entry.weight_kg <= sortedEntries[index + 1].weight_kg ? '' : '+' }}{{ (entry.weight_kg - sortedEntries[index + 1].weight_kg).toFixed(1) }}kg
            </span>
          </div>
        </div>

        <div v-else class="text-center py-8">
          <div class="w-12 h-12 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-3">
            <UIcon name="i-heroicons-scale" class="w-6 h-6 text-pure-white/40" />
          </div>
          <p class="text-pure-white/60 mb-3">No weight entries yet</p>
          <BaseButton variant="primary" size="sm" icon="i-heroicons-plus" @click="navigateTo('/fitness/weight')">
            Log Weight
          </BaseButton>
        </div>
      </div>
    </template>
  </div>
</template>
