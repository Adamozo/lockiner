<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from 'chart.js'
import type { MerchantSpending } from '~/types/api'

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps<{
  month?: string
  limit?: number
}>()

const { getSpendingByMerchant } = useAnalytics()

// Data state
const merchantData = ref<MerchantSpending[]>([])
const loading = ref(false)

// Fetch merchant data
const fetchData = async () => {
  loading.value = true
  try {
    const data = await getSpendingByMerchant(props.month)
    // Limit to top N merchants
    merchantData.value = data.slice(0, props.limit || 10)
  } catch (error) {
    console.error('Failed to fetch merchant data:', error)
    merchantData.value = []
  } finally {
    loading.value = false
  }
}

// Watch for prop changes
watch(() => props.month, fetchData, { immediate: true })

// Generate chart data
const chartData = computed<ChartData<'bar'>>(() => {
  const labels = merchantData.value.map(item => item.merchant)
  const values = merchantData.value.map(item => item.total)

  return {
    labels,
    datasets: [
      {
        label: 'Spending (PLN)',
        data: values,
        backgroundColor: '#3B82F6',
        borderColor: '#60A5FA',
        borderWidth: 1,
      },
    ],
  }
})

// Chart options
const chartOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: true,
  indexAxis: 'y', // Horizontal bars
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#1A1D29',
      titleColor: '#F8FAFC',
      bodyColor: '#F8FAFC',
      borderColor: '#3B82F6',
      borderWidth: 1,
      padding: 12,
      callbacks: {
        label: (context) => {
          const value = context.parsed.x || 0
          const item = merchantData.value[context.dataIndex]
          return `Total: ${value.toFixed(2)} PLN (${item?.receipts_count || 0} receipts)`
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
      },
      grid: {
        display: false,
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
    <Bar v-else-if="merchantData.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else class="text-pure-white/40 text-center py-8">
      No merchant data available
    </p>
  </div>
</template>
