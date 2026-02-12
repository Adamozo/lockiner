<script setup lang="ts">
import type { ExerciseSetCreate, Workout } from '~/types/fitness'

interface ExerciseFormData {
  name: string
  sets: number
  reps: number
  weight_kg: number
  rest_seconds?: number
  notes?: string
  sets_detail: ExerciseSetCreate[]
}

const props = defineProps<{
  modelValue: ExerciseFormData
  exerciseIndex: number
  workouts?: Workout[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ExerciseFormData]
  'delete': []
}>()

const collapsed = ref(false)

const updateName = (name: string) => {
  emit('update:modelValue', { ...props.modelValue, name })
}

const updateSet = (index: number, set: ExerciseSetCreate) => {
  const newSets = [...props.modelValue.sets_detail]
  newSets[index] = set
  emit('update:modelValue', { ...props.modelValue, sets_detail: newSets })
}

const addSet = () => {
  const lastSet = props.modelValue.sets_detail[props.modelValue.sets_detail.length - 1]
  const newSet: ExerciseSetCreate = {
    set_number: props.modelValue.sets_detail.length + 1,
    reps: lastSet?.reps || 10,
    weight_kg: lastSet?.weight_kg || 0,
    completed: false,
  }
  emit('update:modelValue', {
    ...props.modelValue,
    sets_detail: [...props.modelValue.sets_detail, newSet],
  })
}

const deleteSet = (index: number) => {
  const newSets = props.modelValue.sets_detail
    .filter((_, i) => i !== index)
    .map((s, i) => ({ ...s, set_number: i + 1 }))
  emit('update:modelValue', { ...props.modelValue, sets_detail: newSets })
}

const completedCount = computed(() =>
  props.modelValue.sets_detail.filter(s => s.completed).length
)

const setsSummary = computed(() => {
  const total = props.modelValue.sets_detail.length
  if (total === 0) return 'No sets'
  return `${completedCount.value}/${total} sets`
})
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg overflow-hidden">
    <!-- Header -->
    <div class="flex items-center gap-3 p-4 border-b border-border-gray">
      <button
        type="button"
        class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-pure-white/40 hover:text-pure-white hover:bg-border-gray/50 transition-colors"
        @click="collapsed = !collapsed"
      >
        <UIcon
          :name="collapsed ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-down'"
          class="w-5 h-5"
        />
      </button>

      <div class="flex-1 min-w-0">
        <template v-if="collapsed">
          <p class="text-sm font-semibold text-pure-white truncate">
            {{ modelValue.name || `Exercise ${exerciseIndex + 1}` }}
          </p>
          <p class="text-xs text-pure-white/40">{{ setsSummary }}</p>
        </template>
        <template v-else>
          <WorkoutExerciseSearchInput
            :model-value="modelValue.name"
            :workouts="workouts"
            @update:model-value="updateName"
          />
        </template>
      </div>

      <button
        type="button"
        class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-pure-white/30 hover:text-danger-red hover:bg-danger-red/10 transition-colors"
        @click="$emit('delete')"
      >
        <UIcon name="i-heroicons-trash" class="w-4 h-4" />
      </button>
    </div>

    <!-- Sets list -->
    <div v-if="!collapsed" class="p-4 space-y-3">
      <!-- Column headers -->
      <div v-if="modelValue.sets_detail.length > 0" class="flex items-center gap-2 sm:gap-3 px-1">
        <div class="w-8 sm:w-10" />
        <div class="flex-1 text-[10px] uppercase tracking-wider text-pure-white/30 text-center">Weight</div>
        <div class="flex-1 text-[10px] uppercase tracking-wider text-pure-white/30 text-center">Reps</div>
        <div class="w-10 sm:w-12" />
        <div class="w-8" />
      </div>

      <WorkoutSetRow
        v-for="(set, index) in modelValue.sets_detail"
        :key="index"
        :model-value="set"
        :set-index="index"
        @update:model-value="updateSet(index, $event)"
        @delete="deleteSet(index)"
      />

      <!-- Add Set button -->
      <div class="flex justify-center">
        <button
          type="button"
          class="px-5 py-2 rounded-lg border border-dashed border-border-gray text-sm text-pure-white/50 hover:text-warning-orange hover:border-warning-orange/50 transition-colors flex items-center gap-2"
          @click="addSet"
        >
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Add Set
        </button>
      </div>
    </div>
  </div>
</template>
