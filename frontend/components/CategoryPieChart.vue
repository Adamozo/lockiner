<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from 'chart.js'
import type { CategorySpending } from '~/types/api'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  data: CategorySpending[]
}>()

const categoriesStore = useCategoriesStore()

// Distinct color palette for categories without a stored color
const COLOR_PALETTE = [
  '#00FF87', '#00B4D8', '#F97316', '#A855F7', '#EF4444',
  '#EAB308', '#EC4899', '#14B8A6', '#6366F1', '#8B5CF6',
  '#F59E0B', '#06B6D4', '#F43F5E', '#10B981', '#3B82F6',
]

// Generate chart data
const chartData = computed<ChartData<'doughnut'>>(() => {
  const labels = props.data.map(item => item.category)
  const values = props.data.map(item => item.total)
  const colors = props.data.map((item, index) => {
    const category = categoriesStore.getCategoryByName(item.category)
    return category?.color || COLOR_PALETTE[index % COLOR_PALETTE.length]
  })

  return {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: colors,
        borderColor: '#1A1D29',
        borderWidth: 2,
      },
    ],
  }
})

// Chart options
const chartOptions = computed<ChartOptions<'doughnut'>>(() => ({
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: '#F8FAFC',
        padding: 15,
        font: {
          size: 12,
        },
        usePointStyle: true,
        pointStyle: 'circle',
      },
    },
    tooltip: {
      backgroundColor: '#1A1D29',
      titleColor: '#F8FAFC',
      bodyColor: '#F8FAFC',
      borderColor: '#3B82F6',
      borderWidth: 1,
      padding: 12,
      displayColors: true,
      callbacks: {
        label: (context) => {
          const label = context.label || ''
          const value = context.parsed || 0
          const percentage = props.data[context.dataIndex]?.percentage || 0
          return `${label}: ${value.toFixed(2)} PLN (${percentage.toFixed(1)}%)`
        },
      },
    },
  },
}))
</script>

<template>
  <div class="w-full">
    <Doughnut v-if="data.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else class="text-pure-white/40 text-center py-8">
      No category data available
    </p>
  </div>
</template>
