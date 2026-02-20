<script setup lang="ts">
import type { TodoNotificationRule, TodoNotificationRuleCreate } from '~/types/todo'

const { notificationRules, fetchNotificationRules, createNotificationRule, updateNotificationRule, deleteNotificationRule } = useTodo()

onMounted(fetchNotificationRules)

const showForm = ref(false)
const form = reactive<TodoNotificationRuleCreate>({
  label: '',
  trigger_type: 'fixed_time',
  fixed_time: '08:00',
  minutes_before_end: 120,
  interval_minutes: 60,
  window_start: '09:00',
  window_end: '21:00',
  notify_only_if_incomplete: true,
  enabled: true,
})

const loading = ref(false)

function resetForm() {
  form.label = ''
  form.trigger_type = 'fixed_time'
  form.fixed_time = '08:00'
  form.minutes_before_end = 120
  form.interval_minutes = 60
  form.window_start = '09:00'
  form.window_end = '21:00'
  form.notify_only_if_incomplete = true
  form.enabled = true
}

async function addRule() {
  loading.value = true
  try {
    await createNotificationRule({ ...form })
    resetForm()
    showForm.value = false
  } finally {
    loading.value = false
  }
}

async function toggleRule(rule: TodoNotificationRule) {
  await updateNotificationRule(rule.id, { enabled: !rule.enabled })
}

async function removeRule(ruleId: number) {
  await deleteNotificationRule(ruleId)
}

function describeRule(rule: TodoNotificationRule): string {
  if (rule.trigger_type === 'fixed_time') {
    return `Every day at ${rule.fixed_time}`
  }
  if (rule.trigger_type === 'before_end_of_day') {
    const h = Math.floor((rule.minutes_before_end ?? 0) / 60)
    const m = (rule.minutes_before_end ?? 0) % 60
    const parts = []
    if (h > 0) parts.push(`${h}h`)
    if (m > 0) parts.push(`${m}min`)
    return `${parts.join(' ')} before end of day`
  }
  if (rule.trigger_type === 'interval') {
    return `Every ${rule.interval_minutes} min (${rule.window_start}–${rule.window_end})`
  }
  return rule.trigger_type
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-pure-white">Notification rules</h3>
      <BaseButton variant="ghost" size="sm" @click="showForm = !showForm">
        <span class="i-heroicons-plus text-sm mr-1" />
        Add rule
      </BaseButton>
    </div>

    <!-- Existing rules -->
    <div v-if="notificationRules.length > 0" class="space-y-2">
      <div
        v-for="rule in notificationRules"
        :key="rule.id"
        class="flex items-center justify-between p-3 bg-background-black border border-border-gray rounded-lg"
      >
        <div class="flex-1 min-w-0">
          <p class="text-sm text-pure-white font-medium">
            {{ rule.label || 'Unnamed rule' }}
          </p>
          <p class="text-xs text-border-gray mt-0.5">{{ describeRule(rule) }}</p>
          <p v-if="rule.notify_only_if_incomplete" class="text-xs text-cyber-blue mt-0.5">
            Only when there are incomplete tasks
          </p>
        </div>

        <div class="flex items-center gap-2 ml-3">
          <!-- Toggle -->
          <button
            class="relative inline-flex w-9 h-5 rounded-full transition-colors"
            :class="rule.enabled ? 'bg-electric-green' : 'bg-border-gray'"
            @click="toggleRule(rule)"
          >
            <span
              class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
              :class="rule.enabled ? 'translate-x-4' : 'translate-x-0.5'"
            />
          </button>

          <button
            class="p-1.5 rounded text-border-gray hover:text-danger-red hover:bg-danger-red/10 transition-colors"
            @click="removeRule(rule.id)"
          >
            <span class="i-heroicons-trash text-sm" />
          </button>
        </div>
      </div>
    </div>

    <p v-else-if="!showForm" class="text-sm text-border-gray">
      No rules yet. Add one to start receiving task notifications.
    </p>

    <!-- Add rule form -->
    <div v-if="showForm" class="bg-background-black border border-border-gray rounded-lg p-4 space-y-3">
      <div>
        <label class="text-xs text-border-gray mb-1 block">Rule name (optional)</label>
        <input
          v-model="form.label"
          type="text"
          placeholder="e.g. Morning, Evening..."
          class="w-full bg-card-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-cyber-blue focus:outline-none"
        />
      </div>

      <div>
        <label class="text-xs text-border-gray mb-1 block">Trigger type</label>
        <select
          v-model="form.trigger_type"
          class="w-full bg-card-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
        >
          <option value="fixed_time">At a specific time</option>
          <option value="before_end_of_day">X minutes before end of day</option>
          <option value="interval">Every X minutes (within a time window)</option>
        </select>
      </div>

      <!-- fixed_time fields -->
      <template v-if="form.trigger_type === 'fixed_time'">
        <div>
          <label class="text-xs text-border-gray mb-1 block">Time</label>
          <input
            v-model="form.fixed_time"
            type="time"
            class="bg-card-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
          />
        </div>
      </template>

      <!-- before_end_of_day fields -->
      <template v-if="form.trigger_type === 'before_end_of_day'">
        <div>
          <label class="text-xs text-border-gray mb-1 block">Minutes before 23:59</label>
          <input
            v-model.number="form.minutes_before_end"
            type="number"
            min="1"
            max="1439"
            placeholder="e.g. 120 = at 21:59"
            class="w-full bg-card-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-cyber-blue focus:outline-none"
          />
        </div>
      </template>

      <!-- interval fields -->
      <template v-if="form.trigger_type === 'interval'">
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label class="text-xs text-border-gray mb-1 block">Every (min)</label>
            <input
              v-model.number="form.interval_minutes"
              type="number"
              min="5"
              max="1440"
              class="w-full bg-card-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
            />
          </div>
          <div>
            <label class="text-xs text-border-gray mb-1 block">From</label>
            <input
              v-model="form.window_start"
              type="time"
              class="w-full bg-card-black border border-border-gray rounded-lg px-2 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
            />
          </div>
          <div>
            <label class="text-xs text-border-gray mb-1 block">Until</label>
            <input
              v-model="form.window_end"
              type="time"
              class="w-full bg-card-black border border-border-gray rounded-lg px-2 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
            />
          </div>
        </div>
      </template>

      <!-- Only if incomplete -->
      <label class="flex items-center gap-2 cursor-pointer">
        <input
          v-model="form.notify_only_if_incomplete"
          type="checkbox"
          class="w-4 h-4 rounded border-border-gray bg-background-black accent-cyber-blue"
        />
        <span class="text-sm text-pure-white">Only send when there are incomplete tasks</span>
      </label>

      <div class="flex gap-2">
        <BaseButton variant="primary" size="sm" :loading="loading" @click="addRule">
          Add rule
        </BaseButton>
        <BaseButton variant="ghost" size="sm" @click="showForm = false; resetForm()">
          Cancel
        </BaseButton>
      </div>
    </div>
  </div>
</template>
