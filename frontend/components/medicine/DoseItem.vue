<script setup lang="ts">
import type { TodayDose } from '~/types/medicine'

interface Props {
  dose: TodayDose
}

const props = defineProps<Props>()
const emit = defineEmits<{
  toggle: [logId: number, taken: boolean]
}>()

const timeLabel = computed(() => {
  // scheduled_time is "HH:MM:SS" or "HH:MM"
  const parts = props.dose.scheduled_time.split(':')
  return `${parts[0]}:${parts[1]}`
})

const dosageLabel = computed(() => {
  if (!props.dose.dosage) return null
  return props.dose.unit
    ? `${props.dose.dosage} ${props.dose.unit}`
    : props.dose.dosage
})

const handleToggle = () => {
  emit('toggle', props.dose.log_id, !props.dose.taken)
}
</script>

<template>
  <div
    class="flex items-center gap-3 py-2.5 px-3 rounded-lg transition-colors"
    :class="dose.taken ? 'bg-electric-green/5' : 'bg-transparent hover:bg-pure-white/5'"
  >
    <!-- Time badge -->
    <div class="flex-shrink-0 w-14 text-center">
      <span
        class="inline-block px-2 py-0.5 rounded text-xs font-mono font-semibold"
        :class="
          dose.taken
            ? 'bg-electric-green/20 text-electric-green'
            : 'bg-border-gray/50 text-pure-white/60'
        "
      >
        {{ timeLabel }}
      </span>
    </div>

    <!-- Color dot -->
    <div class="flex-shrink-0">
      <span
        v-if="dose.medicine_color"
        class="block w-2.5 h-2.5 rounded-full border border-white/10"
        :style="{ backgroundColor: dose.medicine_color }"
      />
      <span
        v-else
        class="block w-2.5 h-2.5 rounded-full bg-pure-white/20"
      />
    </div>

    <!-- Medicine info -->
    <div class="flex-1 min-w-0">
      <p
        class="text-sm font-medium truncate transition-colors"
        :class="dose.taken ? 'text-pure-white/50 line-through' : 'text-pure-white'"
      >
        {{ dose.medicine_name }}
      </p>
      <p
        v-if="dosageLabel"
        class="text-xs text-pure-white/40 mt-0.5"
      >
        {{ dosageLabel }}
      </p>
    </div>

    <!-- Taken toggle -->
    <button
      type="button"
      class="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200 border focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-card-black"
      :class="
        dose.taken
          ? 'bg-electric-green border-electric-green text-background-black focus:ring-electric-green'
          : 'border-border-gray bg-transparent text-pure-white/30 hover:border-electric-green/60 hover:text-electric-green/60 focus:ring-electric-green/50'
      "
      :aria-label="dose.taken ? 'Mark as not taken' : 'Mark as taken'"
      :aria-pressed="dose.taken"
      @click="handleToggle"
    >
      <UIcon
        name="i-heroicons-check"
        class="w-4 h-4"
        :class="dose.taken ? 'opacity-100' : 'opacity-0'"
      />
    </button>
  </div>
</template>
