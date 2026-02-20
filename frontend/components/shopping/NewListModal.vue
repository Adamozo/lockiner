<script setup lang="ts">
import type { ShoppingListCreate } from '~/types/shopping'

defineProps<{ error?: string | null }>()

const emit = defineEmits<{
  confirm: [data: ShoppingListCreate]
  cancel: []
}>()

const { households, fetchHouseholds } = useHouseholds()
onMounted(() => fetchHouseholds(true))

const form = reactive({
  name: '',
  store_name: null as string | null,
  planned_date: null as string | null,
  visibility: 'private' as 'private' | 'household',
  notes: null as string | null,
})

// Separate string ref for the select — v-model on native <select> always returns strings
const selectedHouseholdStr = ref('')

watch(() => form.visibility, (v) => {
  if (v !== 'household') selectedHouseholdStr.value = ''
})

const isValid = computed(() => {
  if (!form.name.trim()) return false
  if (form.visibility === 'household') {
    const id = Number(selectedHouseholdStr.value)
    if (!Number.isFinite(id) || id <= 0) return false
  }
  return true
})

const loading = ref(false)

async function submit() {
  if (!isValid.value) return
  loading.value = true
  const payload = {
    ...form,
    household_id: selectedHouseholdStr.value ? Number(selectedHouseholdStr.value) : null,
  }
  try {
    emit('confirm', payload)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <BaseModal :model-value="true" title="New shopping list" @update:model-value="emit('cancel')">
    <div class="space-y-4">
      <!-- Name -->
      <div>
        <label class="text-xs text-border-gray mb-1 block">List name *</label>
        <input
          v-model="form.name"
          type="text"
          placeholder="e.g. Weekly groceries, Biedronka, Hardware store"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
          @keydown.enter="submit"
        />
      </div>

      <!-- Store name -->
      <div>
        <label class="text-xs text-border-gray mb-1 block">Store (optional)</label>
        <input
          v-model="form.store_name"
          type="text"
          placeholder="e.g. Lidl, Leroy Merlin"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
        />
      </div>

      <!-- Planned date -->
      <div>
        <label class="text-xs text-border-gray mb-1 block">Planned date (optional)</label>
        <input
          v-model="form.planned_date"
          type="date"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-warning-orange focus:outline-none"
        />
      </div>

      <!-- Visibility -->
      <div>
        <label class="text-xs text-border-gray mb-1 block">Visibility</label>
        <select
          v-model="form.visibility"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-warning-orange focus:outline-none"
        >
          <option value="private">Private (only me)</option>
          <option value="household" :disabled="households.length === 0">
            Household (shared){{ households.length === 0 ? ' — no households' : '' }}
          </option>
        </select>
      </div>

      <!-- Household selector -->
      <div v-if="form.visibility === 'household'">
        <label class="text-xs text-border-gray mb-1 block">Select household *</label>
        <select
          v-model="selectedHouseholdStr"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-warning-orange focus:outline-none"
          :class="{ 'border-danger-red': form.visibility === 'household' && !selectedHouseholdStr }"
        >
          <option value="" disabled>— choose household —</option>
          <option v-for="h in households" :key="h.id" :value="String(h.id)">
            {{ h.name }}
          </option>
        </select>
      </div>

      <!-- Error -->
      <p v-if="error" class="text-sm text-danger-red">{{ error }}</p>

      <!-- Actions -->
      <div class="flex gap-2 pt-1">
        <BaseButton variant="primary" :loading="loading" :disabled="!isValid" @click="submit">
          Create list
        </BaseButton>
        <BaseButton variant="ghost" @click="emit('cancel')">
          Cancel
        </BaseButton>
      </div>
    </div>
  </BaseModal>
</template>
