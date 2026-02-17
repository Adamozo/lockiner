<script setup lang="ts">
import type { NotificationSchedule } from '~/composables/useNotificationSchedules'

const { schedules, loading, fetchSchedules, bulkUpdateSchedules, createCustomReminder, deleteCustomReminder } = useNotificationSchedules()
const toast = useToast()
const saving = ref(false)
const showAddDialog = ref(false)

// Local draft copy that the user edits (not synced to server until Save)
const draft = ref<NotificationSchedule[]>([])

// Track whether user has unsaved changes
const isDirty = computed(() => {
  if (draft.value.length !== schedules.value.length) return false
  return draft.value.some((d, i) => {
    const s = schedules.value[i]
    return (
      d.enabled !== s.enabled ||
      d.frequency !== s.frequency ||
      d.hour !== s.hour ||
      d.minute !== s.minute ||
      d.day_of_week !== s.day_of_week ||
      d.day_of_month !== s.day_of_month
    )
  })
})

// Sync draft from server data
watch(schedules, (val) => {
  draft.value = val.map(s => ({ ...s }))
}, { immediate: true })

const updateCard = (index: number, updated: NotificationSchedule) => {
  draft.value[index] = updated
}

const handleSave = async () => {
  saving.value = true
  try {
    await bulkUpdateSchedules(
      draft.value.map(d => ({
        reminder_type: d.reminder_type,
        enabled: d.enabled,
        frequency: d.frequency,
        hour: d.hour,
        minute: d.minute,
        day_of_week: d.day_of_week,
        day_of_month: d.day_of_month,
        custom_name: d.custom_name,
        custom_icon: d.custom_icon,
        custom_title: d.custom_title,
        custom_body: d.custom_body,
      })),
    )
    toast.add({
      title: 'Saved',
      description: 'Reminder settings updated successfully',
      color: 'green',
    })
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to save reminder settings',
      color: 'red',
    })
  } finally {
    saving.value = false
  }
}

const handleReset = () => {
  draft.value = schedules.value.map(s => ({ ...s }))
}

const handleAddReminder = async (data: {
  custom_name: string
  custom_icon: string
  custom_title: string
  custom_body: string
}) => {
  try {
    await createCustomReminder(data)
    await fetchSchedules()
    showAddDialog.value = false
    toast.add({
      title: 'Created',
      description: `Custom reminder "${data.custom_name}" created`,
      color: 'green',
    })
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to create custom reminder',
      color: 'red',
    })
  }
}

const handleDeleteReminder = async (reminderType: string) => {
  try {
    await deleteCustomReminder(reminderType)
    await fetchSchedules()
    toast.add({
      title: 'Deleted',
      description: 'Custom reminder deleted',
      color: 'green',
    })
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to delete custom reminder',
      color: 'red',
    })
  }
}

onMounted(() => {
  fetchSchedules()
})
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <!-- Section Header -->
    <div class="px-6 py-4 border-b border-border-gray relative">
      <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-warning-orange to-danger-red" />
      <h2 class="text-xl font-semibold text-pure-white">Reminder Notifications</h2>
      <p class="mt-1 text-sm text-pure-white/60">
        Schedule push notifications to remind you about daily tasks
      </p>
    </div>

    <div class="px-4 sm:px-6 py-6 space-y-3">
      <!-- Loading state -->
      <div v-if="loading" class="text-center py-8 text-pure-white/60">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin mx-auto mb-2" />
        <p class="text-sm">Loading reminder settings...</p>
      </div>

      <!-- Schedule cards -->
      <template v-else>
        <SettingsReminderScheduleCard
          v-for="(schedule, index) in draft"
          :key="schedule.reminder_type"
          :schedule="schedule"
          :disabled="saving"
          @update:schedule="(updated) => updateCard(index, updated)"
          @delete="handleDeleteReminder(schedule.reminder_type)"
        />

        <!-- Save / Reset / Add buttons -->
        <div class="flex items-center gap-3 pt-3">
          <BaseButton
            :variant="isDirty ? 'primary' : 'secondary'"
            :loading="saving"
            :disabled="!isDirty"
            size="sm"
            @click="handleSave"
          >
            Save Changes
          </BaseButton>
          <BaseButton
            v-if="isDirty"
            variant="ghost"
            :disabled="saving"
            size="sm"
            @click="handleReset"
          >
            Reset
          </BaseButton>
          <BaseButton
            variant="warning"
            :disabled="saving"
            size="sm"
            icon="i-heroicons-plus"
            @click="showAddDialog = true"
          >
            Add Reminder
          </BaseButton>
          <span v-if="!isDirty && !saving" class="text-xs text-pure-white/40">
            No unsaved changes
          </span>
        </div>
      </template>

      <!-- Info text -->
      <p class="text-xs text-pure-white/40 mt-4">
        Reminders are sent as push notifications. Make sure you have push notifications enabled in your browser.
      </p>
    </div>

    <!-- Add Reminder Dialog -->
    <SettingsAddReminderDialog
      v-model="showAddDialog"
      @submit="handleAddReminder"
    />
  </div>
</template>
