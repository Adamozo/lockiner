<script setup lang="ts">
import type { WorkoutTemplate } from '~/types/fitness'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'select': [template: WorkoutTemplate]
}>()

const { templates, loading, fetchTemplates } = useWorkoutTemplates()

const workoutTypeIcon: Record<string, string> = {
  'Push Day': 'i-heroicons-arrow-up',
  'Pull Day': 'i-heroicons-arrow-down',
  'Leg Day': 'i-heroicons-bolt',
  'Upper Body': 'i-heroicons-user',
  'Full Body': 'i-heroicons-fire',
  'Custom': 'i-heroicons-pencil',
}

onMounted(async () => {
  await fetchTemplates()
})

const handleSelect = (template: WorkoutTemplate) => {
  emit('select', template)
  emit('update:modelValue', false)
}
</script>

<template>
  <BaseModal :model-value="modelValue" title="Use Template" @update:model-value="$emit('update:modelValue', $event)">
    <div class="space-y-4">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-warning-orange animate-spin" />
      </div>

      <!-- Empty state -->
      <div v-else-if="templates.length === 0" class="text-center py-8">
        <UIcon name="i-heroicons-document-duplicate" class="w-12 h-12 mx-auto text-pure-white/30 mb-3" />
        <p class="text-pure-white/60 mb-4">No templates yet</p>
        <BaseButton
          variant="secondary"
          size="sm"
          @click="navigateTo('/fitness/workouts/templates')"
        >
          Create Templates
        </BaseButton>
      </div>

      <!-- Template list -->
      <div v-else class="space-y-2 max-h-96 overflow-y-auto">
        <button
          v-for="template in templates"
          :key="template.id"
          type="button"
          class="w-full text-left p-4 rounded-lg border border-border-gray bg-background-black/50 hover:border-warning-orange/50 hover:bg-warning-orange/5 transition-colors"
          @click="handleSelect(template)"
        >
          <div class="flex items-center gap-3">
            <div class="p-2 bg-warning-orange/10 rounded-lg flex-shrink-0">
              <UIcon :name="workoutTypeIcon[template.workout_type] ?? 'i-heroicons-fire'" class="w-5 h-5 text-warning-orange" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-pure-white truncate">{{ template.name }}</p>
              <p class="text-xs text-pure-white/50">{{ template.workout_type }} &middot; {{ template.exercises.length }} exercises</p>
            </div>
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 text-pure-white/30 flex-shrink-0" />
          </div>
        </button>
      </div>
    </div>
  </BaseModal>
</template>
