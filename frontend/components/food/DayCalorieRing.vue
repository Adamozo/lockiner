<script setup lang="ts">
const props = defineProps<{
  consumed: number
  goal: number
  protein?: number
  carbohydrates?: number
  fat?: number
  proteinGoal?: number
  carbGoal?: number
  fatGoal?: number
}>()

const { t } = useI18n()

const size = 180
const strokeWidth = 14
const radius = (size - strokeWidth) / 2
const circumference = 2 * Math.PI * radius

const progress = computed(() => props.goal ? Math.min(props.consumed / props.goal, 1) : 0)
const dashOffset = computed(() => circumference * (1 - progress.value))

const progressColor = computed(() => {
  const p = progress.value
  if (p < 0.5) return '#00ff88'
  if (p < 0.9) return '#00bfff'
  if (p <= 1.0) return '#ffa500'
  return '#ff4444'
})

const macros = computed(() => [
  { label: t('food.goal_protein').replace(' (g)', ''), value: props.protein || 0, goal: props.proteinGoal, color: '#00bfff' },
  { label: t('food.goal_carbs').replace(' (g)', ''), value: props.carbohydrates || 0, goal: props.carbGoal, color: '#a78bfa' },
  { label: t('food.goal_fat').replace(' (g)', ''), value: props.fat || 0, goal: props.fatGoal, color: '#ffa500' },
])
</script>

<template>
  <div class="flex flex-col items-center gap-5">
    <!-- Ring -->
    <div class="relative" :style="{ width: size + 'px', height: size + 'px' }">
      <svg :width="size" :height="size" class="-rotate-90">
        <circle :cx="size/2" :cy="size/2" :r="radius" fill="none" stroke="#2a2a2a" :stroke-width="strokeWidth" />
        <circle
          :cx="size/2" :cy="size/2" :r="radius" fill="none"
          :stroke="progressColor" :stroke-width="strokeWidth"
          stroke-linecap="round"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="dashOffset"
          style="transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease"
        />
      </svg>
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="text-pure-white font-bold text-3xl leading-none tabular-nums">{{ Math.round(consumed) }}</span>
        <span class="text-gray-400 text-xs mt-0.5">/ {{ Math.round(goal) }} kcal</span>
        <span class="font-bold text-sm mt-1" :style="{ color: progressColor }">{{ Math.round(progress * 100) }}%</span>
      </div>
    </div>

    <!-- Macro bars -->
    <div class="w-full space-y-2.5 max-w-xs">
      <div v-for="macro in macros" :key="macro.label">
        <div class="flex justify-between text-xs mb-1">
          <span class="text-gray-400">{{ macro.label }}</span>
          <span class="text-pure-white tabular-nums">
            {{ Math.round(macro.value) }}g
            <span v-if="macro.goal" class="text-gray-500"> / {{ macro.goal }}g</span>
          </span>
        </div>
        <div class="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :style="{
              width: macro.goal ? Math.min(macro.value / macro.goal * 100, 100) + '%' : '0%',
              backgroundColor: macro.color,
            }"
          />
        </div>
      </div>
    </div>
  </div>
</template>
