<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'
import type { DailyGoal, WeeklyDay } from '~/composables/useFoodNutrition'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

definePageMeta({ layout: 'fitness' })

const { t, locale } = useI18n()
const { fetchWeeklySummary, fetchGoal, updateGoal } = useFoodNutrition()
const toast = useToast()

const weeklyData = ref<WeeklyDay[]>([])
const goal = ref<DailyGoal>({ calories: 2000 })
const goalForm = ref<DailyGoal>({ calories: 2000 })
const loading = ref(false)
const savingGoal = ref(false)
const editingGoal = ref(false)

async function load() {
  loading.value = true
  try {
    const [weekly, g] = await Promise.all([fetchWeeklySummary(), fetchGoal()])
    weeklyData.value = weekly
    goal.value = g
    goalForm.value = { ...g }
  } catch {}
  loading.value = false
}

const chartData = computed(() => ({
  labels: weeklyData.value.map(d => {
    const date = new Date(d.date + 'T12:00:00')
    const loc = locale.value === 'pl' ? 'pl-PL' : 'en-US'
    return date.toLocaleDateString(loc, { weekday: 'short', day: 'numeric' })
  }),
  datasets: [
    {
      label: t('food.goal_calories'),
      data: weeklyData.value.map(d => d.goal_calories),
      backgroundColor: '#ffffff18',
      borderColor: '#ffffff33',
      borderWidth: 1,
      borderRadius: 4,
    },
    {
      label: 'kcal',
      data: weeklyData.value.map(d => d.calories),
      backgroundColor: '#00bfff99',
      borderColor: '#00bfff',
      borderWidth: 1,
      borderRadius: 4,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#aaa', font: { size: 11 } } },
    tooltip: {
      callbacks: {
        label: (ctx: any) => `${ctx.dataset.label}: ${Math.round(ctx.raw)} kcal`,
      },
    },
  },
  scales: {
    x: { ticks: { color: '#888' }, grid: { color: '#2a2a2a' } },
    y: { ticks: { color: '#888' }, grid: { color: '#2a2a2a' }, beginAtZero: true },
  },
}

const weekAvgKcal = computed(() => {
  if (!weeklyData.value.length) return 0
  return Math.round(weeklyData.value.reduce((s, d) => s + d.calories, 0) / weeklyData.value.length)
})

async function saveGoal() {
  savingGoal.value = true
  try {
    await updateGoal(goalForm.value)
    goal.value = { ...goalForm.value }
    editingGoal.value = false
    toast.add({ title: t('common.success'), color: 'green' })
    await load()
  } catch {
    toast.add({ title: t('common.error'), color: 'red' })
  } finally {
    savingGoal.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-pure-white">{{ $t('food.calorie_trend') }}</h1>
        <p class="text-pure-white/60 text-sm mt-1">{{ $t('food.last_7_days') }}</p>
      </div>
      <NuxtLink to="/food/today">
        <BaseButton variant="secondary" size="sm">
          {{ $t('food.go_to_log') }}
        </BaseButton>
      </NuxtLink>
    </div>

    <!-- Weekly chart -->
    <div class="bg-card-black border border-border-gray rounded-xl p-5">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-pure-white font-semibold">{{ $t('food.last_7_days') }}</h3>
        <div class="text-sm">
          <span class="text-gray-400">{{ $t('food.avg_weekly') }}: </span>
          <span class="text-cyber-blue font-bold">{{ weekAvgKcal }} kcal</span>
        </div>
      </div>
      <div v-if="loading" class="h-52 flex items-center justify-center">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-cyber-blue animate-spin" />
      </div>
      <div v-else class="h-52">
        <Bar :data="chartData" :options="chartOptions" />
      </div>
    </div>

    <!-- Goals section -->
    <div class="bg-card-black border border-border-gray rounded-xl p-5">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-pure-white font-semibold">{{ $t('food.daily_goal') }}</h3>
        <BaseButton
          :variant="editingGoal ? 'ghost' : 'secondary'"
          size="sm"
          @click="editingGoal = !editingGoal; goalForm = { ...goal }"
        >
          {{ editingGoal ? $t('food.cancel') : $t('food.edit_goals') }}
        </BaseButton>
      </div>

      <!-- Edit form -->
      <template v-if="editingGoal">
        <div class="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label class="text-xs text-gray-400 mb-1.5 block">{{ $t('food.goal_calories') }}</label>
            <input
              v-model.number="goalForm.calories"
              type="number"
              class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white text-sm focus:outline-none focus:border-electric-green transition-colors"
            />
          </div>
          <div>
            <label class="text-xs text-gray-400 mb-1.5 block">{{ $t('food.goal_protein') }}</label>
            <input
              v-model.number="goalForm.protein"
              type="number"
              class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white text-sm focus:outline-none focus:border-electric-green transition-colors"
            />
          </div>
          <div>
            <label class="text-xs text-gray-400 mb-1.5 block">{{ $t('food.goal_carbs') }}</label>
            <input
              v-model.number="goalForm.carbohydrates"
              type="number"
              class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white text-sm focus:outline-none focus:border-electric-green transition-colors"
            />
          </div>
          <div>
            <label class="text-xs text-gray-400 mb-1.5 block">{{ $t('food.goal_fat') }}</label>
            <input
              v-model.number="goalForm.fat"
              type="number"
              class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white text-sm focus:outline-none focus:border-electric-green transition-colors"
            />
          </div>
        </div>
        <BaseButton variant="primary" size="md" :loading="savingGoal" @click="saveGoal">
          {{ $t('food.save_goals') }}
        </BaseButton>
      </template>

      <!-- Display -->
      <template v-else>
        <div class="grid grid-cols-4 gap-3">
          <div class="bg-background-black rounded-xl p-3 text-center">
            <div class="text-electric-green font-bold text-xl">{{ goal.calories || 2000 }}</div>
            <div class="text-gray-400 text-xs mt-0.5">kcal</div>
          </div>
          <div class="bg-background-black rounded-xl p-3 text-center">
            <div class="text-cyber-blue font-bold text-xl">{{ goal.protein ?? '—' }}</div>
            <div class="text-gray-400 text-xs mt-0.5">{{ $t('food.goal_protein') }}</div>
          </div>
          <div class="bg-background-black rounded-xl p-3 text-center">
            <div class="text-purple-400 font-bold text-xl">{{ goal.carbohydrates ?? '—' }}</div>
            <div class="text-gray-400 text-xs mt-0.5">{{ $t('food.goal_carbs') }}</div>
          </div>
          <div class="bg-background-black rounded-xl p-3 text-center">
            <div class="text-warning-orange font-bold text-xl">{{ goal.fat ?? '—' }}</div>
            <div class="text-gray-400 text-xs mt-0.5">{{ $t('food.goal_fat') }}</div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
