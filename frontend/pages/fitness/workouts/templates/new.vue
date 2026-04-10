<script setup lang="ts">
import type { ExerciseSetCreate } from '~/types/fitness'
import type { WorkoutType } from '~/types/fitness'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'New Template - LockIner',
  description: 'Create a new workout template',
})

const router = useRouter()
const toast = useToast()
const { loading, createTemplate } = useWorkoutTemplates()

interface ExerciseFormData {
  name: string
  sets: number
  reps: number
  weight_kg: number
  rest_seconds?: number
  notes?: string
  sets_detail: ExerciseSetCreate[]
}

const workoutTypes: { name: WorkoutType; icon: string }[] = [
  { name: 'Push Day', icon: 'i-heroicons-arrow-up' },
  { name: 'Pull Day', icon: 'i-heroicons-arrow-down' },
  { name: 'Leg Day', icon: 'i-heroicons-bolt' },
  { name: 'Upper Body', icon: 'i-heroicons-user' },
  { name: 'Full Body', icon: 'i-heroicons-fire' },
  { name: 'Custom', icon: 'i-heroicons-pencil' },
]

const selectedType = ref<WorkoutType | ''>('')
const templateName = ref('')
const templateNotes = ref('')
const exercises = ref<ExerciseFormData[]>([])

const isCustom = computed(() => selectedType.value === 'Custom')

const selectType = (type: WorkoutType) => {
  selectedType.value = type
  if (type !== 'Custom') {
    templateName.value = type
  } else {
    templateName.value = ''
  }
}

const addExercise = () => {
  exercises.value.push({
    name: '',
    sets: 3,
    reps: 10,
    weight_kg: 0,
    sets_detail: [
      { set_number: 1, reps: 10, weight_kg: 0, completed: false },
    ],
  })
}

const updateExercise = (index: number, exercise: ExerciseFormData) => {
  exercises.value[index] = exercise
}

const removeExercise = (index: number) => {
  exercises.value.splice(index, 1)
}

const canSave = computed(() => {
  if (!templateName.value.trim()) return false
  if (!selectedType.value) return false
  if (exercises.value.length === 0) return false
  return exercises.value.every(e => e.name.trim() && e.sets_detail.length > 0)
})

const handleSave = async () => {
  if (!canSave.value) {
    toast.add({ title: 'Incomplete', description: 'Fill in name, type, and at least one exercise', color: 'red' })
    return
  }

  try {
    await createTemplate({
      name: templateName.value.trim(),
      workout_type: selectedType.value as WorkoutType,
      notes: templateNotes.value || undefined,
      exercises: exercises.value.map((e, i) => ({
        name: e.name || 'Unnamed Exercise',
        order_index: i,
        sets: e.sets_detail.length || e.sets,
        reps: e.sets_detail.length > 0 ? Math.max(...e.sets_detail.map(s => s.reps)) : e.reps,
        weight_kg: e.sets_detail.length > 0 ? Math.max(...e.sets_detail.map(s => s.weight_kg)) : e.weight_kg,
        rest_seconds: e.rest_seconds,
        notes: e.notes,
      })),
    })
    toast.add({ title: 'Template created', color: 'green' })
    router.push('/fitness/workouts/templates')
  } catch {
    toast.add({ title: 'Error', description: 'Failed to create template', color: 'red' })
  }
}
</script>

<template>
  <div class="pb-4 max-w-2xl mx-auto">
    <!-- Header -->
    <header class="flex items-center gap-4 mb-6">
      <button
        type="button"
        class="w-10 h-10 rounded-lg border border-border-gray flex items-center justify-center text-pure-white/60 hover:text-pure-white hover:border-pure-white/40 transition-colors"
        @click="router.push('/fitness/workouts/templates')"
      >
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </button>
      <h1 class="text-2xl font-bold text-pure-white">New Template</h1>
    </header>

    <!-- Save button -->
    <div class="flex gap-3 mb-6">
      <BaseButton
        variant="primary"
        class="w-full"
        :disabled="!canSave"
        :loading="loading"
        @click="handleSave"
      >
        Save Template
      </BaseButton>
    </div>

    <div class="space-y-6">
      <!-- Workout Type chips -->
      <div>
        <label class="block text-sm font-medium text-pure-white/60 mb-3">Workout Type</label>
        <div class="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-hide">
          <button
            v-for="t in workoutTypes"
            :key="t.name"
            type="button"
            class="flex-shrink-0 px-4 py-2.5 rounded-lg border text-sm font-medium transition-all flex items-center gap-2"
            :class="selectedType === t.name
              ? 'bg-warning-orange/20 border-warning-orange text-warning-orange'
              : 'border-border-gray text-pure-white/60 hover:border-pure-white/40 hover:text-pure-white'"
            @click="selectType(t.name)"
          >
            <UIcon :name="t.icon" class="w-4 h-4" />
            {{ t.name }}
          </button>
        </div>
      </div>

      <!-- Custom name input -->
      <div v-if="isCustom">
        <label class="block text-sm font-medium text-pure-white/60 mb-2">Template Name</label>
        <input
          v-model="templateName"
          type="text"
          placeholder="e.g., Morning HIIT, Chest & Triceps..."
          class="w-full min-h-12 px-4 py-3 rounded-lg border bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors border-border-gray"
        />
      </div>

      <!-- Exercises section -->
      <div>
        <label class="block text-sm font-medium text-pure-white/60 mb-3">Exercises</label>

        <div v-if="exercises.length > 0" class="space-y-4">
          <WorkoutExerciseCard
            v-for="(exercise, index) in exercises"
            :key="index"
            :model-value="exercise"
            :exercise-index="index"
            @update:model-value="updateExercise(index, $event)"
            @delete="removeExercise(index)"
          />
        </div>

        <div v-else class="p-8 border-2 border-dashed border-border-gray rounded-lg text-center">
          <UIcon name="i-heroicons-plus-circle" class="w-10 h-10 mx-auto text-pure-white/20 mb-3" />
          <p class="text-pure-white/40 text-sm">Add exercises to your template</p>
        </div>

        <div class="mt-4 flex justify-center">
          <button
            type="button"
            class="px-6 py-3 rounded-lg bg-warning-orange text-black font-semibold hover:bg-warning-orange/90 transition-colors flex items-center gap-2"
            @click="addExercise"
          >
            <UIcon name="i-heroicons-plus" class="w-5 h-5" />
            Add Exercise
          </button>
        </div>
      </div>

      <!-- Notes -->
      <div>
        <label class="block text-sm font-medium text-pure-white/60 mb-2">Notes (optional)</label>
        <textarea
          v-model="templateNotes"
          rows="3"
          placeholder="Any notes about this template..."
          class="w-full px-4 py-3 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors resize-none"
        />
      </div>
    </div>
  </div>
</template>
