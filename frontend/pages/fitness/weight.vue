<script setup lang="ts">
import type { WeightEntryCreate } from '~/types/fitness'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Weight Tracking - LockIner',
  description: 'Track your body weight and progress',
})

const { sortedEntries, currentWeight, weightChange, chartData, loading, fetchEntries, addEntry, deleteEntry } = useWeight()
const toast = useToast()

// UI state
const showAddModal = ref(false)
const newEntry = ref<WeightEntryCreate>({
  date: new Date().toISOString().split('T')[0],
  weight_kg: 0,
  body_fat_percentage: undefined,
  notes: '',
})

onMounted(async () => {
  await fetchEntries()
})

const handleAddEntry = async () => {
  if (!newEntry.value.weight_kg) {
    toast.add({
      title: 'Error',
      description: 'Please enter your weight',
      color: 'red',
    })
    return
  }

  try {
    await addEntry(newEntry.value)
    toast.add({
      title: 'Success',
      description: 'Weight entry added!',
      color: 'green',
    })
    showAddModal.value = false
    resetForm()
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to add entry',
      color: 'red',
    })
  }
}

const handleDelete = async (id: number) => {
  if (!confirm('Delete this weight entry?')) return

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
    date: new Date().toISOString().split('T')[0],
    weight_kg: currentWeight.value || 0,
    body_fat_percentage: undefined,
    notes: '',
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
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
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Weight Tracking</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">Monitor your body weight over time</p>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        size="sm"
        variant="primary"
        @click="showAddModal = true; resetForm()"
      >
        Add Entry
      </BaseButton>
    </header>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Current Weight -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-warning-orange to-electric-green"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Current Weight</p>
            <p class="mt-2 text-3xl font-bold text-warning-orange">
              {{ currentWeight ? `${currentWeight} kg` : 'N/A' }}
            </p>
          </div>
          <div class="p-3 bg-gradient-to-br from-warning-orange/20 to-warning-orange/5 rounded-full border border-warning-orange/30">
            <UIcon name="i-heroicons-scale" class="w-8 h-8 text-warning-orange" />
          </div>
        </div>
      </div>

      <!-- Weight Change -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Total Change</p>
            <p
              class="mt-2 text-3xl font-bold"
              :class="weightChange !== null && weightChange <= 0 ? 'text-electric-green' : 'text-danger-red'"
            >
              {{ weightChange !== null ? `${weightChange > 0 ? '+' : ''}${weightChange.toFixed(1)} kg` : 'N/A' }}
            </p>
          </div>
          <div class="p-3 bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 rounded-full border border-cyber-blue/30">
            <UIcon
              :name="weightChange !== null && weightChange <= 0 ? 'i-heroicons-arrow-trending-down' : 'i-heroicons-arrow-trending-up'"
              class="w-8 h-8"
              :class="weightChange !== null && weightChange <= 0 ? 'text-electric-green' : 'text-danger-red'"
            />
          </div>
        </div>
      </div>

      <!-- Entries Count -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-electric-green to-cyber-blue"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Total Entries</p>
            <p class="mt-2 text-3xl font-bold text-electric-green">
              {{ sortedEntries.length }}
            </p>
          </div>
          <div class="p-3 bg-gradient-to-br from-electric-green/20 to-electric-green/5 rounded-full border border-electric-green/30">
            <UIcon name="i-heroicons-clipboard-document-list" class="w-8 h-8 text-electric-green" />
          </div>
        </div>
      </div>
    </div>

    <!-- Weight Chart Placeholder -->
    <div class="bg-card-black border border-border-gray rounded-lg p-6">
      <h2 class="text-xl font-semibold text-pure-white mb-4">Weight Over Time</h2>
      <div v-if="chartData.weights.length > 1" class="h-64 flex items-end gap-2">
        <!-- Simple bar chart visualization -->
        <div
          v-for="(weight, index) in chartData.weights"
          :key="index"
          class="flex-1 flex flex-col items-center"
        >
          <span class="text-xs text-pure-white/60 mb-1">{{ weight }}kg</span>
          <div
            class="w-full bg-gradient-to-t from-warning-orange to-warning-orange/50 rounded-t-sm transition-all"
            :style="{
              height: `${((weight - Math.min(...chartData.weights) + 1) / (Math.max(...chartData.weights) - Math.min(...chartData.weights) + 2)) * 100}%`,
              minHeight: '20px'
            }"
          />
          <span class="text-xs text-pure-white/40 mt-1 truncate w-full text-center">
            {{ chartData.labels[index].slice(5) }}
          </span>
        </div>
      </div>
      <div v-else class="h-64 flex items-center justify-center">
        <p class="text-pure-white/40">Add more entries to see the chart</p>
      </div>
    </div>

    <!-- Entries list -->
    <div>
      <h2 class="text-xl font-semibold text-pure-white mb-4">History</h2>

      <div v-if="sortedEntries.length > 0" class="space-y-3">
        <div
          v-for="entry in sortedEntries"
          :key="entry.id"
          class="bg-card-black border border-border-gray rounded-lg p-4 flex items-center justify-between hover:border-warning-orange/50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="p-2 bg-warning-orange/10 rounded-lg">
              <UIcon name="i-heroicons-scale" class="w-5 h-5 text-warning-orange" />
            </div>
            <div>
              <p class="font-semibold text-pure-white">{{ entry.weight_kg }} kg</p>
              <p class="text-sm text-pure-white/60">{{ formatDate(entry.date) }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div v-if="entry.body_fat_percentage" class="text-right">
              <p class="text-sm text-pure-white">{{ entry.body_fat_percentage }}%</p>
              <p class="text-xs text-pure-white/40">body fat</p>
            </div>
            <BaseButton
              variant="danger"
              size="sm"
              icon="i-heroicons-trash"
              @click="handleDelete(entry.id)"
            />
          </div>
        </div>
      </div>

      <div v-else class="bg-card-black border border-border-gray rounded-lg p-8 text-center">
        <UIcon name="i-heroicons-scale" class="w-12 h-12 mx-auto text-pure-white/40 mb-3" />
        <p class="text-pure-white/60">No weight entries yet</p>
      </div>
    </div>

    <!-- Add Entry Modal -->
    <BaseModal v-model="showAddModal" title="Add Weight Entry" max-width="lg">
      <form @submit.prevent="handleAddEntry" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Date</label>
          <input
            v-model="newEntry.date"
            type="date"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Weight (kg)</label>
          <input
            v-model.number="newEntry.weight_kg"
            type="number"
            step="0.1"
            min="0"
            placeholder="82.5"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Body Fat % (optional)</label>
          <input
            v-model.number="newEntry.body_fat_percentage"
            type="number"
            step="0.1"
            min="0"
            max="100"
            placeholder="15.0"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Notes (optional)</label>
          <input
            v-model="newEntry.notes"
            type="text"
            placeholder="Morning weight, after workout..."
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <BaseButton type="button" variant="secondary" @click="showAddModal = false">
            Cancel
          </BaseButton>
          <BaseButton type="submit" variant="primary" :loading="loading">
            Add Entry
          </BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
