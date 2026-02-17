<script setup lang="ts">
import type { JournalStats } from '~/types/journal'

definePageMeta({ layout: 'journal' })
useSeoMeta({ title: 'Journal - Dashboard' })

const { fetchStats, fetchEntries, recentEntries, loading } = useJournal()

const stats = ref<JournalStats | null>(null)
const loadingStats = ref(true)

onMounted(async () => {
  try {
    const [s] = await Promise.all([
      fetchStats(),
      fetchEntries({ limit: 5 }),
    ])
    stats.value = s
  } catch {
    // handled by composable
  } finally {
    loadingStats.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-pure-white">Journal Dashboard</h2>
      <NuxtLink
        :to="`/journal/today`"
        class="px-4 py-2 bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30 rounded-lg hover:bg-cyber-blue/20 transition-all text-sm font-medium"
      >
        Write Today
      </NuxtLink>
    </div>

    <!-- Stats Cards -->
    <div v-if="loadingStats" class="grid grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="bg-card-black border border-border-gray rounded-xl p-4 h-20 animate-pulse" />
    </div>
    <div v-else-if="stats" class="grid grid-cols-2 lg:grid-cols-3 gap-4">
      <JournalStatsCard label="Total Entries" :value="stats.total_entries" icon="i-heroicons-document-text" />
      <JournalStatsCard label="This Week" :value="stats.entries_this_week" icon="i-heroicons-calendar" />
      <JournalStatsCard label="This Month" :value="stats.entries_this_month" icon="i-heroicons-calendar-days" />
      <JournalStatsCard label="Current Streak" :value="`${stats.current_streak}d`" icon="i-heroicons-fire" color="text-warning-orange" />
      <JournalStatsCard label="Longest Streak" :value="`${stats.longest_streak}d`" icon="i-heroicons-trophy" color="text-electric-green" />
      <JournalStatsCard label="Avg Mood" :value="stats.avg_mood ?? '-'" icon="i-heroicons-face-smile" color="text-cyber-blue" />
    </div>

    <!-- Recent Entries -->
    <section>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-pure-white">Recent Entries</h3>
        <NuxtLink
          to="/journal/history"
          class="text-sm text-cyber-blue hover:text-cyber-blue/80 transition-colors"
        >
          View all
        </NuxtLink>
      </div>

      <div v-if="loading" class="space-y-3">
        <div v-for="i in 3" :key="i" class="bg-card-black border border-border-gray rounded-xl p-4 h-20 animate-pulse" />
      </div>

      <div v-else-if="recentEntries.length === 0" class="bg-card-black border border-border-gray rounded-xl p-8 text-center">
        <UIcon name="i-heroicons-book-open" class="w-12 h-12 text-pure-white/20 mx-auto mb-3" />
        <p class="text-pure-white/40 mb-4">No journal entries yet</p>
        <NuxtLink
          to="/journal/today"
          class="inline-block px-4 py-2 bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30 rounded-lg hover:bg-cyber-blue/20 transition-all text-sm"
        >
          Write your first entry
        </NuxtLink>
      </div>

      <div v-else class="space-y-3">
        <JournalEntryCard v-for="entry in recentEntries" :key="entry.id" :entry="entry" />
      </div>
    </section>
  </div>
</template>
