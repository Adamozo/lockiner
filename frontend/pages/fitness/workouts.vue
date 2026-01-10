<script setup lang="ts">
import type { Workout, WorkoutCreate } from '~/types/fitness'
import { exerciseLibrary } from '~/composables/useFitnessMockData'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Workouts - LockIner',
  description: 'Log and manage your gym workouts',
})

const { workouts, loading, fetchWorkouts, createWorkout, deleteWorkout } = useWorkouts()
const toast = useToast()

// UI state
const showAddModal = ref(false)
const newWorkout = ref<WorkoutCreate>({
  date: new Date().toISOString().split('T')[0],
  name: '',
  exercises: [],
  duration_minutes: 60,
  notes: '',
})

onMounted(async () => {
  await fetchWorkouts()
})

const addExercise = () => {
  newWorkout.value.exercises.push({
    name: '',
    sets: 3,
    reps: 10,
    weight_kg: 0,
    rest_seconds: 60,
  })
}

const removeExercise = (index: number) => {
  newWorkout.value.exercises.splice(index, 1)
}

const handleAddWorkout = async () => {
  if (!newWorkout.value.name || newWorkout.value.exercises.length === 0) {
    toast.add({
      title: 'Error',
      description: 'Please add a name and at least one exercise',
      color: 'red',
    })
    return
  }

  try {
    await createWorkout(newWorkout.value)
    toast.add({
      title: 'Success',
      description: 'Workout logged successfully!',
      color: 'green',
    })
    showAddModal.value = false
    resetForm()
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to log workout',
      color: 'red',
    })
  }
}

const handleDelete = async (id: number) => {
  if (!confirm('Are you sure you want to delete this workout?')) return

  try {
    await deleteWorkout(id)
    toast.add({
      title: 'Success',
      description: 'Workout deleted',
      color: 'green',
    })
  } catch (e) {
    toast.add({
      title: 'Error',
      description: 'Failed to delete workout',
      color: 'red',
    })
  }
}

const resetForm = () => {
  newWorkout.value = {
    date: new Date().toISOString().split('T')[0],
    name: '',
    exercises: [],
    duration_minutes: 60,
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

const workoutTemplates = [
  { name: 'Push Day', icon: 'i-heroicons-arrow-up' },
  { name: 'Pull Day', icon: 'i-heroicons-arrow-down' },
  { name: 'Leg Day', icon: 'i-heroicons-bolt' },
  { name: 'Upper Body', icon: 'i-heroicons-user' },
  { name: 'Full Body', icon: 'i-heroicons-fire' },
]
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Workouts</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">Log and track your gym sessions</p>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        size="sm"
        variant="primary"
        @click="showAddModal = true"
      >
        Log Workout
      </BaseButton>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-warning-orange animate-spin" />
    </div>

    <!-- Workouts list -->
    <div v-else-if="workouts.length > 0" class="space-y-4">
      <div
        v-for="workout in workouts"
        :key="workout.id"
        class="bg-card-black border border-border-gray rounded-lg overflow-hidden hover:border-warning-orange/50 transition-colors"
      >
        <div class="p-4 border-b border-border-gray">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="p-3 bg-warning-orange/10 rounded-lg">
                <UIcon name="i-heroicons-fire" class="w-6 h-6 text-warning-orange" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-pure-white">{{ workout.name }}</h3>
                <p class="text-sm text-pure-white/60">{{ formatDate(workout.date) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="text-right">
                <p class="text-sm font-medium text-pure-white">{{ workout.duration_minutes }} min</p>
                <p class="text-xs text-pure-white/40">{{ workout.exercises.length }} exercises</p>
              </div>
              <BaseButton
                variant="danger"
                size="sm"
                icon="i-heroicons-trash"
                @click="handleDelete(workout.id)"
              />
            </div>
          </div>
        </div>

        <!-- Exercises -->
        <div class="p-4 bg-background-black/50">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="exercise in workout.exercises"
              :key="exercise.id"
              class="flex items-center gap-3 p-3 bg-card-black rounded-lg"
            >
              <UIcon name="i-heroicons-bolt" class="w-4 h-4 text-warning-orange" />
              <div class="flex-1">
                <p class="text-sm font-medium text-pure-white">{{ exercise.name }}</p>
                <p class="text-xs text-pure-white/60">
                  {{ exercise.sets }}x{{ exercise.reps }} @ {{ exercise.weight_kg }}kg
                </p>
              </div>
            </div>
          </div>
          <p v-if="workout.notes" class="mt-3 text-sm text-pure-white/60 italic">
            "{{ workout.notes }}"
          </p>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="bg-card-black border border-border-gray rounded-lg p-12 text-center">
      <UIcon name="i-heroicons-fire" class="w-16 h-16 mx-auto text-pure-white/40 mb-4" />
      <h3 class="text-lg font-semibold text-pure-white mb-2">No workouts yet</h3>
      <p class="text-pure-white/60 mb-6">Start logging your gym sessions to track progress</p>
      <BaseButton variant="primary" icon="i-heroicons-plus" @click="showAddModal = true">
        Log Your First Workout
      </BaseButton>
    </div>

    <!-- Add Workout Modal -->
    <BaseModal v-model="showAddModal" title="Log Workout" max-width="3xl">
      <form @submit.prevent="handleAddWorkout" class="space-y-6">
        <!-- Basic Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Date</label>
            <input
              v-model="newWorkout.date"
              type="date"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Workout Name</label>
            <select
              v-model="newWorkout.name"
              class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
            >
              <option value="">Select or type...</option>
              <option v-for="t in workoutTemplates" :key="t.name" :value="t.name">{{ t.name }}</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Duration (minutes)</label>
          <input
            v-model.number="newWorkout.duration_minutes"
            type="number"
            min="1"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>

        <!-- Exercises -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <label class="text-sm font-medium text-pure-white">Exercises</label>
            <BaseButton type="button" variant="secondary" size="sm" icon="i-heroicons-plus" @click="addExercise">
              Add Exercise
            </BaseButton>
          </div>

          <div v-if="newWorkout.exercises.length > 0" class="space-y-3">
            <div
              v-for="(exercise, index) in newWorkout.exercises"
              :key="index"
              class="p-4 bg-background-black rounded-lg border border-border-gray"
            >
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-medium text-pure-white/60">Exercise {{ index + 1 }}</span>
                <button
                  type="button"
                  class="text-danger-red hover:text-danger-red/80"
                  @click="removeExercise(index)"
                >
                  <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                </button>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div class="col-span-2 md:col-span-1">
                  <select
                    v-model="exercise.name"
                    class="w-full px-3 py-2 text-sm border border-border-gray rounded-lg bg-card-black text-pure-white focus:border-warning-orange focus:outline-none"
                  >
                    <option value="">Select exercise</option>
                    <option v-for="ex in exerciseLibrary" :key="ex" :value="ex">{{ ex }}</option>
                  </select>
                </div>
                <div>
                  <input
                    v-model.number="exercise.sets"
                    type="number"
                    min="1"
                    placeholder="Sets"
                    class="w-full px-3 py-2 text-sm border border-border-gray rounded-lg bg-card-black text-pure-white focus:border-warning-orange focus:outline-none"
                  />
                  <span class="text-xs text-pure-white/40">sets</span>
                </div>
                <div>
                  <input
                    v-model.number="exercise.reps"
                    type="number"
                    min="1"
                    placeholder="Reps"
                    class="w-full px-3 py-2 text-sm border border-border-gray rounded-lg bg-card-black text-pure-white focus:border-warning-orange focus:outline-none"
                  />
                  <span class="text-xs text-pure-white/40">reps</span>
                </div>
                <div>
                  <input
                    v-model.number="exercise.weight_kg"
                    type="number"
                    min="0"
                    step="0.5"
                    placeholder="Weight"
                    class="w-full px-3 py-2 text-sm border border-border-gray rounded-lg bg-card-black text-pure-white focus:border-warning-orange focus:outline-none"
                  />
                  <span class="text-xs text-pure-white/40">kg</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="p-6 border-2 border-dashed border-border-gray rounded-lg text-center">
            <p class="text-pure-white/40">Click "Add Exercise" to start logging</p>
          </div>
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">Notes (optional)</label>
          <textarea
            v-model="newWorkout.notes"
            rows="2"
            placeholder="How did it feel?"
            class="w-full px-4 py-2 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none"
          />
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-4 border-t border-border-gray">
          <BaseButton type="button" variant="secondary" @click="showAddModal = false">
            Cancel
          </BaseButton>
          <BaseButton type="submit" variant="primary" :loading="loading">
            Log Workout
          </BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
