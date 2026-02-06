<script setup lang="ts">
import { useHouseholdsStore } from '~/stores/households'
import { useHouseholdContext } from '~/composables/useHouseholdContext'
import { useAuthStore } from '~/stores/auth'

const householdsStore = useHouseholdsStore()
const authStore = useAuthStore()
const { currentHouseholdId, setHouseholdContext, clearHouseholdContext } = useHouseholdContext()
const toast = useToast()

// Fetch households on mount if authenticated
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await householdsStore.fetchHouseholds()
  }
})

// Current value for select (empty string means Personal)
const selectedValue = computed(() => currentHouseholdId.value || '')

// Handle selection change
const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const value = target.value

  if (value === '') {
    clearHouseholdContext()
    toast.add({
      title: 'Context switched',
      description: 'Now viewing personal finances',
      color: 'green',
    })
  } else {
    const household = householdsStore.getHouseholdByUid(value)
    setHouseholdContext(value)
    toast.add({
      title: 'Context switched',
      description: `Now viewing ${household?.name || 'household'}`,
      color: 'green',
    })
  }
}
</script>

<template>
  <select
    v-if="authStore.isAuthenticated"
    :value="selectedValue"
    @change="handleChange"
    class="w-full px-3 py-2.5 bg-card-black border border-border-gray rounded-lg text-pure-white focus:outline-none focus:border-cyber-blue transition-colors"
  >
    <option value="">Personal</option>
    <option
      v-for="household in householdsStore.households"
      :key="household.uid"
      :value="household.uid"
    >
      {{ household.name }}
    </option>
  </select>
</template>
