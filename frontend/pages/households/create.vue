<script setup lang="ts">
import { useHouseholds } from '~/composables/useHouseholds'

definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: 'Create Household - LockIner',
  description: 'Create a new household',
})

const router = useRouter()
const toast = useToast()
const { createHousehold, loading } = useHouseholds()

// Form state
const form = ref({
  name: '',
  description: '',
  icon: '',
})

const errors = ref({
  name: '',
  general: '',
})

// Available icons for selection
const availableIcons = ['🏠', '🏡', '🏢', '🏘️', '🏰', '👨‍👩‍👧‍👦', '👪', '🏠', '🏛️', '🏗️']

// Validation
const validateForm = (): boolean => {
  errors.value = { name: '', general: '' }

  if (!form.value.name || form.value.name.trim().length < 2) {
    errors.value.name = 'Name must be at least 2 characters'
    return false
  }

  if (form.value.name.trim().length > 100) {
    errors.value.name = 'Name must be less than 100 characters'
    return false
  }

  return true
}

// Submit handler
const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    const household = await createHousehold({
      name: form.value.name.trim(),
      description: form.value.description.trim() || null,
      icon: form.value.icon || null,
    })

    toast.add({
      title: 'Household created',
      description: `"${household.name}" has been created successfully`,
      color: 'green',
    })

    await router.push(`/households/${household.uid}`)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    errors.value.general = err.data?.detail || 'Failed to create household'
  }
}

// Select icon
const selectIcon = (icon: string) => {
  form.value.icon = form.value.icon === icon ? '' : icon
}
</script>

<template>
  <div class="max-w-2xl mx-auto space-y-8">
    <!-- Page header -->
    <header>
      <NuxtLink
        to="/households"
        class="inline-flex items-center gap-2 text-pure-white/60 hover:text-pure-white transition-colors mb-4"
      >
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        <span>Back to Households</span>
      </NuxtLink>
      <h1 class="text-3xl font-bold text-pure-white">Create Household</h1>
      <p class="mt-2 text-pure-white/60">
        Create a new household to share expenses with others
      </p>
    </header>

    <!-- Form card -->
    <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 border-b border-border-gray relative">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
        <h2 class="text-xl font-semibold text-pure-white">Household Details</h2>
      </div>

      <form @submit.prevent="handleSubmit" class="px-6 py-6 space-y-6">
        <!-- General error -->
        <div
          v-if="errors.general"
          class="p-4 bg-danger-red/10 border border-danger-red/30 rounded-lg"
        >
          <div class="flex items-center gap-2 text-danger-red">
            <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 flex-shrink-0" />
            <span class="text-sm">{{ errors.general }}</span>
          </div>
        </div>

        <!-- Name -->
        <div>
          <label for="name" class="block text-sm font-medium text-pure-white mb-2">
            Household Name <span class="text-danger-red">*</span>
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            placeholder="e.g., Smith Family, Apartment 42"
            :class="[
              'w-full px-4 py-2.5 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              errors.name
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30'
            ]"
          />
          <p v-if="errors.name" class="mt-1 text-sm text-danger-red">{{ errors.name }}</p>
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-pure-white mb-2">
            Description
          </label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            placeholder="Optional description for your household"
            class="w-full px-4 py-2.5 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 focus:border-cyber-blue focus:ring-cyber-blue/30 transition-colors resize-none"
          />
        </div>

        <!-- Icon selection -->
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">
            Icon (optional)
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="icon in availableIcons"
              :key="icon"
              type="button"
              class="w-12 h-12 rounded-lg border text-2xl flex items-center justify-center transition-all duration-200"
              :class="form.icon === icon
                ? 'border-cyber-blue bg-cyber-blue/10'
                : 'border-border-gray hover:border-cyber-blue/50 bg-background-black'"
              @click="selectIcon(icon)"
            >
              {{ icon }}
            </button>
          </div>
          <p class="mt-2 text-sm text-pure-white/40">
            Click to select an icon, click again to deselect
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-4 pt-4">
          <BaseButton
            type="submit"
            variant="primary"
            :loading="loading"
            icon="i-heroicons-plus"
          >
            Create Household
          </BaseButton>
          <NuxtLink to="/households">
            <BaseButton variant="secondary">
              Cancel
            </BaseButton>
          </NuxtLink>
        </div>
      </form>
    </div>

    <!-- Info box -->
    <div class="p-4 bg-electric-green/10 border border-electric-green/30 rounded-lg">
      <div class="flex">
        <UIcon
          name="i-heroicons-light-bulb"
          class="w-5 h-5 text-electric-green mr-3 flex-shrink-0 mt-0.5"
        />
        <div class="text-sm text-pure-white/80">
          <p class="font-medium text-pure-white mb-1">You'll be the manager</p>
          <p>
            As the creator, you'll automatically become the manager of this household.
            Managers can invite members, manage roles, and delete the household.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
