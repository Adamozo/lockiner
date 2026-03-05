<script setup lang="ts">
import type { WeightEntryCreate } from '~/types/fitness'
import type { BodyMeasurementEntryCreate } from '~/types/fitness'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Body Measurements - LockIner',
  description: 'Track your body weight, height, and circumference measurements',
})

// Composables
const { sortedEntries, currentWeight, weightChange, chartData, loading: weightLoading, fetchEntries, addEntry, deleteEntry } = useWeight()
const { sortedMeasurements, latestMeasurements, bodyProfile, loading: measurementLoading, fetchMeasurements, addMeasurement, deleteMeasurement, fetchBodyProfile, updateBodyProfile } = useBodyMeasurements()
const toast = useToast()

// --- Height profile ---
const editingHeight = ref(false)
const heightInput = ref<number | null>(null)

const startEditHeight = () => {
  heightInput.value = bodyProfile.value?.height_cm ?? null
  editingHeight.value = true
}

const saveHeight = async () => {
  if (!heightInput.value || heightInput.value <= 0) {
    toast.add({ title: 'Error', description: 'Please enter a valid height', color: 'red' })
    return
  }
  try {
    await updateBodyProfile(heightInput.value)
    editingHeight.value = false
    toast.add({ title: 'Success', description: 'Height updated', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to update height', color: 'red' })
  }
}

// BMI computed
const bmi = computed(() => {
  const height = bodyProfile.value?.height_cm
  const weight = currentWeight.value
  if (!height || !weight) return null
  const heightM = height / 100
  return (weight / (heightM * heightM)).toFixed(1)
})

// --- Weight modal ---
const showWeightModal = ref(false)
const newWeightEntry = ref<WeightEntryCreate>({
  date: new Date().toISOString().split('T')[0],
  weight_kg: 0,
  body_fat_percentage: undefined,
  notes: '',
})

const handleAddWeight = async () => {
  if (!newWeightEntry.value.weight_kg) {
    toast.add({ title: 'Error', description: 'Please enter your weight', color: 'red' })
    return
  }
  try {
    await addEntry(newWeightEntry.value)
    toast.add({ title: 'Success', description: 'Weight entry added!', color: 'green' })
    showWeightModal.value = false
    resetWeightForm()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to add weight entry', color: 'red' })
  }
}

const resetWeightForm = () => {
  newWeightEntry.value = {
    date: new Date().toISOString().split('T')[0],
    weight_kg: currentWeight.value || 0,
    body_fat_percentage: undefined,
    notes: '',
  }
}

const { confirm } = useConfirm()

const handleDeleteWeight = async (id: number) => {
  if (!await confirm({ message: 'Delete this weight entry?', confirmText: 'Delete' })) return
  try {
    await deleteEntry(id)
    toast.add({ title: 'Success', description: 'Entry deleted', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete entry', color: 'red' })
  }
}

// --- Measurements modal ---
const showMeasurementsModal = ref(false)
const newMeasurement = ref<BodyMeasurementEntryCreate>({
  date: new Date().toISOString().split('T')[0],
  bicep_cm: undefined,
  waist_cm: undefined,
  thigh_cm: undefined,
  calf_cm: undefined,
  chest_cm: undefined,
  notes: '',
})

const handleAddMeasurement = async () => {
  const hasValue = [
    newMeasurement.value.bicep_cm,
    newMeasurement.value.waist_cm,
    newMeasurement.value.thigh_cm,
    newMeasurement.value.calf_cm,
    newMeasurement.value.chest_cm,
  ].some(v => v != null && v > 0)

  if (!hasValue) {
    toast.add({ title: 'Error', description: 'Please enter at least one measurement', color: 'red' })
    return
  }
  try {
    await addMeasurement(newMeasurement.value)
    toast.add({ title: 'Success', description: 'Measurements added!', color: 'green' })
    showMeasurementsModal.value = false
    resetMeasurementForm()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to add measurements', color: 'red' })
  }
}

const resetMeasurementForm = () => {
  newMeasurement.value = {
    date: new Date().toISOString().split('T')[0],
    bicep_cm: undefined,
    waist_cm: undefined,
    thigh_cm: undefined,
    calf_cm: undefined,
    chest_cm: undefined,
    notes: '',
  }
}

const handleDeleteMeasurement = async (id: number) => {
  if (!await confirm({ message: 'Delete this measurement entry?', confirmText: 'Delete' })) return
  try {
    await deleteMeasurement(id)
    toast.add({ title: 'Success', description: 'Entry deleted', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete entry', color: 'red' })
  }
}

// Load data
onMounted(async () => {
  await Promise.all([fetchEntries(), fetchMeasurements(), fetchBodyProfile()])
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

// Circumference fields config
const circumferenceFields = [
  { key: 'bicep_cm' as const, label: 'Bicep', icon: 'i-heroicons-arrow-up-circle', color: 'text-cyber-blue' },
  { key: 'waist_cm' as const, label: 'Waist', icon: 'i-heroicons-minus-circle', color: 'text-warning-orange' },
  { key: 'thigh_cm' as const, label: 'Thigh', icon: 'i-heroicons-arrow-down-circle', color: 'text-electric-green' },
  { key: 'calf_cm' as const, label: 'Calf', icon: 'i-heroicons-arrow-down-circle', color: 'text-cyber-blue' },
  { key: 'chest_cm' as const, label: 'Chest', icon: 'i-heroicons-heart', color: 'text-warning-orange' },
]
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Body Measurements</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">Track your body composition over time</p>
      </div>
      <div class="flex gap-2">
        <BaseButton icon="i-heroicons-scale" size="sm" variant="secondary" @click="showWeightModal = true; resetWeightForm()">
          Add Weight
        </BaseButton>
        <BaseButton icon="i-heroicons-plus" size="sm" variant="primary" @click="showMeasurementsModal = true; resetMeasurementForm()">
          Add Measurements
        </BaseButton>
      </div>
    </header>

    <!-- Height Profile Card -->
    <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
      <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"></div>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="p-3 bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 rounded-full border border-cyber-blue/30">
            <UIcon name="i-heroicons-user" class="w-7 h-7 text-cyber-blue" />
          </div>
          <div>
            <p class="text-sm font-medium text-pure-white/60">Height</p>
            <div v-if="!editingHeight" class="flex items-center gap-3">
              <p class="text-2xl font-bold text-cyber-blue">
                {{ bodyProfile?.height_cm ? `${bodyProfile.height_cm} cm` : 'Not set' }}
              </p>
              <button
                class="text-pure-white/40 hover:text-pure-white transition-colors"
                @click="startEditHeight"
              >
                <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
              </button>
            </div>
            <div v-else class="flex items-center gap-2 mt-1">
              <input
                v-model.number="heightInput"
                type="number"
                step="0.1"
                min="50"
                max="300"
                placeholder="180"
                class="w-28 px-3 py-1 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none text-sm"
                @keyup.enter="saveHeight"
                @keyup.escape="editingHeight = false"
              />
              <span class="text-pure-white/60 text-sm">cm</span>
              <BaseButton size="sm" variant="primary" @click="saveHeight">Save</BaseButton>
              <BaseButton size="sm" variant="secondary" @click="editingHeight = false">Cancel</BaseButton>
            </div>
          </div>
        </div>
        <div v-if="bmi" class="text-right">
          <p class="text-sm text-pure-white/60">BMI</p>
          <p class="text-2xl font-bold text-electric-green">{{ bmi }}</p>
        </div>
      </div>
    </div>

    <!-- Stats Row -->
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
            <p class="text-sm font-medium text-pure-white/60">Weight Change</p>
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

      <!-- BMI or Measurement Count -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-electric-green to-cyber-blue"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">{{ bmi ? 'BMI' : 'Measurements Logged' }}</p>
            <p class="mt-2 text-3xl font-bold text-electric-green">
              {{ bmi || sortedMeasurements.length }}
            </p>
          </div>
          <div class="p-3 bg-gradient-to-br from-electric-green/20 to-electric-green/5 rounded-full border border-electric-green/30">
            <UIcon name="i-heroicons-clipboard-document-list" class="w-8 h-8 text-electric-green" />
          </div>
        </div>
      </div>
    </div>

    <!-- Weight Section -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-pure-white">Weight</h2>
      </div>

      <!-- Weight Chart -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6">
        <h3 class="text-base font-medium text-pure-white/80 mb-4">Weight Over Time</h3>
        <div v-if="chartData.weights.length > 1" class="h-48 flex items-end gap-2">
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
        <div v-else class="h-48 flex items-center justify-center">
          <p class="text-pure-white/40">Add more weight entries to see the chart</p>
        </div>
      </div>

      <!-- Weight History -->
      <div v-if="sortedEntries.length > 0" class="space-y-2">
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
            <BaseButton variant="danger" size="sm" icon="i-heroicons-trash" @click="handleDeleteWeight(entry.id)" />
          </div>
        </div>
      </div>
      <div v-else class="bg-card-black border border-border-gray rounded-lg p-8 text-center">
        <UIcon name="i-heroicons-scale" class="w-12 h-12 mx-auto text-pure-white/40 mb-3" />
        <p class="text-pure-white/60">No weight entries yet</p>
      </div>
    </div>

    <!-- Circumference Section -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-pure-white">Circumferences</h2>
      </div>

      <!-- Latest Measurements Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <div
          v-for="field in circumferenceFields"
          :key="field.key"
          class="bg-card-black border border-border-gray rounded-lg p-4 text-center"
        >
          <UIcon :name="field.icon" class="w-6 h-6 mx-auto mb-2" :class="field.color" />
          <p class="text-xs text-pure-white/60 mb-1">{{ field.label }}</p>
          <p class="text-lg font-bold" :class="latestMeasurements[field.key] ? field.color : 'text-pure-white/30'">
            {{ latestMeasurements[field.key] != null ? `${latestMeasurements[field.key]} cm` : '-' }}
          </p>
        </div>
      </div>

      <!-- Measurements History -->
      <div v-if="sortedMeasurements.length > 0" class="space-y-2">
        <div
          v-for="entry in sortedMeasurements"
          :key="entry.id"
          class="bg-card-black border border-border-gray rounded-lg p-4 hover:border-cyber-blue/50 transition-colors"
        >
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-cyber-blue/10 rounded-lg">
                <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5 text-cyber-blue" />
              </div>
              <p class="font-semibold text-pure-white">{{ formatDate(entry.date) }}</p>
            </div>
            <BaseButton variant="danger" size="sm" icon="i-heroicons-trash" @click="handleDeleteMeasurement(entry.id)" />
          </div>
          <div class="grid grid-cols-3 sm:grid-cols-5 gap-2 text-sm">
            <div v-if="entry.bicep_cm != null" class="text-center">
              <p class="text-pure-white/60 text-xs">Bicep</p>
              <p class="text-cyber-blue font-medium">{{ entry.bicep_cm }} cm</p>
            </div>
            <div v-if="entry.waist_cm != null" class="text-center">
              <p class="text-pure-white/60 text-xs">Waist</p>
              <p class="text-warning-orange font-medium">{{ entry.waist_cm }} cm</p>
            </div>
            <div v-if="entry.thigh_cm != null" class="text-center">
              <p class="text-pure-white/60 text-xs">Thigh</p>
              <p class="text-electric-green font-medium">{{ entry.thigh_cm }} cm</p>
            </div>
            <div v-if="entry.calf_cm != null" class="text-center">
              <p class="text-pure-white/60 text-xs">Calf</p>
              <p class="text-cyber-blue font-medium">{{ entry.calf_cm }} cm</p>
            </div>
            <div v-if="entry.chest_cm != null" class="text-center">
              <p class="text-pure-white/60 text-xs">Chest</p>
              <p class="text-warning-orange font-medium">{{ entry.chest_cm }} cm</p>
            </div>
          </div>
          <p v-if="entry.notes" class="mt-2 text-xs text-pure-white/40 italic">{{ entry.notes }}</p>
        </div>
      </div>
      <div v-else class="bg-card-black border border-border-gray rounded-lg p-8 text-center">
        <UIcon name="i-heroicons-clipboard-document-list" class="w-12 h-12 mx-auto text-pure-white/40 mb-3" />
        <p class="text-pure-white/60">No circumference measurements yet</p>
      </div>
    </div>

    <!-- Weight Modal -->
    <BaseModal v-model="showWeightModal" title="Add Weight Entry" max-width="lg">
      <form @submit.prevent="handleAddWeight" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Date</label>
          <input
            v-model="newWeightEntry.date"
            type="date"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Weight (kg)</label>
          <input
            v-model.number="newWeightEntry.weight_kg"
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
            v-model.number="newWeightEntry.body_fat_percentage"
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
            v-model="newWeightEntry.notes"
            type="text"
            placeholder="Morning weight, after workout..."
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <BaseButton type="button" variant="secondary" @click="showWeightModal = false">Cancel</BaseButton>
          <BaseButton type="submit" variant="primary" :loading="weightLoading">Add Weight</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Measurements Modal -->
    <BaseModal v-model="showMeasurementsModal" title="Add Circumference Measurements" max-width="lg">
      <form @submit.prevent="handleAddMeasurement" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Date</label>
          <input
            v-model="newMeasurement.date"
            type="date"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Bicep (cm)</label>
            <input
              v-model.number="newMeasurement.bicep_cm"
              type="number"
              step="0.1"
              min="0"
              placeholder="35.0"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Waist (cm)</label>
            <input
              v-model.number="newMeasurement.waist_cm"
              type="number"
              step="0.1"
              min="0"
              placeholder="80.0"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Thigh (cm)</label>
            <input
              v-model.number="newMeasurement.thigh_cm"
              type="number"
              step="0.1"
              min="0"
              placeholder="55.0"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-electric-green focus:ring-2 focus:ring-electric-green/30 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Calf (cm)</label>
            <input
              v-model.number="newMeasurement.calf_cm"
              type="number"
              step="0.1"
              min="0"
              placeholder="37.0"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Chest (cm)</label>
            <input
              v-model.number="newMeasurement.chest_cm"
              type="number"
              step="0.1"
              min="0"
              placeholder="95.0"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Notes (optional)</label>
          <input
            v-model="newMeasurement.notes"
            type="text"
            placeholder="Morning measurements..."
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
          />
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <BaseButton type="button" variant="secondary" @click="showMeasurementsModal = false">Cancel</BaseButton>
          <BaseButton type="submit" variant="primary" :loading="measurementLoading">Add Measurements</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
