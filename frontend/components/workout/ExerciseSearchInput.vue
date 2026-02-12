<script setup lang="ts">
import type { Workout } from '~/types/fitness'

const props = defineProps<{
  modelValue: string
  workouts?: Workout[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const { search } = useExerciseLibrary(toRef(() => props.workouts || []) as Ref<Workout[]>)

const query = ref(props.modelValue)
const isOpen = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

watch(() => props.modelValue, (val) => {
  query.value = val
})

const results = computed(() => search(query.value))

const handleInput = (e: Event) => {
  const val = (e.target as HTMLInputElement).value
  query.value = val
  emit('update:modelValue', val)
  isOpen.value = true
}

const selectExercise = (name: string) => {
  query.value = name
  emit('update:modelValue', name)
  isOpen.value = false
}

const handleFocus = () => {
  isOpen.value = true
}

const handleBlur = () => {
  // Delay to allow click on dropdown items
  setTimeout(() => {
    isOpen.value = false
  }, 200)
}

const categoryColors: Record<string, string> = {
  push: 'text-warning-orange',
  pull: 'text-cyber-blue',
  legs: 'text-electric-green',
  core: 'text-purple-400',
  other: 'text-pure-white/60',
}
</script>

<template>
  <div class="relative">
    <input
      ref="inputRef"
      :value="query"
      type="text"
      placeholder="Search exercises..."
      class="w-full min-h-12 px-4 py-3 rounded-lg border border-border-gray bg-card-black text-pure-white placeholder-pure-white/40 focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
    />
    <UIcon
      name="i-heroicons-magnifying-glass"
      class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-pure-white/30 pointer-events-none"
    />

    <!-- Dropdown -->
    <div
      v-if="isOpen && (results.recent.length > 0 || results.grouped.length > 0)"
      class="absolute z-50 mt-1 w-full max-h-64 overflow-y-auto rounded-lg border border-border-gray bg-card-black shadow-xl"
    >
      <!-- Recent exercises -->
      <div v-if="results.recent.length > 0 && !query">
        <div class="px-3 py-2 text-[10px] uppercase tracking-wider text-pure-white/40 font-semibold">
          Recent
        </div>
        <button
          v-for="name in results.recent"
          :key="'recent-' + name"
          type="button"
          class="w-full px-3 py-2.5 text-left text-sm text-pure-white hover:bg-warning-orange/10 transition-colors flex items-center gap-2"
          @mousedown.prevent="selectExercise(name)"
        >
          <UIcon name="i-heroicons-clock" class="w-4 h-4 text-pure-white/30 flex-shrink-0" />
          {{ name }}
        </button>
        <div class="border-t border-border-gray" />
      </div>

      <!-- Grouped by category -->
      <div v-for="group in results.grouped" :key="group.category">
        <div class="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold" :class="categoryColors[group.category]">
          {{ group.label }}
        </div>
        <button
          v-for="name in group.exercises"
          :key="name"
          type="button"
          class="w-full px-3 py-2.5 text-left text-sm text-pure-white hover:bg-warning-orange/10 transition-colors pl-6"
          @mousedown.prevent="selectExercise(name)"
        >
          {{ name }}
        </button>
      </div>
    </div>
  </div>
</template>
