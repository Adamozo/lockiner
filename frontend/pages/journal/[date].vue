<script setup lang="ts">
import type { JournalItemCreate, JournalCategory } from '~/types/journal'
import { JOURNAL_CATEGORIES } from '~/types/journal'

definePageMeta({ layout: 'journal' })

const route = useRoute()
const date = computed(() => route.params.date as string)

useSeoMeta({ title: () => `Journal - ${date.value}` })

const { fetchEntryByDate, createEntry, updateEntry, deleteEntry } = useJournal()
const toast = useToast()

const entryId = ref<number | null>(null)
const moodScore = ref<number | null>(null)
const notes = ref<string>('')
const itemsByCategory = ref<Record<JournalCategory, JournalItemCreate[]>>({
  accomplished: [],
  grateful: [],
  proud: [],
  annoyed: [],
  learned: [],
})

const isLoading = ref(true)
const isSaving = ref(false)
const isNew = ref(true)
const hasUnsavedChanges = ref(false)

// Load existing entry
const loadEntry = async () => {
  isLoading.value = true
  try {
    const entry = await fetchEntryByDate(date.value)
    entryId.value = entry.id
    moodScore.value = entry.mood_score
    notes.value = entry.notes || ''
    isNew.value = false

    // Group items by category
    const grouped: Record<JournalCategory, JournalItemCreate[]> = {
      accomplished: [],
      grateful: [],
      proud: [],
      annoyed: [],
      learned: [],
    }
    for (const item of entry.items) {
      if (grouped[item.category]) {
        grouped[item.category].push({
          category: item.category,
          position: item.position,
          content: item.content,
        })
      }
    }
    itemsByCategory.value = grouped
  } catch {
    // Entry doesn't exist yet, keep defaults
    isNew.value = true
  } finally {
    isLoading.value = false
  }
}

onMounted(loadEntry)

// Watch date changes
watch(date, loadEntry)

// Collect all items
const allItems = computed(() => {
  const items: JournalItemCreate[] = []
  for (const cat of JOURNAL_CATEGORIES) {
    for (const item of itemsByCategory.value[cat]) {
      items.push(item)
    }
  }
  return items
})

// Auto-save with debounce
let saveTimeout: ReturnType<typeof setTimeout> | null = null

const triggerAutoSave = () => {
  hasUnsavedChanges.value = true
  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(() => {
    saveEntry()
  }, 3000)
}

watch(moodScore, triggerAutoSave)
watch(notes, triggerAutoSave)
watch(itemsByCategory, triggerAutoSave, { deep: true })

const updateCategoryItems = (category: JournalCategory, items: JournalItemCreate[]) => {
  itemsByCategory.value[category] = items
}

const saveEntry = async () => {
  if (isLoading.value) return
  isSaving.value = true
  try {
    if (isNew.value) {
      const entry = await createEntry({
        date: date.value,
        mood_score: moodScore.value,
        notes: notes.value || undefined,
        items: allItems.value,
      })
      entryId.value = entry.id
      isNew.value = false
    } else if (entryId.value) {
      await updateEntry(entryId.value, {
        mood_score: moodScore.value,
        notes: notes.value || undefined,
        items: allItems.value,
      })
    }
    hasUnsavedChanges.value = false
  } catch (e) {
    toast.add({
      title: 'Save Failed',
      description: e instanceof Error ? e.message : 'Could not save entry',
      color: 'red',
    })
  } finally {
    isSaving.value = false
  }
}

const { confirm } = useConfirm()

const handleDelete = async () => {
  if (!entryId.value) return
  if (!await confirm({ message: 'Delete this journal entry?', confirmText: 'Delete' })) return
  try {
    await deleteEntry(entryId.value)
    toast.add({ title: 'Entry deleted', color: 'green' })
    await navigateTo('/journal')
  } catch {
    toast.add({ title: 'Delete failed', color: 'red' })
  }
}

const formatDateDisplay = (d: string) => {
  const dt = new Date(d + 'T00:00:00')
  return dt.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
}

// Cleanup on unmount
onUnmounted(() => {
  if (saveTimeout) clearTimeout(saveTimeout)
})
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-pure-white">{{ formatDateDisplay(date) }}</h2>
          <div class="flex items-center gap-2 mt-1">
            <span v-if="isSaving" class="text-xs text-cyber-blue animate-pulse">Saving...</span>
            <span v-else-if="hasUnsavedChanges" class="text-xs text-warning-orange">Unsaved changes</span>
            <span v-else-if="!isNew" class="text-xs text-electric-green">Saved</span>
          </div>
        </div>
        <!-- Desktop buttons -->
        <div class="hidden md:flex gap-2">
          <button
            v-if="!isNew"
            @click="handleDelete"
            class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all duration-300 bg-gradient-to-r from-danger-red to-pink-500 text-white shadow-lg shadow-danger-red/30"
          >
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Delete
          </button>
          <button
            @click="saveEntry"
            :disabled="isSaving"
            class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all duration-300 bg-gradient-to-r from-electric-green to-cyan-400 text-background-black shadow-lg shadow-electric-green/30 disabled:opacity-50"
          >
            <UIcon name="i-heroicons-check" class="w-4 h-4" />
            {{ isSaving ? 'Saving...' : 'Save Now' }}
          </button>
        </div>
      </div>

      <!-- Mobile buttons -->
      <div class="flex gap-3 mt-4 md:hidden">
        <button
          v-if="!isNew"
          @click="handleDelete"
          class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold text-sm transition-all duration-300 bg-gradient-to-r from-danger-red to-pink-500 text-white shadow-lg shadow-danger-red/30"
        >
          <UIcon name="i-heroicons-trash" class="w-5 h-5" />
          Delete
        </button>
        <button
          @click="saveEntry"
          :disabled="isSaving"
          class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-semibold text-sm transition-all duration-300 bg-gradient-to-r from-electric-green to-cyan-400 text-background-black shadow-lg shadow-electric-green/30 disabled:opacity-50"
        >
          <UIcon name="i-heroicons-check" class="w-5 h-5" />
          {{ isSaving ? 'Saving...' : 'Save Now' }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="bg-card-black border border-border-gray rounded-xl p-6 h-32 animate-pulse" />
    </div>

    <template v-else>
      <!-- Mood Selector -->
      <div class="bg-card-black border border-border-gray rounded-xl p-4">
        <JournalMoodSelector v-model="moodScore" />
      </div>

      <!-- Category Sections -->
      <div
        v-for="cat in JOURNAL_CATEGORIES"
        :key="cat"
        class="bg-card-black border border-border-gray rounded-xl p-4"
      >
        <JournalCategorySection
          :category="cat"
          :items="itemsByCategory[cat]"
          @update:items="updateCategoryItems(cat, $event)"
        />
      </div>

      <!-- Notes -->
      <div class="bg-card-black border border-border-gray rounded-xl p-4">
        <div class="flex items-center gap-2 mb-3">
          <UIcon name="i-heroicons-chat-bubble-bottom-center-text" class="w-5 h-5 text-cyber-blue" />
          <h3 class="font-semibold text-pure-white">Notes</h3>
        </div>
        <textarea
          v-model="notes"
          rows="3"
          placeholder="Any additional thoughts for today..."
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-pure-white/30 focus:outline-none focus:border-cyber-blue/50 transition-colors resize-none"
        />
      </div>
    </template>
  </div>
</template>
