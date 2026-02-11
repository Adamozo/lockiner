<script setup lang="ts">
definePageMeta({
  layout: 'food',
})

const { fetchCategories, categories } = useFood()
const {
  reminderSettings,
  loading,
  fetchReminderSettings,
  updateReminderSettings,
} = useFoodInventory()

const toast = useToast()

// Local state for editing
const editedSettings = ref({
  enabled: true,
  default_days_before: 3,
  dairy_days_before: 2,
  meat_days_before: 1,
  vegetables_days_before: 2,
  fruits_days_before: 2,
  bread_days_before: 1,
  frozen_days_before: 7,
})

// Fetch data on mount
onMounted(async () => {
  await Promise.all([
    fetchCategories(),
    fetchReminderSettings(),
  ])

  // Initialize form with current settings
  if (reminderSettings.value) {
    editedSettings.value = {
      enabled: reminderSettings.value.enabled,
      default_days_before: reminderSettings.value.default_days_before,
      dairy_days_before: reminderSettings.value.dairy_days_before,
      meat_days_before: reminderSettings.value.meat_days_before,
      vegetables_days_before: reminderSettings.value.vegetables_days_before,
      fruits_days_before: reminderSettings.value.fruits_days_before,
      bread_days_before: reminderSettings.value.bread_days_before,
      frozen_days_before: reminderSettings.value.frozen_days_before,
    }
  }
})

// Save settings
const saveSettings = async () => {
  try {
    await updateReminderSettings(editedSettings.value)
    toast.add({ title: 'Settings saved', color: 'green' })
  } catch (e) {
    toast.add({ title: 'Failed to save settings', color: 'red' })
  }
}

// Reminder settings fields
const reminderFields = [
  { key: 'default_days_before', label: 'Default', icon: 'i-heroicons-clock' },
  { key: 'dairy_days_before', label: 'Dairy', icon: 'i-heroicons-beaker' },
  { key: 'meat_days_before', label: 'Meat', icon: 'i-heroicons-fire' },
  { key: 'vegetables_days_before', label: 'Vegetables', icon: 'i-heroicons-sparkles' },
  { key: 'fruits_days_before', label: 'Fruits', icon: 'i-heroicons-sun' },
  { key: 'bread_days_before', label: 'Bread', icon: 'i-heroicons-cake' },
  { key: 'frozen_days_before', label: 'Frozen', icon: 'i-heroicons-cube-transparent' },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-pure-white">Food Settings</h1>
        <p class="text-pure-white/60 mt-1">Configure categories and notification preferences</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-pure-white/40 animate-spin" />
    </div>

    <template v-else>
      <!-- Notification Settings -->
      <div class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-border-gray flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-cyber-blue/10 flex items-center justify-center">
              <UIcon name="i-heroicons-bell" class="w-5 h-5 text-cyber-blue" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-pure-white">Expiry Reminders</h2>
              <p class="text-pure-white/60 text-sm">Get notified before products expire</p>
            </div>
          </div>
          <UToggle v-model="editedSettings.enabled" />
        </div>

        <div v-if="editedSettings.enabled" class="p-6 space-y-4">
          <p class="text-pure-white/60 text-sm mb-4">
            Set how many days before expiry you want to be reminded for each category.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="field in reminderFields"
              :key="field.key"
              class="flex items-center justify-between p-4 bg-pure-white/5 rounded-lg"
            >
              <div class="flex items-center gap-3">
                <UIcon :name="field.icon" class="w-5 h-5 text-pure-white/60" />
                <span class="text-pure-white">{{ field.label }}</span>
              </div>
              <div class="flex items-center gap-2">
                <UInput
                  v-model.number="(editedSettings as any)[field.key]"
                  type="number"
                  min="1"
                  max="30"
                  class="w-20"
                />
                <span class="text-pure-white/60 text-sm">days</span>
              </div>
            </div>
          </div>

          <div class="pt-4">
            <BaseButton variant="primary" @click="saveSettings">
              Save Settings
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Product Categories -->
      <div class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-border-gray">
          <h2 class="text-lg font-semibold text-pure-white">Product Categories</h2>
          <p class="text-pure-white/60 text-sm mt-1">
            Default expiration days for each category
          </p>
        </div>

        <div v-if="categories.length > 0" class="divide-y divide-border-gray max-h-[480px] overflow-y-auto scrollbar-thin">
          <div
            v-for="category in categories"
            :key="category.id"
            class="px-6 py-4 flex items-center justify-between hover:bg-pure-white/5 transition-colors"
          >
            <div class="flex items-center gap-4">
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center"
                :style="{ backgroundColor: `${category.color}20` }"
              >
                <UIcon
                  :name="`i-heroicons-${category.icon || 'cube'}`"
                  class="w-5 h-5"
                  :style="{ color: category.color }"
                />
              </div>
              <div>
                <p class="text-pure-white font-medium">{{ category.name }}</p>
                <p v-if="category.storage_tips" class="text-pure-white/60 text-sm line-clamp-1">
                  {{ category.storage_tips }}
                </p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-pure-white font-semibold">
                {{ category.default_expiry_days || '-' }} days
              </p>
              <p class="text-pure-white/60 text-xs">default expiration</p>
            </div>
          </div>
        </div>

        <div v-else class="p-6 text-center text-pure-white/60">
          No categories found
        </div>
      </div>
    </template>
  </div>
</template>
