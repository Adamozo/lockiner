<script setup lang="ts">
definePageMeta({ layout: 'journal' })
useSeoMeta({ title: 'Journal - History' })

const router = useRouter()
const { fetchEntries, entries, loading } = useJournal()

const newEntryDate = ref('')
const dateInputRef = ref<HTMLInputElement | null>(null)

const goToDate = () => {
  if (newEntryDate.value) {
    router.push(`/journal/${newEntryDate.value}`)
  }
}

const openDatePicker = () => {
  dateInputRef.value?.showPicker?.()
}

const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1)

const monthLabel = computed(() => {
  const d = new Date(selectedYear.value, selectedMonth.value - 1)
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const loadEntries = async () => {
  const y = selectedYear.value
  const m = String(selectedMonth.value).padStart(2, '0')
  const startDate = `${y}-${m}-01`

  // End of month
  const nextMonth = selectedMonth.value === 12 ? 1 : selectedMonth.value + 1
  const nextYear = selectedMonth.value === 12 ? y + 1 : y
  const endDt = new Date(nextYear, nextMonth - 1, 0)
  const endDate = `${y}-${m}-${String(endDt.getDate()).padStart(2, '0')}`

  await fetchEntries({ start_date: startDate, end_date: endDate, limit: 100 })
}

onMounted(loadEntries)
watch([selectedYear, selectedMonth], loadEntries)

const prevMonth = () => {
  if (selectedMonth.value === 1) {
    selectedMonth.value = 12
    selectedYear.value--
  } else {
    selectedMonth.value--
  }
}

const nextMonth = () => {
  if (selectedMonth.value === 12) {
    selectedMonth.value = 1
    selectedYear.value++
  } else {
    selectedMonth.value++
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header with New Entry -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h2 class="text-2xl font-bold text-pure-white">History</h2>
      <div class="flex items-center gap-2">
        <input
          ref="dateInputRef"
          v-model="newEntryDate"
          type="date"
          @click="openDatePicker"
          class="bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:outline-none focus:border-cyber-blue/50 transition-colors cursor-pointer"
        />
        <button
          @click="goToDate"
          :disabled="!newEntryDate"
          class="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all duration-300 bg-gradient-to-r from-cyber-blue to-electric-green text-background-black shadow-lg shadow-electric-green/20 hover:opacity-90 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          New Entry
        </button>
      </div>
    </div>

    <!-- Month Picker -->
    <div class="flex items-center justify-center gap-3">
      <button
        @click="prevMonth"
        class="p-2 rounded-lg border border-border-gray text-pure-white/60 hover:text-pure-white hover:border-pure-white/30 transition-all"
      >
        <UIcon name="i-heroicons-chevron-left" class="w-5 h-5" />
      </button>
      <span class="text-pure-white font-medium min-w-[160px] text-center">{{ monthLabel }}</span>
      <button
        @click="nextMonth"
        class="p-2 rounded-lg border border-border-gray text-pure-white/60 hover:text-pure-white hover:border-pure-white/30 transition-all"
      >
        <UIcon name="i-heroicons-chevron-right" class="w-5 h-5" />
      </button>
    </div>

    <!-- Entry List -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="bg-card-black border border-border-gray rounded-xl p-4 h-20 animate-pulse" />
    </div>

    <div v-else-if="entries.length === 0" class="bg-card-black border border-border-gray rounded-xl p-8 text-center">
      <UIcon name="i-heroicons-calendar" class="w-12 h-12 text-pure-white/20 mx-auto mb-3" />
      <p class="text-pure-white/40">No entries for {{ monthLabel }}</p>
    </div>

    <div v-else class="space-y-3">
      <JournalEntryCard v-for="entry in entries" :key="entry.id" :entry="entry" />
    </div>
  </div>
</template>
