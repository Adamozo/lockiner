<script setup lang="ts">
import type { JournalReport } from '~/types/journal'

definePageMeta({ layout: 'journal' })
useSeoMeta({ title: 'Journal - Reports' })

const { generateReport, fetchReport, fetchReports } = useJournal()
const toast = useToast()

const reportType = ref<'monthly' | 'yearly'>('monthly')
const reports = ref<JournalReport[]>([])
const selectedReport = ref<JournalReport | null>(null)
const loadingList = ref(true)
const loadingGenerate = ref(false)

const now = new Date()
const generateYear = ref(now.getFullYear())
const generateMonth = ref(now.getMonth() + 1)

const periodLabel = computed(() => {
  if (reportType.value === 'monthly') {
    return `${generateYear.value}-${String(generateMonth.value).padStart(2, '0')}`
  }
  return String(generateYear.value)
})

const loadReports = async () => {
  loadingList.value = true
  try {
    reports.value = await fetchReports(reportType.value)
  } catch {
    // handled
  } finally {
    loadingList.value = false
  }
}

onMounted(loadReports)
watch(reportType, () => {
  selectedReport.value = null
  loadReports()
})

const handleGenerate = async () => {
  loadingGenerate.value = true
  try {
    const report = await generateReport({
      report_type: reportType.value,
      period: periodLabel.value,
    })
    selectedReport.value = report
    toast.add({ title: 'Report generated', color: 'green' })
    await loadReports()
  } catch (e) {
    toast.add({
      title: 'Generation failed',
      description: e instanceof Error ? e.message : 'Could not generate report',
      color: 'red',
    })
  } finally {
    loadingGenerate.value = false
  }
}

const viewReport = async (report: JournalReport) => {
  try {
    selectedReport.value = await fetchReport(report.report_type, report.period)
  } catch {
    toast.add({ title: 'Failed to load report', color: 'red' })
  }
}

const formatPeriod = (type: string, period: string) => {
  if (type === 'yearly') return period
  const [y, m] = period.split('-')
  const d = new Date(+y, +m - 1)
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
}
</script>

<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-pure-white">Reports</h2>

    <!-- Report Type Toggle -->
    <div class="flex items-center gap-2">
      <button
        @click="reportType = 'monthly'"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
        :class="reportType === 'monthly' ? 'bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30' : 'text-pure-white/60 border border-border-gray hover:text-pure-white'"
      >
        Monthly
      </button>
      <button
        @click="reportType = 'yearly'"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
        :class="reportType === 'yearly' ? 'bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/30' : 'text-pure-white/60 border border-border-gray hover:text-pure-white'"
      >
        Yearly
      </button>
    </div>

    <!-- Generate Section -->
    <div class="bg-card-black border border-border-gray rounded-xl p-4">
      <h3 class="font-semibold text-pure-white mb-3">Generate Report</h3>
      <div class="flex items-end gap-3 flex-wrap">
        <div>
          <label class="block text-xs text-pure-white/50 mb-1">Year</label>
          <select
            v-model="generateYear"
            class="bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:outline-none focus:border-cyber-blue/50"
          >
            <option v-for="y in 5" :key="y" :value="now.getFullYear() - y + 1">
              {{ now.getFullYear() - y + 1 }}
            </option>
          </select>
        </div>
        <div v-if="reportType === 'monthly'">
          <label class="block text-xs text-pure-white/50 mb-1">Month</label>
          <select
            v-model="generateMonth"
            class="bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:outline-none focus:border-cyber-blue/50"
          >
            <option v-for="m in 12" :key="m" :value="m">
              {{ new Date(2000, m - 1).toLocaleDateString('en-US', { month: 'long' }) }}
            </option>
          </select>
        </div>
        <button
          @click="handleGenerate"
          :disabled="loadingGenerate"
          class="px-4 py-2 bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30 rounded-lg hover:bg-cyber-blue/20 disabled:opacity-50 transition-all text-sm font-medium"
        >
          {{ loadingGenerate ? 'Generating...' : 'Generate' }}
        </button>
      </div>
    </div>

    <!-- Report List -->
    <div v-if="loadingList" class="space-y-3">
      <div v-for="i in 3" :key="i" class="bg-card-black border border-border-gray rounded-xl p-4 h-16 animate-pulse" />
    </div>

    <div v-else-if="reports.length === 0" class="bg-card-black border border-border-gray rounded-xl p-8 text-center">
      <UIcon name="i-heroicons-chart-bar" class="w-12 h-12 text-pure-white/20 mx-auto mb-3" />
      <p class="text-pure-white/40">No {{ reportType }} reports yet. Generate one above.</p>
    </div>

    <div v-else class="space-y-2">
      <button
        v-for="report in reports"
        :key="report.id"
        @click="viewReport(report)"
        class="w-full bg-card-black border rounded-xl p-4 text-left transition-all duration-200 hover:border-cyber-blue/30"
        :class="selectedReport?.id === report.id ? 'border-cyber-blue/50' : 'border-border-gray'"
      >
        <div class="flex items-center justify-between">
          <span class="font-medium text-pure-white">{{ formatPeriod(report.report_type, report.period) }}</span>
          <span class="text-sm text-pure-white/40">{{ report.entry_count }} entries</span>
        </div>
      </button>
    </div>

    <!-- Selected Report Detail -->
    <div v-if="selectedReport">
      <h3 class="text-lg font-semibold text-pure-white mb-4">
        {{ formatPeriod(selectedReport.report_type, selectedReport.period) }} Report
      </h3>
      <JournalReportDetail :report="selectedReport" />
    </div>
  </div>
</template>
