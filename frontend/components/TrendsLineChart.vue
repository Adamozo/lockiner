<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartData,
  type ChartOptions,
} from 'chart.js'
import type { SpendingTrend } from '~/types/api'

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps<{
  months?: number
  category?: string
}>()

const { getSpendingTrends } = useAnalytics()

// Data state
const trendsData = ref<SpendingTrend[]>([])
const loading = ref(false)

// Fetch trends data
const fetchData = async () => {
  loading.value = true
  try {
    trendsData.value = await getSpendingTrends(props.months || 6, props.category)
  } catch (error) {
    console.error('Failed to fetch trends data:', error)
    trendsData.value = []
  } finally {
    loading.value = false
  }
}

// Watch for prop changes
watch([() => props.months, () => props.category], fetchData, { immediate: true })

// Format month for display (YYYY-MM -> MMM YYYY)
const formatMonth = (month: string) => {
  const [year, monthNum] = month.split('-')
  const date = new Date(Number(year), Number(monthNum) - 1)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

// Generate chart data
const chartData = computed<ChartData<'line'>>(() => {
  const labels = trendsData.value.map(item => formatMonth(item.month))
  const values = trendsData.value.map(item => item.amount)

  return {
    labels,
    datasets: [
      {
        label: 'Monthly Spending',
        data: values,
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#10B981',
        pointBorderColor: '#1A1D29',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  }
})

// Chart options
const chartOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1A1D29',
      titleColor: '#F8FAFC',
      bodyColor: '#F8FAFC',
      borderColor: '#10B981',
      borderWidth: 1,
      padding: 12,
      callbacks: {
        label: (context) => {
          const value = context.parsed.y || 0
          return `Spending: ${value.toFixed(2)} PLN`
        },
      },
    },
  },
  scales: {
    x: {
      ticks: {
        color: '#F8FAFC',
      },
      grid: {
        color: '#2D3748',
      },
    },
    y: {
      ticks: {
        color: '#F8FAFC',
        callback: (value) => `${value} PLN`,
      },
      grid: {
        color: '#2D3748',
      },
    },
  },
}))
</script>

<template>
  <div class="w-full">
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-blue"></div>
    </div>
    <Line v-else-if="trendsData.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else class="text-pure-white/40 text-center py-8">
      No trend data available
    </p>
  </div>
</template>
