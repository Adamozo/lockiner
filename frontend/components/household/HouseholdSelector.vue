<script setup lang="ts">
import { useHouseholdsStore } from '~/stores/households'
import { useHouseholdContext } from '~/composables/useHouseholdContext'
import { useAuthStore } from '~/stores/auth'

interface Props {
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
})

const householdsStore = useHouseholdsStore()
const authStore = useAuthStore()
const { currentHouseholdId, setHouseholdContext, clearHouseholdContext } = useHouseholdContext()
const toast = useToast()

// Dropdown state
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

// Fetch households on mount if authenticated
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await householdsStore.fetchHouseholds()
  }
})

// Watch for auth changes
watch(
  () => authStore.isAuthenticated,
  async (isAuth) => {
    if (isAuth) {
      await householdsStore.fetchHouseholds()
    }
  }
)

// Current context display
const currentContextName = computed(() => {
  if (!currentHouseholdId.value) {
    return 'Personal'
  }
  const household = householdsStore.getHouseholdByUid(currentHouseholdId.value)
  return household?.name || 'Household'
})

const currentContextIcon = computed(() => {
  if (!currentHouseholdId.value) {
    return null
  }
  const household = householdsStore.getHouseholdByUid(currentHouseholdId.value)
  return household?.icon || null
})

// Handle selection
const selectPersonal = () => {
  clearHouseholdContext()
  isOpen.value = false
  toast.add({
    title: 'Context switched',
    description: 'Now viewing personal finances',
    color: 'green',
  })
}

const selectHousehold = (uid: string, name: string) => {
  setHouseholdContext(uid)
  isOpen.value = false
  toast.add({
    title: 'Context switched',
    description: `Now viewing ${name}`,
    color: 'green',
  })
}

// Close dropdown on outside click
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div v-if="authStore.isAuthenticated" ref="dropdownRef" class="relative">
    <!-- Trigger Button -->
    <button
      @click="isOpen = !isOpen"
      class="w-full flex items-center rounded-lg transition-all duration-200 text-pure-white/60 hover:text-pure-white hover:bg-card-black/50"
      :class="collapsed ? 'justify-center px-2 py-3' : 'px-3 py-3 space-x-3'"
      :title="collapsed ? currentContextName : undefined"
    >
      <template v-if="currentHouseholdId && currentContextIcon">
        <span class="text-lg flex-shrink-0">{{ currentContextIcon }}</span>
      </template>
      <template v-else-if="currentHouseholdId">
        <UIcon name="i-heroicons-home" class="w-5 h-5 flex-shrink-0 text-cyber-blue" />
      </template>
      <template v-else>
        <UIcon name="i-heroicons-user" class="w-5 h-5 flex-shrink-0" />
      </template>

      <template v-if="!collapsed">
        <span class="font-medium flex-1 text-left truncate">{{ currentContextName }}</span>
        <UIcon
          :name="isOpen ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
          class="w-4 h-4 flex-shrink-0"
        />
      </template>
    </button>

    <!-- Dropdown Menu -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-2 bg-card-black border border-border-gray rounded-lg shadow-xl overflow-hidden min-w-[200px]"
        :class="collapsed ? 'left-full ml-2 bottom-0' : 'left-0 right-0'"
      >
        <div class="p-1">
          <!-- Personal option -->
          <button
            @click="selectPersonal"
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-left transition-colors"
            :class="!currentHouseholdId
              ? 'bg-cyber-blue/10 text-cyber-blue'
              : 'text-pure-white/80 hover:bg-background-black/50'"
          >
            <UIcon name="i-heroicons-user" class="w-5 h-5 flex-shrink-0" />
            <span class="font-medium">Personal</span>
            <UIcon
              v-if="!currentHouseholdId"
              name="i-heroicons-check"
              class="w-4 h-4 ml-auto"
            />
          </button>

          <!-- Divider -->
          <div v-if="householdsStore.households.length > 0" class="my-1 border-t border-border-gray" />

          <!-- Households label -->
          <div v-if="householdsStore.households.length > 0" class="px-3 py-1.5 text-xs font-medium text-pure-white/40 uppercase tracking-wider">
            Households
          </div>

          <!-- Household options -->
          <button
            v-for="household in householdsStore.households"
            :key="household.uid"
            @click="selectHousehold(household.uid, household.name)"
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-left transition-colors"
            :class="currentHouseholdId === household.uid
              ? 'bg-cyber-blue/10 text-cyber-blue'
              : 'text-pure-white/80 hover:bg-background-black/50'"
          >
            <template v-if="household.icon">
              <span class="text-lg flex-shrink-0">{{ household.icon }}</span>
            </template>
            <template v-else>
              <UIcon name="i-heroicons-home" class="w-5 h-5 flex-shrink-0" />
            </template>
            <span class="font-medium truncate">{{ household.name }}</span>
            <UIcon
              v-if="currentHouseholdId === household.uid"
              name="i-heroicons-check"
              class="w-4 h-4 ml-auto flex-shrink-0"
            />
          </button>

          <!-- Divider -->
          <div class="my-1 border-t border-border-gray" />

          <!-- Manage households link -->
          <NuxtLink
            to="/households"
            @click="isOpen = false"
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-left text-pure-white/60 hover:text-pure-white hover:bg-background-black/50 transition-colors"
          >
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 flex-shrink-0" />
            <span class="font-medium">Manage Households</span>
          </NuxtLink>
        </div>
      </div>
    </Transition>
  </div>
</template>
