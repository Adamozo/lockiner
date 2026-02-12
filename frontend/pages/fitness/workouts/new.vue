<script setup lang="ts">
import type { ExerciseSetCreate, WorkoutCreate, WorkoutUpdate } from '~/types/fitness'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'New Workout - LockIner',
  description: 'Log a new workout session',
})

const router = useRouter()
const toast = useToast()
const { workouts, loading, createWorkout, updateWorkout, fetchWorkouts } = useWorkouts()

interface ExerciseFormData {
  name: string
  sets: number
  reps: number
  weight_kg: number
  rest_seconds?: number
  notes?: string
  sets_detail: ExerciseSetCreate[]
}

// Form state
const workoutName = ref('')
const workoutDate = ref(new Date().toISOString().split('T')[0])
const durationMinutes = ref<number | undefined>(undefined)
const workoutNotes = ref('')
const exercises = ref<ExerciseFormData[]>([])
const draftId = ref<number | null>(null)
const saveStatus = ref<'idle' | 'saving' | 'saved'>('idle')

// Timer
const startTime = ref(Date.now())
const elapsed = ref('00:00')
let timerInterval: ReturnType<typeof setInterval> | undefined

onMounted(async () => {
  await fetchWorkouts()
  timerInterval = setInterval(() => {
    const diff = Math.floor((Date.now() - startTime.value) / 1000)
    const mins = Math.floor(diff / 60).toString().padStart(2, '0')
    const secs = (diff % 60).toString().padStart(2, '0')
    elapsed.value = `${mins}:${secs}`
  }, 1000)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

// Workout templates
const templates = [
  { name: 'Push Day', icon: 'i-heroicons-arrow-up' },
  { name: 'Pull Day', icon: 'i-heroicons-arrow-down' },
  { name: 'Leg Day', icon: 'i-heroicons-bolt' },
  { name: 'Upper Body', icon: 'i-heroicons-user' },
  { name: 'Full Body', icon: 'i-heroicons-fire' },
  { name: 'Custom', icon: 'i-heroicons-pencil' },
]

const selectedTemplate = ref('')
const isCustomName = ref(false)

const selectTemplate = (name: string) => {
  selectedTemplate.value = name
  if (name === 'Custom') {
    isCustomName.value = true
    workoutName.value = ''
  } else {
    isCustomName.value = false
    workoutName.value = name
  }
}

// Exercise management
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
  triggerAutoSave()
}

const updateExercise = (index: number, exercise: ExerciseFormData) => {
  exercises.value[index] = exercise
  triggerAutoSave()
}

const removeExercise = (index: number) => {
  exercises.value.splice(index, 1)
  triggerAutoSave()
}

// Validation
const nameError = ref(false)
const canComplete = computed(() => {
  if (!workoutName.value.trim()) return false
  if (exercises.value.length === 0) return false
  return exercises.value.every(e =>
    e.name.trim() && e.sets_detail.length > 0 && e.sets_detail.every(s => s.reps >= 1)
  )
})

// Auto-save (draft)
let autoSaveTimeout: ReturnType<typeof setTimeout> | undefined

const triggerAutoSave = () => {
  if (autoSaveTimeout) clearTimeout(autoSaveTimeout)
  autoSaveTimeout = setTimeout(() => saveDraft(), 3000)
}

const buildWorkoutPayload = (completed: boolean): WorkoutCreate => ({
  date: workoutDate.value,
  name: workoutName.value || 'Untitled Workout',
  duration_minutes: durationMinutes.value,
  notes: workoutNotes.value || undefined,
  completed,
  exercises: exercises.value.map(e => ({
    name: e.name || 'Unnamed Exercise',
    sets: e.sets_detail.length || e.sets,
    reps: e.sets_detail.length > 0 ? Math.max(...e.sets_detail.map(s => s.reps)) : e.reps,
    weight_kg: e.sets_detail.length > 0 ? Math.max(...e.sets_detail.map(s => s.weight_kg)) : e.weight_kg,
    rest_seconds: e.rest_seconds,
    notes: e.notes,
    sets_detail: e.sets_detail,
  })),
})

const saveDraft = async () => {
  if (exercises.value.length === 0 && !workoutName.value) return
  saveStatus.value = 'saving'
  try {
    if (draftId.value) {
      const payload: WorkoutUpdate = buildWorkoutPayload(false)
      await updateWorkout(draftId.value, payload)
    } else {
      const result = await createWorkout(buildWorkoutPayload(false))
      draftId.value = result.id
    }
    saveStatus.value = 'saved'
  } catch {
    saveStatus.value = 'idle'
  }
}

const handleSaveDraft = async () => {
  await saveDraft()
  toast.add({ title: 'Draft saved', description: 'You can resume this workout later', color: 'green' })
}

const handleComplete = async () => {
  nameError.value = !workoutName.value.trim()
  if (!canComplete.value) {
    toast.add({ title: 'Incomplete', description: 'Please fill in all required fields', color: 'red' })
    return
  }

  loading.value = true
  try {
    if (draftId.value) {
      await updateWorkout(draftId.value, { ...buildWorkoutPayload(true) })
    } else {
      await createWorkout(buildWorkoutPayload(true))
    }
    toast.add({ title: 'Workout complete!', description: 'Great job!', color: 'green' })
    router.push('/fitness/workouts')
  } catch {
    toast.add({ title: 'Error', description: 'Failed to save workout', color: 'red' })
  } finally {
    loading.value = false
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
        @click="router.push('/fitness/workouts')"
      >
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
      </button>
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-pure-white">New Workout</h1>
        <div class="flex items-center gap-3 mt-1">
          <span class="text-sm text-pure-white/40 flex items-center gap-1">
            <UIcon name="i-heroicons-clock" class="w-4 h-4" />
            {{ elapsed }}
          </span>
          <span
            v-if="saveStatus !== 'idle'"
            class="text-xs px-2 py-0.5 rounded-full"
            :class="saveStatus === 'saving' ? 'bg-warning-orange/20 text-warning-orange' : 'bg-electric-green/20 text-electric-green'"
          >
            {{ saveStatus === 'saving' ? 'Saving...' : 'Saved' }}
          </span>
        </div>
      </div>
    </header>

    <!-- Action buttons -->
    <div class="flex gap-3 mb-6">
      <BaseButton
        variant="secondary"
        class="flex-1 min-w-0"
        @click="handleSaveDraft"
      >
        Save Draft
      </BaseButton>
      <BaseButton
        variant="primary"
        class="flex-1 min-w-0"
        :disabled="!canComplete"
        :loading="loading"
        @click="handleComplete"
      >
        Complete Workout
      </BaseButton>
    </div>

    <div class="space-y-6">
      <!-- Workout Template chips -->
      <div>
        <label class="block text-sm font-medium text-pure-white/60 mb-3">Workout Type</label>
        <div class="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-hide">
          <button
            v-for="t in templates"
            :key="t.name"
            type="button"
            class="flex-shrink-0 px-4 py-2.5 rounded-lg border text-sm font-medium transition-all flex items-center gap-2"
            :class="selectedTemplate === t.name
              ? 'bg-warning-orange/20 border-warning-orange text-warning-orange'
              : 'border-border-gray text-pure-white/60 hover:border-pure-white/40 hover:text-pure-white'"
            @click="selectTemplate(t.name)"
          >
            <UIcon :name="t.icon" class="w-4 h-4" />
            {{ t.name }}
          </button>
        </div>
      </div>

      <!-- Custom name input (shown when Custom selected) -->
      <div v-if="isCustomName">
        <label class="block text-sm font-medium text-pure-white/60 mb-2">Workout Name</label>
        <input
          v-model="workoutName"
          type="text"
          placeholder="e.g., Morning HIIT, Chest & Triceps..."
          class="w-full min-h-12 px-4 py-3 rounded-lg border bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors"
          :class="nameError && !workoutName.trim() ? 'border-danger-red' : 'border-border-gray'"
        />
      </div>

      <!-- Date & Duration -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-pure-white/60 mb-2">Date</label>
          <input
            v-model="workoutDate"
            type="date"
            class="w-full min-h-12 px-4 py-3 rounded-lg border border-border-gray bg-card-black text-pure-white focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-pure-white/60 mb-2">Duration (min)</label>
          <input
            v-model.number="durationMinutes"
            type="number"
            inputmode="numeric"
            min="1"
            placeholder="Optional"
            class="w-full min-h-12 px-4 py-3 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors"
          />
        </div>
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
            :workouts="workouts"
            @update:model-value="updateExercise(index, $event)"
            @delete="removeExercise(index)"
          />
        </div>

        <!-- Empty state -->
        <div v-else class="p-8 border-2 border-dashed border-border-gray rounded-lg text-center">
          <UIcon name="i-heroicons-plus-circle" class="w-10 h-10 mx-auto text-pure-white/20 mb-3" />
          <p class="text-pure-white/40 text-sm">Add your first exercise to get started</p>
        </div>

        <!-- Add Exercise button -->
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
          v-model="workoutNotes"
          rows="3"
          placeholder="How did it feel? Any PRs?"
          class="w-full px-4 py-3 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors resize-none"
        />
      </div>
    </div>

  </div>
</template>
