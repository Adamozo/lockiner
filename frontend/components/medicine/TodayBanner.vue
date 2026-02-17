<script setup lang="ts">
import type { TodayDose } from '~/types/medicine'

interface Props {
  doses: TodayDose[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<{
  toggle: [logId: number, taken: boolean]
}>()

const takenCount = computed(() => props.doses.filter(d => d.taken).length)
const totalCount = computed(() => props.doses.length)

const progressPercent = computed(() => {
  if (totalCount.value === 0) return 100
  return Math.round((takenCount.value / totalCount.value) * 100)
})

const allDone = computed(() => totalCount.value > 0 && takenCount.value === totalCount.value)

// Sort doses by scheduled time
const sortedDoses = computed(() =>
  [...props.doses].sort((a, b) => a.scheduled_time.localeCompare(b.scheduled_time)),
)
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-xl p-5">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <div
          class="p-2 rounded-lg"
          :class="allDone ? 'bg-electric-green/20' : 'bg-warning-orange/20'"
        >
          <UIcon
            :name="allDone ? 'i-heroicons-check-circle' : 'i-heroicons-clock'"
            class="w-5 h-5"
            :class="allDone ? 'text-electric-green' : 'text-warning-orange'"
          />
        </div>
        <div>
          <h2 class="font-semibold text-pure-white leading-tight">
            Today's Medicines
          </h2>
          <p class="text-xs text-pure-white/50">
            {{ new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) }}
          </p>
        </div>
      </div>

      <!-- Dose count -->
      <div class="text-right">
        <span class="text-lg font-bold text-pure-white">
          {{ takenCount }}<span class="text-pure-white/40">/{{ totalCount }}</span>
        </span>
        <p class="text-xs text-pure-white/50">doses taken</p>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="relative h-2 bg-background-black rounded-full overflow-hidden mb-5">
      <div
        class="absolute top-0 left-0 h-full rounded-full bg-gradient-to-r from-warning-orange to-electric-green transition-all duration-500"
        :style="{ width: `${progressPercent}%` }"
        :aria-valuenow="progressPercent"
        aria-valuemin="0"
        aria-valuemax="100"
        role="progressbar"
        :aria-label="`${takenCount} of ${totalCount} doses taken`"
      />
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-2">
      <div
        v-for="i in 3"
        :key="i"
        class="h-10 bg-pure-white/5 rounded-lg animate-pulse"
      />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="doses.length === 0"
      class="flex flex-col items-center justify-center py-6 text-center"
    >
      <UIcon name="i-heroicons-beaker" class="w-8 h-8 text-pure-white/20 mb-2" />
      <p class="text-sm text-pure-white/40">No doses scheduled for today</p>
    </div>

    <!-- All done banner -->
    <div
      v-else-if="allDone"
      class="flex items-center gap-3 p-3 bg-electric-green/10 border border-electric-green/20 rounded-lg mb-3"
    >
      <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-electric-green flex-shrink-0" />
      <p class="text-sm text-electric-green font-medium">
        All doses taken for today!
      </p>
    </div>

    <!-- Dose list -->
    <div v-if="!loading && doses.length > 0" class="space-y-1">
      <MedicineDoseItem
        v-for="dose in sortedDoses"
        :key="dose.log_id"
        :dose="dose"
        @toggle="(logId, taken) => emit('toggle', logId, taken)"
      />
    </div>
  </div>
</template>
