<script setup lang="ts">
import type { ExerciseSetCreate, WorkoutUpdate, Workout } from '~/types/fitness'

definePageMeta({
  layout: 'fitness',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { workouts, loading, fetchWorkout, updateWorkout, fetchWorkouts, timerStart, timerPause, timerResume, timerStop } = useWorkouts()

const workoutId = computed(() => Number(route.params.id))

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
const workoutDate = ref('')
const durationMinutes = ref<number | undefined>(undefined)
const workoutNotes = ref('')
const exercises = ref<ExerciseFormData[]>([])
const isCompleted = ref(false)
const saveStatus = ref<'idle' | 'saving' | 'saved'>('idle')
const loadError = ref(false)

// Workout data with timer fields
const currentWorkout = ref<Workout | null>(null)

useSeoMeta({
  title: 'Edit Workout - LockIner',
  description: 'Edit or resume your workout',
})

// ─── Timer state (derived from server data) ─────────────────────────────────

const timerState = computed((): 'idle' | 'running' | 'paused' | 'done' => {
  const w = currentWorkout.value
  if (!w || !w.timer_started_at) return 'idle'
  if (w.timer_ended_at) return 'done'
  if (w.timer_paused_at) return 'paused'
  return 'running'
})

const elapsedSeconds = ref(0)
let tickerInterval: ReturnType<typeof setInterval> | undefined

const computeElapsed = () => {
  const w = currentWorkout.value
  if (!w || !w.timer_started_at) { elapsedSeconds.value = 0; return }
  const started = new Date(w.timer_started_at).getTime()
  const paused = (w.total_paused_seconds || 0) * 1000
  if (w.timer_ended_at) {
    elapsedSeconds.value = Math.max(0, Math.floor((new Date(w.timer_ended_at).getTime() - started - paused) / 1000))
  } else if (w.timer_paused_at) {
    elapsedSeconds.value = Math.max(0, Math.floor((new Date(w.timer_paused_at).getTime() - started - paused) / 1000))
  } else {
    elapsedSeconds.value = Math.max(0, Math.floor((Date.now() - started - paused) / 1000))
  }
}

const syncTicker = () => {
  if (tickerInterval) clearInterval(tickerInterval)
  computeElapsed()
  if (timerState.value === 'running') {
    tickerInterval = setInterval(computeElapsed, 1000)
  }
}

watch(timerState, syncTicker)

const formatTimer = (seconds: number): string => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const formatTime = (iso: string) => {
  return new Date(iso).toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })
}

// Timer controls
const timerLoading = ref(false)

const handleTimerStart = async () => {
  timerLoading.value = true
  try {
    currentWorkout.value = await timerStart(workoutId.value)
    syncTicker()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to start timer', color: 'red' })
  } finally {
    timerLoading.value = false
  }
}

const handleTimerPause = async () => {
  timerLoading.value = true
  try {
    currentWorkout.value = await timerPause(workoutId.value)
    syncTicker()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to pause timer', color: 'red' })
  } finally {
    timerLoading.value = false
  }
}

const handleTimerResume = async () => {
  timerLoading.value = true
  try {
    currentWorkout.value = await timerResume(workoutId.value)
    syncTicker()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to resume timer', color: 'red' })
  } finally {
    timerLoading.value = false
  }
}

const handleTimerStop = async () => {
  timerLoading.value = true
  try {
    currentWorkout.value = await timerStop(workoutId.value)
    durationMinutes.value = currentWorkout.value.duration_minutes ?? undefined
    syncTicker()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to stop timer', color: 'red' })
  } finally {
    timerLoading.value = false
  }
}

// ─── Rest Timer ─────────────────────────────────────────────────────────────

const defaultRestSeconds = ref(90)
const restSecondsLeft = ref(0)
let restInterval: ReturnType<typeof setInterval> | undefined
const restActive = computed(() => restSecondsLeft.value > 0)

const playBeep = () => {
  try {
    const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
    const ctx = new AudioCtx()
    for (let i = 0; i < 3; i++) {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.frequency.value = 880
      osc.type = 'sine'
      const t = ctx.currentTime + i * 0.35
      gain.gain.setValueAtTime(0.4, t)
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.28)
      osc.start(t)
      osc.stop(t + 0.28)
    }
  } catch { /* audio not supported */ }
}

const startRest = () => {
  restSecondsLeft.value = defaultRestSeconds.value
  if (restInterval) clearInterval(restInterval)
  restInterval = setInterval(() => {
    restSecondsLeft.value = Math.max(0, restSecondsLeft.value - 1)
    if (restSecondsLeft.value === 0) {
      clearInterval(restInterval)
      playBeep()
    }
  }, 1000)
}

const cancelRest = () => {
  if (restInterval) clearInterval(restInterval)
  restSecondsLeft.value = 0
}

const saveDefaultRest = async () => {
  try {
    await updateWorkout(workoutId.value, { default_rest_seconds: defaultRestSeconds.value } as WorkoutUpdate)
  } catch { /* silent */ }
}

// ─── Load workout ────────────────────────────────────────────────────────────

onMounted(async () => {
  await fetchWorkouts()
  try {
    const workout = await fetchWorkout(workoutId.value)
    currentWorkout.value = workout
    workoutName.value = workout.name
    workoutDate.value = workout.date
    durationMinutes.value = workout.duration_minutes
    workoutNotes.value = workout.notes || ''
    isCompleted.value = workout.completed
    defaultRestSeconds.value = workout.default_rest_seconds || 90
    exercises.value = workout.exercises.map(e => ({
      name: e.name,
      sets: e.sets,
      reps: e.reps,
      weight_kg: e.weight_kg,
      rest_seconds: e.rest_seconds,
      notes: e.notes,
      sets_detail: e.sets_detail?.length
        ? e.sets_detail.map(s => ({
            set_number: s.set_number,
            reps: s.reps,
            weight_kg: s.weight_kg,
            completed: s.completed,
          }))
        : [{ set_number: 1, reps: e.reps, weight_kg: e.weight_kg, completed: false }],
    }))
    syncTicker()
  } catch {
    loadError.value = true
    toast.add({ title: 'Error', description: 'Workout not found', color: 'red' })
  }
})

onUnmounted(() => {
  if (tickerInterval) clearInterval(tickerInterval)
  if (restInterval) clearInterval(restInterval)
})

// ─── Form & save ────────────────────────────────────────────────────────────

const addExercise = () => {
  exercises.value.push({
    name: '',
    sets: 3,
    reps: 10,
    weight_kg: 0,
    sets_detail: [{ set_number: 1, reps: 10, weight_kg: 0, completed: false }],
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

const canComplete = computed(() => {
  if (!workoutName.value.trim()) return false
  if (exercises.value.length === 0) return false
  return exercises.value.every(e =>
    e.name.trim() && e.sets_detail.length > 0 && e.sets_detail.every(s => s.reps >= 1)
  )
})

let autoSaveTimeout: ReturnType<typeof setTimeout> | undefined

const triggerAutoSave = () => {
  if (isCompleted.value) return
  if (autoSaveTimeout) clearTimeout(autoSaveTimeout)
  autoSaveTimeout = setTimeout(() => saveDraft(), 3000)
}

const buildPayload = (completed: boolean): WorkoutUpdate => ({
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
  saveStatus.value = 'saving'
  try {
    await updateWorkout(workoutId.value, buildPayload(false))
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
  if (!canComplete.value) {
    toast.add({ title: 'Incomplete', description: 'Please fill in all required fields', color: 'red' })
    return
  }
  loading.value = true
  try {
    // Auto-stop running timer before completing
    if (timerState.value === 'running' || timerState.value === 'paused') {
      currentWorkout.value = await timerStop(workoutId.value)
      durationMinutes.value = currentWorkout.value.duration_minutes ?? undefined
      syncTicker()
    }
    await updateWorkout(workoutId.value, buildPayload(true))
    toast.add({ title: 'Workout complete!', description: 'Great job!', color: 'green' })
    router.push('/fitness/workouts')
  } catch {
    toast.add({ title: 'Error', description: 'Failed to save workout', color: 'red' })
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  loading.value = true
  try {
    await updateWorkout(workoutId.value, buildPayload(isCompleted.value))
    toast.add({ title: 'Saved', description: 'Workout updated', color: 'green' })
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
    <!-- Loading / Error -->
    <div v-if="loadError" class="text-center py-12">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 mx-auto text-danger-red mb-3" />
      <p class="text-pure-white/60">Workout not found</p>
      <BaseButton variant="secondary" class="mt-4" @click="router.push('/fitness/workouts')">
        Back to Workouts
      </BaseButton>
    </div>

    <template v-else>
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
          <h1 class="text-2xl font-bold text-pure-white">
            {{ isCompleted ? 'Edit Workout' : 'Resume Workout' }}
          </h1>
          <span
            v-if="saveStatus !== 'idle'"
            class="text-xs px-2 py-0.5 rounded-full"
            :class="saveStatus === 'saving' ? 'bg-warning-orange/20 text-warning-orange' : 'bg-electric-green/20 text-electric-green'"
          >
            {{ saveStatus === 'saving' ? 'Saving...' : 'Saved' }}
          </span>
        </div>
      </header>

      <!-- Action buttons -->
      <div class="flex gap-3 mb-6">
        <template v-if="isCompleted">
          <BaseButton variant="secondary" class="flex-1 min-w-0" @click="router.push('/fitness/workouts')">
            Cancel
          </BaseButton>
          <BaseButton variant="primary" class="flex-1 min-w-0" :loading="loading" @click="handleSave">
            Save Changes
          </BaseButton>
        </template>
        <template v-else>
          <BaseButton variant="secondary" class="flex-1 min-w-0" @click="handleSaveDraft">
            Save Draft
          </BaseButton>
          <BaseButton variant="primary" class="flex-1 min-w-0" :disabled="!canComplete" :loading="loading" @click="handleComplete">
            Complete Workout
          </BaseButton>
        </template>
      </div>

      <div class="space-y-6">

        <!-- ─── WORKOUT TIMER (draft only) ─────────────────────────── -->
        <div
          v-if="!isCompleted"
          class="bg-card-black border rounded-xl p-5 relative overflow-hidden transition-colors"
          :class="timerState === 'running' ? 'border-warning-orange/50' : timerState === 'paused' ? 'border-cyber-blue/50' : 'border-border-gray'"
        >
          <div
            class="absolute top-0 left-0 w-full h-0.5"
            :class="timerState === 'running'
              ? 'bg-gradient-to-r from-warning-orange to-electric-green animate-pulse'
              : timerState === 'paused'
              ? 'bg-gradient-to-r from-cyber-blue to-electric-green'
              : 'bg-gradient-to-r from-border-gray to-border-gray'"
          ></div>

          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xs font-semibold text-pure-white/50 uppercase tracking-widest">Workout Timer</h3>
            <div class="flex items-center gap-3 text-xs text-pure-white/40">
              <span v-if="currentWorkout?.timer_started_at">
                Start: {{ formatTime(currentWorkout.timer_started_at) }}
              </span>
              <span v-if="currentWorkout?.total_paused_seconds">
                Pauses: {{ formatTimer(currentWorkout.total_paused_seconds) }}
              </span>
            </div>
          </div>

          <!-- Timer display -->
          <div class="text-center py-3 mb-4">
            <div
              class="font-mono font-bold tabular-nums transition-all"
              :class="[
                timerState === 'running' ? 'text-warning-orange text-6xl' :
                timerState === 'paused' ? 'text-cyber-blue text-6xl' :
                timerState === 'done' ? 'text-electric-green text-5xl' :
                'text-pure-white/30 text-5xl'
              ]"
              :style="timerState === 'running' ? 'text-shadow: 0 0 25px rgba(255,140,0,0.5)' : timerState === 'paused' ? 'text-shadow: 0 0 25px rgba(0,212,255,0.4)' : ''"
            >
              {{ formatTimer(elapsedSeconds) }}
            </div>
            <p v-if="timerState === 'paused'" class="mt-1 text-xs text-cyber-blue/60 uppercase tracking-widest">Paused</p>
            <p v-else-if="timerState === 'done'" class="mt-1 text-xs text-electric-green/60 uppercase tracking-widest">Timer stopped</p>
            <p v-else-if="timerState === 'idle'" class="mt-1 text-xs text-pure-white/30">Press Start to begin tracking</p>
          </div>

          <!-- Controls -->
          <div class="flex justify-center gap-3">
            <template v-if="timerState === 'idle'">
              <BaseButton variant="primary" icon="i-heroicons-play" :loading="timerLoading" @click="handleTimerStart">
                Start Timer
              </BaseButton>
            </template>
            <template v-else-if="timerState === 'running'">
              <BaseButton variant="secondary" icon="i-heroicons-pause" :loading="timerLoading" @click="handleTimerPause">
                Pause
              </BaseButton>
              <BaseButton variant="danger" icon="i-heroicons-stop" :loading="timerLoading" @click="handleTimerStop">
                Stop
              </BaseButton>
            </template>
            <template v-else-if="timerState === 'paused'">
              <BaseButton variant="primary" icon="i-heroicons-play" :loading="timerLoading" @click="handleTimerResume">
                Resume
              </BaseButton>
              <BaseButton variant="danger" icon="i-heroicons-stop" :loading="timerLoading" @click="handleTimerStop">
                Stop
              </BaseButton>
            </template>
            <template v-else>
              <BaseButton variant="secondary" icon="i-heroicons-arrow-path" :loading="timerLoading" @click="handleTimerStart">
                Restart Timer
              </BaseButton>
            </template>
          </div>
        </div>

        <!-- ─── COMPLETED TIMER STATS ──────────────────────────────── -->
        <div
          v-else-if="currentWorkout?.timer_started_at"
          class="bg-card-black border border-border-gray rounded-xl p-5 relative overflow-hidden"
        >
          <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-electric-green to-cyber-blue"></div>
          <h3 class="text-xs font-semibold text-pure-white/50 uppercase tracking-widest mb-4">Workout Time</h3>
          <div class="grid grid-cols-3 gap-4 text-center">
            <div>
              <p class="text-xs text-pure-white/40 mb-1">Active</p>
              <p class="text-xl font-bold font-mono text-warning-orange">{{ formatTimer(elapsedSeconds) }}</p>
            </div>
            <div>
              <p class="text-xs text-pure-white/40 mb-1">Breaks</p>
              <p class="text-xl font-bold font-mono text-cyber-blue">{{ formatTimer(currentWorkout.total_paused_seconds || 0) }}</p>
            </div>
            <div>
              <p class="text-xs text-pure-white/40 mb-1">Total</p>
              <p class="text-xl font-bold font-mono text-pure-white">{{ formatTimer(elapsedSeconds + (currentWorkout.total_paused_seconds || 0)) }}</p>
            </div>
          </div>
          <div v-if="currentWorkout.timer_started_at && currentWorkout.timer_ended_at" class="flex justify-center gap-6 mt-3 text-xs text-pure-white/30">
            <span>{{ formatTime(currentWorkout.timer_started_at) }} → {{ formatTime(currentWorkout.timer_ended_at) }}</span>
          </div>
        </div>

        <!-- ─── REST TIMER (draft only) ────────────────────────────── -->
        <div v-if="!isCompleted" class="bg-card-black border border-border-gray rounded-xl p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xs font-semibold text-pure-white/50 uppercase tracking-widest">Rest Timer</h3>
            <div class="flex items-center gap-2">
              <input
                v-model.number="defaultRestSeconds"
                type="number"
                min="5"
                max="600"
                class="w-16 text-center px-2 py-1 text-sm border border-border-gray rounded-lg bg-background-black text-pure-white focus:border-cyber-blue focus:outline-none"
                @change="saveDefaultRest"
              />
              <span class="text-xs text-pure-white/40">sec</span>
            </div>
          </div>

          <!-- Active rest countdown -->
          <div v-if="restActive" class="text-center">
            <div
              class="font-mono text-5xl font-bold text-cyber-blue tabular-nums mb-3"
              style="text-shadow: 0 0 25px rgba(0,212,255,0.4)"
            >
              {{ formatTimer(restSecondsLeft) }}
            </div>
            <!-- Progress bar -->
            <div class="w-full h-2 bg-border-gray rounded-full mb-4 overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-cyber-blue to-electric-green rounded-full transition-all duration-1000"
                :style="{ width: `${(restSecondsLeft / defaultRestSeconds) * 100}%` }"
              />
            </div>
            <BaseButton variant="secondary" size="sm" icon="i-heroicons-x-mark" @click="cancelRest">
              Cancel Rest
            </BaseButton>
          </div>

          <!-- Start rest button -->
          <div v-else class="flex justify-center">
            <BaseButton variant="secondary" icon="i-heroicons-clock" @click="startRest">
              Start Rest ({{ defaultRestSeconds }}s)
            </BaseButton>
          </div>
        </div>

        <!-- Workout Name -->
        <div>
          <label class="block text-sm font-medium text-pure-white/60 mb-2">Workout Name</label>
          <input
            v-model="workoutName"
            type="text"
            placeholder="e.g., Push Day"
            class="w-full min-h-12 px-4 py-3 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors"
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
              placeholder="Auto from timer"
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

          <div v-else class="p-8 border-2 border-dashed border-border-gray rounded-lg text-center">
            <UIcon name="i-heroicons-plus-circle" class="w-10 h-10 mx-auto text-pure-white/20 mb-3" />
            <p class="text-pure-white/40 text-sm">Add your first exercise</p>
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
            v-model="workoutNotes"
            rows="3"
            placeholder="How did it feel? Any PRs?"
            class="w-full px-4 py-3 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors resize-none"
          />
        </div>

      </div>
    </template>
  </div>
</template>
