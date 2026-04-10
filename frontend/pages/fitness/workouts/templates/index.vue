<script setup lang="ts">
definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Workout Templates - LockIner',
  description: 'Manage your reusable workout templates',
})

const { templates, loading, fetchTemplates, deleteTemplate } = useWorkoutTemplates()
const toast = useToast()
const { confirm } = useConfirm()

onMounted(async () => {
  await fetchTemplates()
})

const handleDelete = async (id: number) => {
  if (!await confirm({ message: 'Delete this template?', confirmText: 'Delete' })) return
  try {
    await deleteTemplate(id)
    toast.add({ title: 'Template deleted', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete template', color: 'red' })
  }
}

const workoutTypeIcon: Record<string, string> = {
  'Push Day': 'i-heroicons-arrow-up',
  'Pull Day': 'i-heroicons-arrow-down',
  'Leg Day': 'i-heroicons-bolt',
  'Upper Body': 'i-heroicons-user',
  'Full Body': 'i-heroicons-fire',
  'Custom': 'i-heroicons-pencil',
}
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div class="flex items-center gap-3">
        <button
          type="button"
          class="w-10 h-10 rounded-lg border border-border-gray flex items-center justify-center text-pure-white/60 hover:text-pure-white hover:border-pure-white/40 transition-colors"
          @click="navigateTo('/fitness/workouts')"
        >
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Workout Templates</h1>
          <p class="mt-1 text-sm text-pure-white/60">Reusable workout structures for quick logging</p>
        </div>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        size="sm"
        variant="primary"
        @click="navigateTo('/fitness/workouts/templates/new')"
      >
        New Template
      </BaseButton>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-warning-orange animate-spin" />
    </div>

    <template v-else>
      <!-- Templates list -->
      <div v-if="templates.length > 0" class="space-y-4">
        <div
          v-for="template in templates"
          :key="template.id"
          class="bg-card-black border border-border-gray rounded-lg overflow-hidden hover:border-warning-orange/50 transition-colors"
        >
          <div class="p-4">
            <div class="flex items-center justify-between gap-4">
              <div class="flex items-center gap-4 flex-1 min-w-0">
                <div class="p-3 bg-warning-orange/10 rounded-lg flex-shrink-0">
                  <UIcon :name="workoutTypeIcon[template.workout_type] ?? 'i-heroicons-fire'" class="w-6 h-6 text-warning-orange" />
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-pure-white truncate">{{ template.name }}</h3>
                  <p class="text-sm text-pure-white/60">{{ template.workout_type }} &middot; {{ template.exercises.length }} exercises</p>
                </div>
              </div>
              <div class="flex items-center gap-1 flex-shrink-0">
                <BaseButton
                  variant="secondary"
                  size="sm"
                  icon="i-heroicons-pencil"
                  @click="navigateTo(`/fitness/workouts/templates/${template.id}`)"
                />
                <BaseButton
                  variant="danger"
                  size="sm"
                  icon="i-heroicons-trash"
                  @click="handleDelete(template.id)"
                />
              </div>
            </div>

            <!-- Exercises preview -->
            <div v-if="template.exercises.length > 0" class="mt-3 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              <div
                v-for="exercise in template.exercises"
                :key="exercise.id"
                class="flex items-center gap-2 px-3 py-2 bg-background-black/50 rounded-lg"
              >
                <UIcon name="i-heroicons-bolt" class="w-3.5 h-3.5 text-warning-orange flex-shrink-0" />
                <span class="text-sm text-pure-white truncate">{{ exercise.name }}</span>
                <span class="text-xs text-pure-white/40 ml-auto flex-shrink-0">{{ exercise.sets }}×{{ exercise.reps }}</span>
              </div>
            </div>

            <p v-if="template.notes" class="mt-3 text-sm text-pure-white/50 italic">"{{ template.notes }}"</p>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-else
        class="bg-card-black border border-border-gray rounded-lg p-12 text-center"
      >
        <UIcon name="i-heroicons-document-duplicate" class="w-16 h-16 mx-auto text-pure-white/40 mb-4" />
        <h3 class="text-lg font-semibold text-pure-white mb-2">No templates yet</h3>
        <p class="text-pure-white/60 mb-6">Create templates to quickly fill in your workouts</p>
        <BaseButton variant="primary" icon="i-heroicons-plus" @click="navigateTo('/fitness/workouts/templates/new')">
          Create First Template
        </BaseButton>
      </div>
    </template>
  </div>
</template>
