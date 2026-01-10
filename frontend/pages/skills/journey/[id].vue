<script setup lang="ts">
import type { LogEntryCreate } from '~/types/skills'

definePageMeta({
  layout: 'skills',
})

const route = useRoute()
const journeyId = computed(() => Number(route.params.id))

const { journeys, getJourney, toggleMilestone, addHours } = useJourneys()
const { entries, addEntry, getEntriesForJourney } = useLearningLog()
const toast = useToast()

const journey = computed(() => getJourney(journeyId.value))
const journeyEntries = computed(() => getEntriesForJourney(journeyId.value))

useSeoMeta({
  title: computed(() => journey.value ? `${journey.value.name} - LockIner` : 'Journey - LockIner'),
  description: 'Track your learning journey progress',
})

// UI state
const showLogModal = ref(false)
const newEntry = ref<LogEntryCreate>({
  journey_id: journeyId.value,
  date: new Date().toISOString().split('T')[0],
  duration_minutes: 60,
  activity: '',
  notes: '',
})

const handleToggleMilestone = async (milestoneId: number) => {
  await toggleMilestone(journeyId.value, milestoneId)
}

const handleLogActivity = async () => {
  if (!newEntry.value.activity) {
    toast.add({
      title: 'Error',
      description: 'Please describe what you worked on',
      color: 'red',
    })
    return
  }

  try {
    newEntry.value.journey_id = journeyId.value
    await addEntry(newEntry.value, journey.value?.name || '')

    // Add hours to journey
    addHours(journeyId.value, newEntry.value.duration_minutes / 60)

    toast.add({
      title: 'Success',
      description: 'Activity logged!',
      color: 'green',
    })
    showLogModal.value = false
    resetForm()
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to log activity',
      color: 'red',
    })
  }
}

const resetForm = () => {
  newEntry.value = {
    journey_id: journeyId.value,
    date: new Date().toISOString().split('T')[0],
    duration_minutes: 60,
    activity: '',
    notes: '',
  }
}

const getProgressPercent = computed(() => {
  if (!journey.value?.target_hours) return 0
  return Math.min(100, (journey.value.logged_hours / journey.value.target_hours) * 100)
})

const completedMilestones = computed(() =>
  journey.value?.milestones.filter(m => m.completed).length || 0
)

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
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
</script>

<template>
  <div v-if="journey" class="space-y-8">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div class="flex items-center gap-3 sm:gap-4">
        <NuxtLink to="/skills/journeys" class="p-2 rounded-lg hover:bg-card-black transition-colors">
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5 text-pure-white/60" />
        </NuxtLink>
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">{{ journey.name }}</h1>
          <p class="mt-1 text-sm sm:text-base text-pure-white/60 capitalize">{{ journey.category }}</p>
        </div>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        size="sm"
        variant="primary"
        @click="showLogModal = true"
      >
        Log Activity
      </BaseButton>
    </header>

    <!-- Progress Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-card-black border border-border-gray rounded-lg p-6">
        <p class="text-sm text-pure-white/60 mb-2">Hours Logged</p>
        <p class="text-3xl font-bold text-cyber-blue">{{ journey.logged_hours }}h</p>
        <p v-if="journey.target_hours" class="text-sm text-pure-white/40">of {{ journey.target_hours }}h goal</p>
      </div>

      <div class="bg-card-black border border-border-gray rounded-lg p-6">
        <p class="text-sm text-pure-white/60 mb-2">Progress</p>
        <p class="text-3xl font-bold text-electric-green">{{ getProgressPercent.toFixed(0) }}%</p>
        <div class="mt-2 h-2 bg-border-gray rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-cyber-blue to-electric-green rounded-full"
            :style="{ width: `${getProgressPercent}%` }"
          />
        </div>
      </div>

      <div class="bg-card-black border border-border-gray rounded-lg p-6">
        <p class="text-sm text-pure-white/60 mb-2">Milestones</p>
        <p class="text-3xl font-bold text-warning-orange">
          {{ completedMilestones }}/{{ journey.milestones.length }}
        </p>
        <p class="text-sm text-pure-white/40">completed</p>
      </div>
    </div>

    <!-- Milestones Section -->
    <div class="bg-card-black border border-border-gray rounded-lg p-6">
      <h2 class="text-xl font-semibold text-pure-white mb-4">Milestones</h2>

      <div v-if="journey.milestones.length > 0" class="space-y-3">
        <div
          v-for="milestone in journey.milestones"
          :key="milestone.id"
          class="flex items-center gap-4 p-3 bg-background-black rounded-lg hover:bg-background-black/80 transition-colors cursor-pointer"
          @click="handleToggleMilestone(milestone.id)"
        >
          <div
            class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors"
            :class="milestone.completed
              ? 'bg-electric-green border-electric-green'
              : 'border-border-gray hover:border-cyber-blue'"
          >
            <UIcon v-if="milestone.completed" name="i-heroicons-check" class="w-4 h-4 text-background-black" />
          </div>
          <div class="flex-1">
            <p
              class="font-medium"
              :class="milestone.completed ? 'text-pure-white/60 line-through' : 'text-pure-white'"
            >
              {{ milestone.title }}
            </p>
            <p v-if="milestone.completed_at" class="text-xs text-pure-white/40">
              Completed {{ formatDate(milestone.completed_at) }}
            </p>
          </div>
        </div>
      </div>

      <p v-else class="text-center text-pure-white/40 py-4">No milestones set for this journey</p>
    </div>

    <!-- Activity Log -->
    <div class="bg-card-black border border-border-gray rounded-lg p-6">
      <h2 class="text-xl font-semibold text-pure-white mb-4">Activity Log</h2>

      <div v-if="journeyEntries.length > 0" class="space-y-3">
        <div
          v-for="entry in journeyEntries"
          :key="entry.id"
          class="p-4 bg-background-black rounded-lg"
        >
          <div class="flex items-start justify-between mb-2">
            <p class="font-medium text-pure-white">{{ entry.activity }}</p>
            <span class="text-sm font-semibold text-cyber-blue">{{ formatDuration(entry.duration_minutes) }}</span>
          </div>
          <p v-if="entry.notes" class="text-sm text-pure-white/60 mb-2">{{ entry.notes }}</p>
          <p class="text-xs text-pure-white/40">{{ formatDate(entry.date) }}</p>
        </div>
      </div>

      <div v-else class="text-center py-8">
        <UIcon name="i-heroicons-clipboard-document-list" class="w-12 h-12 mx-auto text-pure-white/40 mb-3" />
        <p class="text-pure-white/60">No activity logged yet</p>
        <BaseButton variant="primary" class="mt-4" @click="showLogModal = true">
          Log Your First Activity
        </BaseButton>
      </div>
    </div>

    <!-- Log Activity Modal -->
    <BaseModal v-model="showLogModal" title="Log Activity" max-width="lg">
      <form @submit.prevent="handleLogActivity" class="space-y-4">
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

        <div class="flex justify-end gap-3 pt-4">
          <BaseButton type="button" variant="secondary" @click="showLogModal = false">
            Cancel
          </BaseButton>
          <BaseButton type="submit" variant="primary">
            Log Activity
          </BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>

  <div v-else class="text-center py-12">
    <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 mx-auto text-warning-orange mb-4" />
    <p class="text-pure-white/60">Journey not found</p>
    <NuxtLink to="/skills/journeys">
      <BaseButton variant="primary" class="mt-4">Back to Journeys</BaseButton>
    </NuxtLink>
  </div>
</template>
