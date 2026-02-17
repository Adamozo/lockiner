<script setup lang="ts">
import type { JournalReport, JournalCategory } from '~/types/journal'
import { CATEGORY_META, JOURNAL_CATEGORIES } from '~/types/journal'

defineProps<{
  report: JournalReport
}>()
</script>

<template>
  <div class="space-y-6">
    <!-- Summary Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-card-black border border-border-gray rounded-xl p-3 text-center">
        <p class="text-xl font-bold text-pure-white">{{ report.entry_count }}</p>
        <p class="text-xs text-pure-white/50">Entries</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-xl p-3 text-center">
        <p class="text-xl font-bold text-pure-white">{{ report.data.avg_mood ?? '-' }}</p>
        <p class="text-xs text-pure-white/50">Avg Mood</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-xl p-3 text-center">
        <p class="text-xl font-bold text-pure-white">{{ report.data.current_streak }}</p>
        <p class="text-xs text-pure-white/50">Current Streak</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-xl p-3 text-center">
        <p class="text-xl font-bold text-pure-white">{{ report.data.longest_streak }}</p>
        <p class="text-xs text-pure-white/50">Longest Streak</p>
      </div>
    </div>

    <!-- Per-Category Lists -->
    <div
      v-for="cat in JOURNAL_CATEGORIES"
      :key="cat"
      class="bg-card-black border border-border-gray rounded-xl p-4"
    >
      <div class="flex items-center gap-2 mb-3">
        <UIcon :name="CATEGORY_META[cat].icon" class="w-5 h-5" :class="CATEGORY_META[cat].color" />
        <h3 class="font-semibold text-pure-white">{{ CATEGORY_META[cat].label }}</h3>
        <span class="text-xs text-pure-white/40">({{ report.data.categories[cat]?.count ?? 0 }})</span>
      </div>

      <ul v-if="report.data.categories[cat]?.items?.length" class="space-y-1.5">
        <li
          v-for="(item, idx) in report.data.categories[cat].items"
          :key="idx"
          class="text-sm text-pure-white/70 flex items-start gap-2"
        >
          <span class="text-pure-white/30 mt-0.5">&#8226;</span>
          <span>{{ item }}</span>
        </li>
      </ul>
      <p v-else class="text-sm text-pure-white/30 italic">No items</p>
    </div>
  </div>
</template>
