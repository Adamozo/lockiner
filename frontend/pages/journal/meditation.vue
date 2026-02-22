<script setup lang="ts">
definePageMeta({
  layout: 'journal',
})

useSeoMeta({
  title: 'Meditation - LockIner',
  description: 'Track your meditation practice',
})

const {
  completedSessions,
  activeSession,
  stats,
  loading,
  fetchSessions,
  fetchActiveSession,
  fetchStats,
  startSession,
  saveSession,
  discardSession,
} = useMeditation()
const toast = useToast()

// --- Timer state ---
const elapsedSeconds = ref(0)
const timerInterval = ref<ReturnType<typeof setInterval> | null>(null)
const notesForActive = ref('')

const startTimer = () => {
  if (timerInterval.value) clearInterval(timerInterval.value)
  timerInterval.value = setInterval(() => {
    if (!activeSession.value) return
    const started = new Date(activeSession.value.started_at).getTime()
    elapsedSeconds.value = Math.floor((Date.now() - started) / 1000)
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

// Format seconds to HH:MM:SS or MM:SS
const formatTimer = (seconds: number): string => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) {
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

// --- Actions ---
const handleStart = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    await startSession({ date: today })
    elapsedSeconds.value = 0
    startTimer()
    toast.add({ title: 'Meditation started', description: 'Timer is running', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to start session', color: 'red' })
  }
}

const handleSave = async () => {
  if (!activeSession.value) return
  try {
    stopTimer()
    const savedDuration = elapsedSeconds.value
    await saveSession(activeSession.value.id, {
      duration_seconds: elapsedSeconds.value,
      notes: notesForActive.value || undefined,
      completed: true,
    })
    await fetchStats()
    await fetchSessions()
    notesForActive.value = ''
    elapsedSeconds.value = 0
    toast.add({ title: 'Session saved!', description: `Great job! ${formatTimer(savedDuration)} of meditation`, color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to save session', color: 'red' })
    startTimer()
  }
}

const handleDiscard = async () => {
  if (!activeSession.value) return
  if (!confirm('Discard this meditation session?')) return
  try {
    stopTimer()
    await discardSession(activeSession.value.id)
    elapsedSeconds.value = 0
    notesForActive.value = ''
    toast.add({ title: 'Session discarded', color: 'yellow' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to discard session', color: 'red' })
  }
}

const handleDeleteCompleted = async (id: number) => {
  if (!confirm('Delete this meditation session?')) return
  try {
    await discardSession(id)
    await fetchStats()
    toast.add({ title: 'Session deleted', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete', color: 'red' })
  }
}

// Init
onMounted(async () => {
  await Promise.all([fetchSessions(), fetchActiveSession(), fetchStats()])
  // Resume timer if there's an active session
  if (activeSession.value) {
    const started = new Date(activeSession.value.started_at).getTime()
    elapsedSeconds.value = Math.floor((Date.now() - started) / 1000)
    startTimer()
  }
})

onUnmounted(() => {
  stopTimer()
})

// Helpers
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
}

const formatMinutes = (minutes: number): string => {
  if (minutes < 1) return `${Math.round(minutes * 60)}s`
  if (minutes < 60) return `${Math.round(minutes)}m`
  return `${Math.floor(minutes / 60)}h ${Math.round(minutes % 60)}m`
}

const formatDuration = (seconds: number | null): string => {
  if (!seconds) return '-'
  return formatMinutes(seconds / 60)
}
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Meditation</h1>
        <p class="mt-1 text-sm sm:text-base text-pure-white/60">Track your mindfulness practice</p>
      </div>
      <BaseButton
        icon="i-heroicons-play"
        variant="primary"
        :disabled="!!activeSession"
        @click="handleStart"
      >
        Start Meditation
      </BaseButton>
    </header>

    <!-- Stats cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-card-black border border-border-gray rounded-lg p-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"></div>
        <p class="text-xs font-medium text-pure-white/60 uppercase tracking-wider">Sessions</p>
        <p class="mt-2 text-3xl font-bold text-cyber-blue">{{ stats?.total_sessions ?? 0 }}</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-electric-green to-cyber-blue"></div>
        <p class="text-xs font-medium text-pure-white/60 uppercase tracking-wider">Total Time</p>
        <p class="mt-2 text-3xl font-bold text-electric-green">{{ formatMinutes(stats?.total_minutes ?? 0) }}</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-warning-orange to-electric-green"></div>
        <p class="text-xs font-medium text-pure-white/60 uppercase tracking-wider">Avg Session</p>
        <p class="mt-2 text-3xl font-bold text-warning-orange">{{ formatMinutes(stats?.avg_duration_minutes ?? 0) }}</p>
      </div>
      <div class="bg-card-black border border-border-gray rounded-lg p-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-warning-orange"></div>
        <p class="text-xs font-medium text-pure-white/60 uppercase tracking-wider">Streak</p>
        <p class="mt-2 text-3xl font-bold text-cyber-blue">{{ stats?.current_streak_days ?? 0 }}
          <span class="text-sm font-normal text-pure-white/40">days</span>
        </p>
      </div>
    </div>

    <!-- Active Session Card -->
    <Transition name="slide-down">
      <div
        v-if="activeSession"
        class="bg-card-black border border-cyber-blue/40 rounded-xl p-8 relative overflow-hidden"
      >
        <!-- Animated cyber background glow -->
        <div class="absolute inset-0 bg-gradient-to-br from-cyber-blue/5 to-electric-green/5 pointer-events-none"></div>
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue via-electric-green to-cyber-blue animate-pulse"></div>

        <div class="relative space-y-6">
          <!-- Session status badge -->
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-2">
              <span class="relative flex h-3 w-3">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-electric-green opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3 w-3 bg-electric-green"></span>
              </span>
              <span class="text-sm font-medium text-electric-green uppercase tracking-widest">Live</span>
            </div>
            <span class="text-pure-white/40 text-sm">Session in progress</span>
          </div>

          <!-- Big Stopwatch Display -->
          <div class="text-center py-4">
            <div
              class="font-mono text-6xl sm:text-8xl font-bold text-pure-white tracking-widest tabular-nums"
              style="text-shadow: 0 0 30px rgba(0, 212, 255, 0.5), 0 0 60px rgba(0, 212, 255, 0.2);"
            >
              {{ formatTimer(elapsedSeconds) }}
            </div>
            <p class="mt-3 text-pure-white/40 text-sm">{{ formatDate(activeSession.date) }}</p>
          </div>

          <!-- Notes input -->
          <div>
            <label class="block text-sm font-medium text-pure-white/60 mb-2">Notes (optional)</label>
            <input
              v-model="notesForActive"
              type="text"
              placeholder="How are you feeling? What's on your mind?"
              class="w-full px-4 py-3 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/30 focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/30 focus:outline-none"
            />
          </div>

          <!-- Action buttons -->
          <div class="flex justify-center">
            <div class="flex gap-3 w-full max-w-sm">
              <BaseButton
                variant="primary"
                icon="i-heroicons-check-circle"
                class="flex-1"
                :loading="loading"
                @click="handleSave"
              >
                Stop &amp; Save
              </BaseButton>
              <BaseButton
                variant="danger"
                icon="i-heroicons-trash"
                @click="handleDiscard"
              >
                Discard
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Sessions History -->
    <div>
      <h2 class="text-xl font-semibold text-pure-white mb-4">History</h2>

      <div v-if="completedSessions.length > 0" class="space-y-3">
        <div
          v-for="session in completedSessions"
          :key="session.id"
          class="bg-card-black border border-border-gray rounded-lg p-4 flex items-center justify-between hover:border-cyber-blue/40 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="p-3 bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 rounded-full border border-cyber-blue/30">
              <UIcon name="i-heroicons-moon" class="w-5 h-5 text-cyber-blue" />
            </div>
            <div>
              <p class="font-semibold text-pure-white">{{ formatDuration(session.duration_seconds) }}</p>
              <p class="text-sm text-pure-white/60">{{ formatDate(session.date) }}</p>
              <p v-if="session.notes" class="text-xs text-pure-white/40 mt-0.5 italic">{{ session.notes }}</p>
            </div>
          </div>
          <BaseButton
            variant="danger"
            size="sm"
            icon="i-heroicons-trash"
            @click="handleDeleteCompleted(session.id)"
          />
        </div>
      </div>

      <div v-else-if="!activeSession" class="bg-card-black border border-border-gray rounded-lg p-12 text-center">
        <div class="w-16 h-16 rounded-full bg-cyber-blue/10 border border-cyber-blue/30 flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-moon" class="w-8 h-8 text-cyber-blue" />
        </div>
        <p class="text-pure-white/60 text-lg">No meditation sessions yet</p>
        <p class="text-pure-white/40 text-sm mt-1">Start your first session to begin tracking</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
