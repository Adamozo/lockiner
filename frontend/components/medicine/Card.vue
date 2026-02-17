<script setup lang="ts">
import type { Medicine } from '~/types/medicine'

interface Props {
  medicine: Medicine
}

const props = defineProps<Props>()
const emit = defineEmits<{
  delete: [medicine: Medicine]
}>()

const activeSchedulesCount = computed(() =>
  props.medicine.schedules.filter(s => s.active).length,
)

const dosageLabel = computed(() => {
  if (!props.medicine.dosage) return null
  return props.medicine.unit
    ? `${props.medicine.dosage} ${props.medicine.unit}`
    : props.medicine.dosage
})

const handleEdit = () => {
  navigateTo(`/fitness/medicines/${props.medicine.id}`)
}

const handleDelete = () => {
  emit('delete', props.medicine)
}
</script>

<template>
  <div
    class="bg-card-black border border-border-gray rounded-xl p-4 hover:border-cyber-blue/40 transition-all duration-200 group"
  >
    <div class="flex items-start justify-between gap-3">
      <!-- Left: Info -->
      <div class="flex items-start gap-3 min-w-0 flex-1">
        <!-- Color dot -->
        <div class="flex-shrink-0 mt-1">
          <span
            v-if="medicine.color"
            class="block w-3 h-3 rounded-full border border-white/10"
            :style="{ backgroundColor: medicine.color }"
            :aria-label="`Color: ${medicine.color}`"
          />
          <span
            v-else
            class="block w-3 h-3 rounded-full bg-pure-white/20"
          />
        </div>

        <!-- Text info -->
        <div class="min-w-0 flex-1">
          <h3 class="font-semibold text-pure-white truncate leading-tight">
            {{ medicine.name }}
          </h3>
          <p
            v-if="dosageLabel"
            class="text-sm text-pure-white/60 mt-0.5"
          >
            {{ dosageLabel }}
          </p>

          <!-- Schedules + Badge row -->
          <div class="flex flex-wrap items-center gap-2 mt-2">
            <span class="flex items-center gap-1 text-xs text-pure-white/50">
              <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
              {{ activeSchedulesCount }}
              {{ activeSchedulesCount === 1 ? 'schedule' : 'schedules' }}
            </span>

            <!-- Active/Inactive badge -->
            <span
              class="px-2 py-0.5 rounded text-xs font-medium"
              :class="
                medicine.active
                  ? 'bg-electric-green/10 text-electric-green'
                  : 'bg-pure-white/10 text-pure-white/40'
              "
            >
              {{ medicine.active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Right: Action buttons -->
      <div class="flex items-center gap-1 flex-shrink-0 opacity-80 group-hover:opacity-100 transition-opacity">
        <BaseButton
          icon="i-heroicons-pencil-square"
          variant="ghost"
          size="sm"
          title="Edit medicine"
          aria-label="Edit medicine"
          @click="handleEdit"
        />
        <BaseButton
          icon="i-heroicons-trash"
          variant="ghost"
          size="sm"
          title="Delete medicine"
          aria-label="Delete medicine"
          class="hover:text-danger-red"
          @click="handleDelete"
        />
      </div>
    </div>
  </div>
</template>
