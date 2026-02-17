<script setup lang="ts">
import type { JournalEntry } from '~/types/journal'
import { CATEGORY_META, JOURNAL_CATEGORIES } from '~/types/journal'

const props = defineProps<{
  entry: JournalEntry
}>()

const totalItems = computed(() => props.entry.items.length)

const categoryCounts = computed(() => {
  const counts: Record<string, number> = {}
  for (const cat of JOURNAL_CATEGORIES) {
    const count = props.entry.items.filter(i => i.category === cat).length
    if (count > 0) counts[cat] = count
  }
  return counts
})

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
}
</script>

<template>
  <NuxtLink
    :to="`/journal/${entry.date}`"
    class="block bg-card-black border border-border-gray rounded-xl p-4 hover:border-cyber-blue/30 transition-all duration-200"
  >
    <div class="flex items-center justify-between mb-2">
      <span class="font-semibold text-pure-white">{{ formatDate(entry.date) }}</span>
      <div class="flex items-center gap-2">
        <span v-if="entry.mood_score" class="text-sm text-pure-white/60">
          Mood: {{ entry.mood_score }}/10
        </span>
        <span class="text-xs text-pure-white/30">{{ totalItems }} items</span>
      </div>
    </div>

    <!-- Category pills -->
    <div class="flex flex-wrap gap-1.5">
      <span
        v-for="(count, cat) in categoryCounts"
        :key="cat"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-background-black"
        :class="CATEGORY_META[cat as keyof typeof CATEGORY_META]?.color"
      >
        <UIcon :name="CATEGORY_META[cat as keyof typeof CATEGORY_META]?.icon" class="w-3 h-3" />
        {{ count }}
      </span>
    </div>

    <!-- Notes preview -->
    <p v-if="entry.notes" class="mt-2 text-sm text-pure-white/40 truncate">
      {{ entry.notes }}
    </p>
  </NuxtLink>
</template>
