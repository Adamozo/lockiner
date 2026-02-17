<script setup lang="ts">
const props = defineProps<{
  modelValue: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
}>()

const moodLabels: Record<number, string> = {
  1: 'Terrible',
  2: 'Bad',
  3: 'Poor',
  4: 'Below Avg',
  5: 'Okay',
  6: 'Fine',
  7: 'Good',
  8: 'Great',
  9: 'Excellent',
  10: 'Perfect',
}

const getMoodColor = (score: number): string => {
  if (score <= 3) return 'bg-danger-red'
  if (score <= 5) return 'bg-warning-orange'
  if (score <= 7) return 'bg-cyber-blue'
  return 'bg-electric-green'
}

const getMoodBorderColor = (score: number): string => {
  if (score <= 3) return 'border-danger-red'
  if (score <= 5) return 'border-warning-orange'
  if (score <= 7) return 'border-cyber-blue'
  return 'border-electric-green'
}

const selectMood = (score: number) => {
  emit('update:modelValue', props.modelValue === score ? null : score)
}
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <UIcon name="i-heroicons-face-smile" class="w-5 h-5 text-cyber-blue" />
      <h3 class="font-semibold text-pure-white">Mood</h3>
      <span v-if="modelValue" class="text-sm text-pure-white/60">
        {{ modelValue }}/10 - {{ moodLabels[modelValue] }}
      </span>
    </div>
    <div class="flex gap-1.5 flex-wrap">
      <button
        v-for="score in 10"
        :key="score"
        @click="selectMood(score)"
        class="w-9 h-9 rounded-lg border-2 text-sm font-bold transition-all duration-200"
        :class="
          modelValue === score
            ? `${getMoodColor(score)} ${getMoodBorderColor(score)} text-pure-white scale-110`
            : 'border-border-gray text-pure-white/50 hover:border-pure-white/30 hover:text-pure-white/80'
        "
      >
        {{ score }}
      </button>
    </div>
  </div>
</template>
