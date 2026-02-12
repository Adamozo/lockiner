<script setup lang="ts">
interface SetData {
  set_number: number
  reps: number
  weight_kg: number
  completed: boolean
}

const props = defineProps<{
  modelValue: SetData
  setIndex: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: SetData]
  'delete': []
}>()

const update = (field: keyof SetData, value: number | boolean) => {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

const toggleCompleted = () => {
  update('completed', !props.modelValue.completed)
}
</script>

<template>
  <div class="flex items-center gap-2 sm:gap-3">
    <!-- Set number badge -->
    <div
      class="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center text-sm font-bold"
      :class="modelValue.completed ? 'bg-electric-green/20 text-electric-green' : 'bg-border-gray/50 text-pure-white/60'"
    >
      {{ setIndex + 1 }}
    </div>

    <!-- Weight input -->
    <div class="flex-1 min-w-0">
      <label class="text-[10px] uppercase tracking-wider text-pure-white/40 block mb-0.5">kg</label>
      <input
        :value="modelValue.weight_kg"
        type="number"
        inputmode="decimal"
        min="0"
        step="0.5"
        placeholder="0"
        class="w-full min-h-12 px-3 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white text-center text-lg font-semibold focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors"
        @input="update('weight_kg', parseFloat(($event.target as HTMLInputElement).value) || 0)"
      />
    </div>

    <!-- Reps input -->
    <div class="flex-1 min-w-0">
      <label class="text-[10px] uppercase tracking-wider text-pure-white/40 block mb-0.5">reps</label>
      <input
        :value="modelValue.reps"
        type="number"
        inputmode="numeric"
        min="1"
        placeholder="0"
        class="w-full min-h-12 px-3 py-2 rounded-lg border border-border-gray bg-card-black text-pure-white text-center text-lg font-semibold focus:border-warning-orange focus:ring-2 focus:ring-warning-orange/30 focus:outline-none transition-colors"
        @input="update('reps', parseInt(($event.target as HTMLInputElement).value) || 1)"
      />
    </div>

    <!-- Completed toggle -->
    <button
      type="button"
      class="flex-shrink-0 w-10 h-10 sm:w-12 sm:h-12 rounded-lg border flex items-center justify-center transition-all"
      :class="modelValue.completed
        ? 'bg-electric-green/20 border-electric-green text-electric-green'
        : 'border-border-gray text-pure-white/40 hover:border-pure-white/40'"
      @click="toggleCompleted"
    >
      <UIcon name="i-heroicons-check" class="w-5 h-5" />
    </button>

    <!-- Delete button -->
    <button
      type="button"
      class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-pure-white/30 hover:text-danger-red hover:bg-danger-red/10 transition-colors"
      @click="$emit('delete')"
    >
      <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
    </button>
  </div>
</template>
