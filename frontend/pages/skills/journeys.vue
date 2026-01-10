<script setup lang="ts">
import type { JourneyCreate } from '~/types/skills'
import { categoryOptions } from '~/composables/useSkillsMockData'

definePageMeta({
  layout: 'skills',
})

useSeoMeta({
  title: 'Learning Journeys - LockIner',
  description: 'Manage your learning journeys and skill development paths',
})

const { journeys, loading, fetchJourneys, createJourney, deleteJourney } = useJourneys()
const toast = useToast()

// UI state
const showAddModal = ref(false)
const newJourney = ref<JourneyCreate>({
  name: '',
  description: '',
  category: 'programming',
  target_hours: 50,
  milestones: [],
})
const newMilestone = ref('')

onMounted(async () => {
  await fetchJourneys()
})

const addMilestone = () => {
  if (newMilestone.value.trim()) {
    if (!newJourney.value.milestones) {
      newJourney.value.milestones = []
    }
    newJourney.value.milestones.push(newMilestone.value.trim())
    newMilestone.value = ''
  }
}

const removeMilestone = (index: number) => {
  newJourney.value.milestones?.splice(index, 1)
}

const handleAddJourney = async () => {
  if (!newJourney.value.name) {
    toast.add({
      title: 'Error',
      description: 'Please enter a journey name',
      color: 'red',
    })
    return
  }

  try {
    await createJourney(newJourney.value)
    toast.add({
      title: 'Success',
      description: 'Learning journey created!',
      color: 'green',
    })
    showAddModal.value = false
    resetForm()
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to create journey',
      color: 'red',
    })
  }
}

const handleDelete = async (id: number) => {
  if (!confirm('Delete this learning journey?')) return

  try {
    await deleteJourney(id)
    toast.add({
      title: 'Success',
      description: 'Journey deleted',
      color: 'green',
    })
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to delete journey',
      color: 'red',
    })
  }
}

const resetForm = () => {
  newJourney.value = {
    name: '',
    description: '',
    category: 'programming',
    target_hours: 50,
    milestones: [],
  }
  newMilestone.value = ''
}

const getProgressPercent = (journey: any) => {
  if (!journey.target_hours) return 0
  return Math.min(100, (journey.logged_hours / journey.target_hours) * 100)
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'text-electric-green'
    case 'paused': return 'text-warning-orange'
    case 'completed': return 'text-cyber-blue'
    default: return 'text-pure-white/60'
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Learning Journeys</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">Track your skill development paths</p>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        size="sm"
        variant="primary"
        @click="showAddModal = true"
      >
        New Journey
      </BaseButton>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-cyber-blue animate-spin" />
    </div>

    <!-- Journeys grid -->
    <div v-else-if="journeys.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="journey in journeys"
        :key="journey.id"
        class="bg-card-black border border-border-gray rounded-lg overflow-hidden hover:border-cyber-blue/50 transition-colors"
      >
        <!-- Header -->
        <div class="p-4 border-b border-border-gray">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-cyber-blue/10 rounded-lg">
                <UIcon :name="journey.icon || 'i-heroicons-academic-cap'" class="w-6 h-6 text-cyber-blue" />
              </div>
              <div>
                <NuxtLink :to="`/skills/journey/${journey.id}`" class="font-semibold text-pure-white hover:text-cyber-blue transition-colors">
                  {{ journey.name }}
                </NuxtLink>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-xs text-pure-white/60 capitalize">{{ journey.category }}</span>
                  <span class="text-xs" :class="getStatusColor(journey.status)">
                    {{ journey.status }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <NuxtLink :to="`/skills/journey/${journey.id}`">
                <BaseButton variant="secondary" size="sm" icon="i-heroicons-eye" />
              </NuxtLink>
              <BaseButton
                variant="danger"
                size="sm"
                icon="i-heroicons-trash"
                @click="handleDelete(journey.id)"
              />
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="p-4">
          <p v-if="journey.description" class="text-sm text-pure-white/60 mb-4">
            {{ journey.description }}
          </p>

          <!-- Progress -->
          <div class="mb-4">
            <div class="flex justify-between text-sm text-pure-white/60 mb-2">
              <span>Progress</span>
              <span>{{ journey.logged_hours }}h / {{ journey.target_hours || '∞' }}h</span>
            </div>
            <div class="h-2 bg-border-gray rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-cyber-blue to-electric-green rounded-full transition-all"
                :style="{ width: `${getProgressPercent(journey)}%` }"
              />
            </div>
          </div>

          <!-- Milestones -->
          <div class="flex items-center justify-between text-sm">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-flag" class="w-4 h-4 text-pure-white/40" />
              <span class="text-pure-white/60">
                {{ journey.milestones.filter(m => m.completed).length }}/{{ journey.milestones.length }} milestones
              </span>
            </div>
            <span class="text-pure-white/40">Started {{ formatDate(journey.started_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="bg-card-black border border-border-gray rounded-lg p-12 text-center">
      <UIcon name="i-heroicons-academic-cap" class="w-16 h-16 mx-auto text-pure-white/40 mb-4" />
      <h3 class="text-lg font-semibold text-pure-white mb-2">No learning journeys yet</h3>
      <p class="text-pure-white/60 mb-6">Start tracking your skill development</p>
      <BaseButton variant="primary" icon="i-heroicons-plus" @click="showAddModal = true">
        Create Your First Journey
      </BaseButton>
    </div>

    <!-- Add Journey Modal -->
    <BaseModal v-model="showAddModal" title="Create Learning Journey" max-width="2xl">
      <form @submit.prevent="handleAddJourney" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Journey Name</label>
          <input
            v-model="newJourney.name"
            type="text"
            placeholder="e.g., Learn Python, Master SQL..."
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Description (optional)</label>
          <textarea
            v-model="newJourney.description"
            rows="2"
            placeholder="What do you want to achieve?"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Category</label>
            <select
              v-model="newJourney.category"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
            >
              <option v-for="cat in categoryOptions" :key="cat.value" :value="cat.value">
                {{ cat.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Target Hours</label>
            <input
              v-model.number="newJourney.target_hours"
              type="number"
              min="1"
              placeholder="50"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
            />
          </div>
        </div>

        <!-- Milestones -->
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Milestones</label>
          <div class="flex gap-2 mb-2">
            <input
              v-model="newMilestone"
              type="text"
              placeholder="Add a milestone..."
              class="flex-1 px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:outline-none"
              @keyup.enter="addMilestone"
            />
            <BaseButton type="button" variant="secondary" icon="i-heroicons-plus" @click="addMilestone" />
          </div>

          <div v-if="newJourney.milestones && newJourney.milestones.length > 0" class="space-y-2">
            <div
              v-for="(milestone, index) in newJourney.milestones"
              :key="index"
              class="flex items-center justify-between p-2 bg-background-black rounded-lg"
            >
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-flag" class="w-4 h-4 text-cyber-blue" />
                <span class="text-sm text-pure-white">{{ milestone }}</span>
              </div>
              <button
                type="button"
                class="text-danger-red hover:text-danger-red/80"
                @click="removeMilestone(index)"
              >
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
              </button>
            </div>
          </div>
          <p v-else class="text-sm text-pure-white/40">No milestones added yet</p>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-border-gray">
          <BaseButton type="button" variant="secondary" @click="showAddModal = false">
            Cancel
          </BaseButton>
          <BaseButton type="submit" variant="primary" :loading="loading">
            Create Journey
          </BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
