<script setup lang="ts">
definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Workouts - LockIner',
  description: 'Log and manage your gym workouts',
})

const { workouts, loading, draftWorkouts, completedWorkouts, fetchWorkouts, deleteWorkout } = useWorkouts()
const toast = useToast()

onMounted(async () => {
  await fetchWorkouts()
})

const { confirm } = useConfirm()

const handleDelete = async (id: number) => {
  if (!await confirm({ message: 'Are you sure you want to delete this workout?', confirmText: 'Delete' })) return

  try {
    await deleteWorkout(id)
    toast.add({ title: 'Success', description: 'Workout deleted', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete workout', color: 'red' })
  }
}

const handleDiscardDraft = async (id: number) => {
  if (!await confirm({ message: 'Discard this workout draft?', confirmText: 'Discard', variant: 'warning' })) return

  try {
    await deleteWorkout(id)
    toast.add({ title: 'Draft discarded', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to discard draft', color: 'red' })
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
        @click="navigateTo('/fitness/workouts/new')"
      >
        Log Workout
      </BaseButton>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-warning-orange animate-spin" />
    </div>

    <template v-else>
      <!-- Draft workout banners -->
      <div v-if="draftWorkouts.length > 0" class="space-y-3">
        <div
          v-for="draft in draftWorkouts"
          :key="draft.id"
          class="bg-card-black border border-warning-orange/50 rounded-lg p-4 flex items-center gap-4"
        >
          <div class="p-3 bg-warning-orange/10 rounded-lg flex-shrink-0">
            <UIcon name="i-heroicons-clock" class="w-6 h-6 text-warning-orange" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-warning-orange">Workout in progress</p>
            <p class="text-pure-white font-medium truncate">{{ draft.name }}</p>
            <p class="text-xs text-pure-white/40">{{ formatDate(draft.date) }} &middot; {{ draft.exercises.length }} exercises</p>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <BaseButton
              variant="primary"
              size="sm"
              @click="navigateTo(`/fitness/workouts/${draft.id}`)"
            >
              Resume
            </BaseButton>
            <BaseButton
              variant="danger"
              size="sm"
              icon="i-heroicons-trash"
              @click="handleDiscardDraft(draft.id)"
            />
          </div>
        </div>
      </div>

      <!-- Completed workouts list -->
      <div v-if="completedWorkouts.length > 0" class="space-y-4">
        <div
          v-for="workout in completedWorkouts"
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
                <div class="flex items-center gap-1">
                  <BaseButton
                    variant="secondary"
                    size="sm"
                    icon="i-heroicons-pencil"
                    @click="navigateTo(`/fitness/workouts/${workout.id}`)"
                  />
                  <BaseButton
                    variant="danger"
                    size="sm"
                    icon="i-heroicons-trash"
                    @click="handleDelete(workout.id)"
                  />
                </div>
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
                <UIcon name="i-heroicons-bolt" class="w-4 h-4 text-warning-orange flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-pure-white">{{ exercise.name }}</p>
                  <p v-if="exercise.sets_detail && exercise.sets_detail.length > 0" class="text-xs text-pure-white/60">
                    {{ exercise.sets_detail.length }} sets &middot;
                    {{ exercise.sets_detail.map(s => `${s.weight_kg}kg x${s.reps}`).join(', ') }}
                  </p>
                  <p v-else class="text-xs text-pure-white/60">
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

      <!-- Empty state (no workouts at all) -->
      <div
        v-else-if="draftWorkouts.length === 0"
        class="bg-card-black border border-border-gray rounded-lg p-12 text-center"
      >
        <UIcon name="i-heroicons-fire" class="w-16 h-16 mx-auto text-pure-white/40 mb-4" />
        <h3 class="text-lg font-semibold text-pure-white mb-2">No workouts yet</h3>
        <p class="text-pure-white/60 mb-6">Start logging your gym sessions to track progress</p>
        <BaseButton variant="primary" icon="i-heroicons-plus" @click="navigateTo('/fitness/workouts/new')">
          Log Your First Workout
        </BaseButton>
      </div>
    </template>
  </div>
</template>
