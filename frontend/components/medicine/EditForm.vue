<script setup lang="ts">
import type { Medicine, MedicineUpdate } from '~/types/medicine'

const props = defineProps<{
  medicine: Medicine
}>()

const emit = defineEmits<{
  save: [data: MedicineUpdate]
  cancel: []
}>()

const form = reactive<MedicineUpdate>({
  name: props.medicine.name,
  description: props.medicine.description,
  dosage: props.medicine.dosage,
  unit: props.medicine.unit,
  color: props.medicine.color,
  active: props.medicine.active,
})

const COLOR_OPTIONS = [
  { value: '#3b82f6', label: 'Blue' },
  { value: '#10b981', label: 'Green' },
  { value: '#f59e0b', label: 'Orange' },
  { value: '#ef4444', label: 'Red' },
  { value: '#8b5cf6', label: 'Purple' },
  { value: '#06b6d4', label: 'Cyan' },
  { value: '#ec4899', label: 'Pink' },
  { value: '#6b7280', label: 'Gray' },
]

const labelClass = 'block text-xs font-medium text-pure-white/60 uppercase tracking-wider mb-1'
const inputClass = 'w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-pure-white text-sm placeholder-pure-white/30 focus:outline-none focus:border-cyber-blue/60 transition-colors'

const handleSubmit = () => {
  emit('save', { ...form })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <!-- Name -->
    <div>
      <label for="med-name" :class="labelClass">Name</label>
      <input
        id="med-name"
        v-model="form.name"
        type="text"
        required
        placeholder="Medicine name"
        :class="inputClass"
      />
    </div>

    <!-- Description -->
    <div>
      <label for="med-description" :class="labelClass">Description</label>
      <textarea
        id="med-description"
        v-model="form.description"
        rows="2"
        placeholder="Optional description"
        :class="[inputClass, 'resize-none']"
      />
    </div>

    <!-- Dosage + Unit (side by side) -->
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label for="med-dosage" :class="labelClass">Dosage</label>
        <input
          id="med-dosage"
          v-model="form.dosage"
          type="text"
          placeholder="e.g. 500"
          :class="inputClass"
        />
      </div>
      <div>
        <label for="med-unit" :class="labelClass">Unit</label>
        <input
          id="med-unit"
          v-model="form.unit"
          type="text"
          placeholder="e.g. mg"
          :class="inputClass"
        />
      </div>
    </div>

    <!-- Color picker -->
    <div>
      <span :class="labelClass">Color</span>
      <div class="flex flex-wrap gap-2 mt-1">
        <button
          v-for="opt in COLOR_OPTIONS"
          :key="opt.value"
          type="button"
          :title="opt.label"
          class="w-7 h-7 rounded-full border-2 transition-all duration-150 focus:outline-none"
          :style="{ backgroundColor: opt.value }"
          :class="form.color === opt.value
            ? 'border-pure-white scale-110'
            : 'border-transparent hover:border-pure-white/50'"
          @click="form.color = opt.value"
        />
        <!-- Clear color -->
        <button
          type="button"
          title="No color"
          class="w-7 h-7 rounded-full border-2 border-dashed transition-all duration-150 focus:outline-none flex items-center justify-center"
          :class="!form.color
            ? 'border-pure-white'
            : 'border-border-gray hover:border-pure-white/50'"
          @click="form.color = null"
        >
          <UIcon name="i-heroicons-x-mark" class="w-3.5 h-3.5 text-pure-white/50" />
        </button>
      </div>
    </div>

    <!-- Active toggle -->
    <div class="flex items-center justify-between py-1">
      <div>
        <p class="text-sm font-medium text-pure-white">Active</p>
        <p class="text-xs text-pure-white/40">Show in today's dose list</p>
      </div>
      <button
        type="button"
        class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-electric-green/50"
        :class="form.active ? 'bg-electric-green' : 'bg-border-gray'"
        role="switch"
        :aria-checked="form.active"
        @click="form.active = !form.active"
      >
        <span
          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200"
          :class="form.active ? 'translate-x-5' : 'translate-x-0'"
        />
      </button>
    </div>

    <!-- Actions -->
    <div class="flex gap-3 pt-2">
      <BaseButton type="submit" variant="primary" class="flex-1">
        <UIcon name="i-heroicons-check" class="w-4 h-4" />
        Save
      </BaseButton>
      <BaseButton type="button" variant="secondary" class="flex-1" @click="emit('cancel')">
        Cancel
      </BaseButton>
    </div>
  </form>
</template>
