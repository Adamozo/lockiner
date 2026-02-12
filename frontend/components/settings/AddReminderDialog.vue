<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'submit': [data: {
    custom_name: string
    custom_icon: string
    custom_title: string
    custom_body: string
  }]
}>()

const name = ref('')
const icon = ref('i-heroicons-bell')
const title = ref('')
const body = ref('')
const submitting = ref(false)

const iconOptions = [
  'i-heroicons-bell',
  'i-heroicons-bell-alert',
  'i-heroicons-clock',
  'i-heroicons-calendar',
  'i-heroicons-calendar-days',
  'i-heroicons-check-circle',
  'i-heroicons-clipboard-document-list',
  'i-heroicons-book-open',
  'i-heroicons-academic-cap',
  'i-heroicons-heart',
  'i-heroicons-star',
  'i-heroicons-sun',
  'i-heroicons-moon',
  'i-heroicons-bolt',
  'i-heroicons-fire',
  'i-heroicons-sparkles',
  'i-heroicons-musical-note',
  'i-heroicons-camera',
  'i-heroicons-home',
  'i-heroicons-truck',
  'i-heroicons-shopping-cart',
  'i-heroicons-gift',
  'i-heroicons-phone',
  'i-heroicons-envelope',
]

const isValid = computed(() =>
  name.value.trim().length > 0 &&
  title.value.trim().length > 0 &&
  body.value.trim().length > 0
)

function resetForm() {
  name.value = ''
  icon.value = 'i-heroicons-bell'
  title.value = ''
  body.value = ''
}

function handleSubmit() {
  if (!isValid.value || submitting.value) return
  submitting.value = true
  emit('submit', {
    custom_name: name.value.trim(),
    custom_icon: icon.value,
    custom_title: title.value.trim(),
    custom_body: body.value.trim(),
  })
  submitting.value = false
  resetForm()
}

watch(() => props.modelValue, (open) => {
  if (open) resetForm()
})

const inputClass = 'w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-pure-white text-sm placeholder-pure-white/30 focus:outline-none focus:ring-1 focus:ring-warning-orange/50 focus:border-warning-orange/50'
</script>

<template>
  <BaseModal :model-value="modelValue" title="Add Custom Reminder" max-width="md" @update:model-value="emit('update:modelValue', $event)">
    <form class="space-y-4" @submit.prevent="handleSubmit">
      <!-- Name -->
      <div>
        <label class="block text-sm font-medium text-pure-white/70 mb-1">Reminder Name</label>
        <input
          v-model="name"
          type="text"
          :class="inputClass"
          placeholder="e.g. Meditation"
          maxlength="100"
        />
      </div>

      <!-- Icon picker -->
      <div>
        <label class="block text-sm font-medium text-pure-white/70 mb-2">Icon</label>
        <div class="grid grid-cols-8 gap-2">
          <button
            v-for="opt in iconOptions"
            :key="opt"
            type="button"
            class="w-9 h-9 flex items-center justify-center rounded-lg border transition-all"
            :class="icon === opt
              ? 'border-warning-orange bg-warning-orange/20 ring-1 ring-warning-orange'
              : 'border-border-gray hover:border-pure-white/40 hover:bg-white/5'"
            @click="icon = opt"
          >
            <UIcon
              :name="opt"
              class="w-5 h-5"
              :class="icon === opt ? 'text-warning-orange' : 'text-pure-white/60'"
            />
          </button>
        </div>
      </div>

      <!-- Notification title -->
      <div>
        <label class="block text-sm font-medium text-pure-white/70 mb-1">Notification Title</label>
        <input
          v-model="title"
          type="text"
          :class="inputClass"
          placeholder="e.g. Meditation Reminder"
          maxlength="200"
        />
      </div>

      <!-- Notification body -->
      <div>
        <label class="block text-sm font-medium text-pure-white/70 mb-1">Notification Message</label>
        <textarea
          v-model="body"
          :class="inputClass"
          rows="2"
          placeholder="e.g. Time for your daily meditation session"
          maxlength="500"
        />
      </div>
    </form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <BaseButton variant="ghost" @click="emit('update:modelValue', false)">
          Cancel
        </BaseButton>
        <BaseButton
          variant="primary"
          :disabled="!isValid || submitting"
          :loading="submitting"
          @click="handleSubmit"
        >
          Create Reminder
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>
