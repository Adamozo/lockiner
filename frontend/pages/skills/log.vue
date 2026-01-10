<script setup lang="ts">
import type { LogEntryCreate } from '~/types/skills'

definePageMeta({
  layout: 'skills',
})

useSeoMeta({
  title: 'Learning Log - LockIner',
  description: 'View your learning activity history',
})

const { journeys, addHours, fetchJourneys } = useJourneys()
const { sortedEntries, hoursThisWeek, totalHours, loading, fetchEntries, addEntry, deleteEntry } = useLearningLog()
const toast = useToast()

// UI state
const showAddModal = ref(false)
const newEntry = ref<LogEntryCreate>({
  journey_id: 0,
  date: new Date().toISOString().split('T')[0],
  duration_minutes: 60,
  activity: '',
  notes: '',
})

onMounted(async () => {
  await Promise.all([fetchJourneys(), fetchEntries()])
})

const handleAddEntry = async () => {
  if (!newEntry.value.journey_id || !newEntry.value.activity) {
    toast.add({
      title: 'Error',
      description: 'Please select a journey and describe your activity',
      color: 'red',
    })
    return
  }

  try {
    const journey = journeys.value.find(j => j.id === newEntry.value.journey_id)
    await addEntry(newEntry.value, journey?.name || '')

    // Add hours to journey
    addHours(newEntry.value.journey_id, newEntry.value.duration_minutes / 60)

    toast.add({
      title: 'Success',
      description: 'Activity logged!',
      color: 'green',
    })
    showAddModal.value = false
    resetForm()
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to log activity',
      color: 'red',
    })
  }
}

const handleDelete = async (id: number) => {
  if (!confirm('Delete this activity entry?')) return

  try {
    await deleteEntry(id)
    toast.add({
      title: 'Success',
      description: 'Entry deleted',
      color: 'green',
    })
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to delete entry',
      color: 'red',
    })
  }
}

const resetForm = () => {
  newEntry.value = {
    journey_id: 0,
    date: new Date().toISOString().split('T')[0],
    duration_minutes: 60,
    activity: '',
    notes: '',
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatDuration = (minutes: number) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours === 0) return `${mins}min`
  if (mins === 0) return `${hours}h`
  return `${hours}h ${mins}min`
}

// Group entries by date
const entriesByDate = computed(() => {
  const groups: Record<string, typeof sortedEntries.value> = {}
  sortedEntries.value.forEach(entry => {
    if (!groups[entry.date]) {
      groups[entry.date] = []
    }
    groups[entry.date].push(entry)
  })
  return groups
})

const activeJourneys = computed(() => journeys.value.filter(j => j.status === 'active'))
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Learning Log</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">Track your learning activities</p>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        size="sm"
        variant="primary"
        @click="showAddModal = true"
      >
        Log Activity
      </BaseButton>
    </header>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-card-black border border-border-gray rounded-lg p-6">
        <p class="text-sm text-pure-white/60 mb-2">This Week</p>
        <p class="text-3xl font-bold text-cyber-blue">{{ hoursThisWeek.toFixed(1) }}h</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-6">
        <p class="text-sm text-pure-white/60 mb-2">Total Logged</p>
        <p class="text-3xl font-bold text-electric-green">{{ totalHours.toFixed(1) }}h</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-6">
        <p class="text-sm text-pure-white/60 mb-2">Total Entries</p>
        <p class="text-3xl font-bold text-warning-orange">{{ sortedEntries.length }}</p>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-cyber-blue animate-spin" />
    </div>

    <!-- Entries by date -->
    <div v-else-if="Object.keys(entriesByDate).length > 0" class="space-y-6">
      <div
        v-for="(dateEntries, date) in entriesByDate"
        :key="date"
      >
        <h3 class="text-sm font-medium text-pure-white/60 mb-3">{{ formatDate(date) }}</h3>
        <div class="space-y-3">
          <div
            v-for="entry in dateEntries"
            :key="entry.id"
            class="bg-card-black border border-border-gray rounded-lg p-4 hover:border-cyber-blue/50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-4">
                <div class="p-2 bg-cyber-blue/10 rounded-lg">
                  <UIcon name="i-heroicons-pencil-square" class="w-5 h-5 text-cyber-blue" />
                </div>
                <div>
                  <p class="font-medium text-pure-white">{{ entry.activity }}</p>
                  <NuxtLink
                    :to="`/skills/journey/${entry.journey_id}`"
                    class="text-sm text-cyber-blue hover:text-electric-green transition-colors"
                  >
                    {{ entry.journey_name }}
                  </NuxtLink>
                  <p v-if="entry.notes" class="text-sm text-pure-white/60 mt-2">{{ entry.notes }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-lg font-semibold text-cyber-blue">{{ formatDuration(entry.duration_minutes) }}</span>
                <BaseButton
                  variant="danger"
                  size="sm"
                  icon="i-heroicons-trash"
                  @click="handleDelete(entry.id)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="bg-card-black border border-border-gray rounded-lg p-12 text-center">
      <UIcon name="i-heroicons-clipboard-document-list" class="w-16 h-16 mx-auto text-pure-white/40 mb-4" />
      <h3 class="text-lg font-semibold text-pure-white mb-2">No activity logged yet</h3>
      <p class="text-pure-white/60 mb-6">Start tracking your learning sessions</p>
      <BaseButton variant="primary" icon="i-heroicons-plus" @click="showAddModal = true">
        Log Your First Activity
      </BaseButton>
    </div>

    <!-- Add Entry Modal -->
    <BaseModal v-model="showAddModal" title="Log Activity" max-width="lg">
      <form @submit.prevent="handleAddEntry" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Journey</label>
          <select
            v-model.number="newEntry.journey_id"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          >
            <option value="0" disabled>Select a journey...</option>
            <option v-for="j in activeJourneys" :key="j.id" :value="j.id">
              {{ j.name }}
            </option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Date</label>
            <input
              v-model="newEntry.date"
              type="date"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Duration (minutes)</label>
            <input
              v-model.number="newEntry.duration_minutes"
              type="number"
              min="1"
              step="15"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">What did you work on?</label>
          <input
            v-model="newEntry.activity"
            type="text"
            placeholder="Completed tutorial chapter 5..."
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Notes (optional)</label>
          <textarea
            v-model="newEntry.notes"
            rows="2"
            placeholder="Any insights or reflections..."
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          />
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-border-gray">
          <BaseButton type="button" variant="secondary" @click="showAddModal = false">
            Cancel
          </BaseButton>
          <BaseButton type="submit" variant="primary" :loading="loading">
            Log Activity
          </BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
