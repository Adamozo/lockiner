<script setup lang="ts">
import type { TodoItem, TodoPostponeRequest } from '~/types/todo'

const props = defineProps<{
  item: TodoItem
}>()

const emit = defineEmits<{
  confirm: [data: TodoPostponeRequest]
  cancel: []
}>()

const LAZY_MESSAGES = [
  'Are you sure you need to postpone this? Maybe just 5 minutes to start? 🤔',
  'Future you is already sighing. Do you really want to do this to them?',
  'Statistics say 80% of "I\'ll do it tomorrow" tasks never come back...',
  'Every postponement is a debt you\'ll pay with interest.',
  'If not now, then when? Seriously, when exactly?',
  'This task has already been postponed... maybe it\'s time to just do it?',
]

const message = LAZY_MESSAGES[Math.floor(Math.random() * LAZY_MESSAGES.length)]

const confirmed = ref(false)
const toDate = ref<string>('')
const excuse = ref<'busy' | 'other'>('other')
const loading = ref(false)

onMounted(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  toDate.value = tomorrow.toISOString().split('T')[0]
})

function confirmLazy() {
  confirmed.value = true
}

async function submit() {
  loading.value = true
  try {
    emit('confirm', {
      to_date: toDate.value || null,
      excuse: excuse.value,
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/70" @click="emit('cancel')" />

    <!-- Modal -->
    <div class="relative bg-card-black border border-border-gray rounded-xl p-6 w-full max-w-md space-y-5 shadow-2xl">

      <!-- Motivational phase -->
      <template v-if="!confirmed">
        <div class="text-center space-y-3">
          <div class="w-12 h-12 rounded-full bg-warning-orange/10 border border-warning-orange/30 flex items-center justify-center mx-auto">
            <span class="i-heroicons-exclamation-triangle text-2xl text-warning-orange" />
          </div>

          <h2 class="text-lg font-bold text-pure-white">Hold on...</h2>

          <p class="text-warning-orange font-medium text-sm leading-relaxed">
            {{ message }}
          </p>

          <p class="text-border-gray text-xs">
            Task: <span class="text-pure-white font-medium">{{ item.title }}</span>
          </p>
        </div>

        <div class="flex flex-col gap-2 pt-2">
          <BaseButton variant="secondary" @click="emit('cancel')">
            You're right, I'll do it now
          </BaseButton>
          <button
            class="text-xs text-border-gray hover:text-pure-white transition-colors py-1"
            @click="confirmLazy"
          >
            I really need to postpone it →
          </button>
        </div>
      </template>

      <!-- Postpone config phase -->
      <template v-else>
        <div class="space-y-4">
          <h2 class="text-base font-bold text-pure-white">Postpone task</h2>

          <div>
            <label class="text-xs text-border-gray mb-1.5 block">Postpone to</label>
            <input
              v-model="toDate"
              type="date"
              class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
            />
            <p class="text-xs text-border-gray mt-1">Leave empty to postpone without a date.</p>
          </div>

          <div>
            <label class="text-xs text-border-gray mb-1.5 block">Reason (be honest)</label>
            <select
              v-model="excuse"
              class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
            >
              <option value="busy">I'm genuinely busy</option>
              <option value="other">Other (honestly, I just don't feel like it)</option>
            </select>
          </div>

          <div class="flex gap-2 pt-1">
            <BaseButton variant="primary" :loading="loading" @click="submit">
              Postpone task
            </BaseButton>
            <BaseButton variant="ghost" @click="emit('cancel')">
              Cancel
            </BaseButton>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
