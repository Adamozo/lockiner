<script setup lang="ts">
import type { TodoItem, TodoItemCreate, TodoItemUpdate } from '~/types/todo'

const props = defineProps<{
  item?: TodoItem | null
  listId: number
}>()

const emit = defineEmits<{
  saved: [item: TodoItem]
  cancel: []
}>()

const { addItem, updateItem } = useTodo()

const form = reactive<TodoItemCreate>({
  title: props.item?.title ?? '',
  description: props.item?.description ?? null,
  estimated_minutes: props.item?.estimated_minutes ?? null,
  priority: props.item?.priority ?? 'medium',
  item_reminder_enabled: props.item?.item_reminder_enabled ?? false,
  item_reminder_time: props.item?.item_reminder_time ?? null,
})

const loading = ref(false)

const isEdit = computed(() => !!props.item)

async function submit() {
  if (!form.title.trim()) return
  loading.value = true
  try {
    let saved: TodoItem
    if (isEdit.value && props.item) {
      saved = await updateItem(props.item.id, form as TodoItemUpdate)
    } else {
      saved = await addItem(props.listId, form)
    }
    emit('saved', saved)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg p-4 space-y-4">
    <h3 class="text-sm font-semibold text-pure-white">
      {{ isEdit ? 'Edit task' : 'New task' }}
    </h3>

    <!-- Title -->
    <div>
      <input
        v-model="form.title"
        type="text"
        placeholder="What needs to be done?"
        class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-cyber-blue focus:outline-none"
        @keydown.enter="submit"
        @keydown.escape="emit('cancel')"
      />
    </div>

    <!-- Description -->
    <textarea
      v-model="form.description"
      placeholder="Details (optional)"
      rows="2"
      class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-cyber-blue focus:outline-none resize-none"
    />

    <!-- Row: priority + time estimate -->
    <div class="flex gap-3">
      <div class="flex-1">
        <label class="text-xs text-border-gray mb-1 block">Priority</label>
        <select
          v-model="form.priority"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div class="flex-1">
        <label class="text-xs text-border-gray mb-1 block">Estimated time (min)</label>
        <input
          v-model.number="form.estimated_minutes"
          type="number"
          min="1"
          max="1440"
          placeholder="e.g. 30"
          class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-border-gray focus:border-cyber-blue focus:outline-none"
        />
      </div>
    </div>

    <!-- Item reminder -->
    <div class="flex items-center gap-3">
      <label class="flex items-center gap-2 cursor-pointer">
        <input
          v-model="form.item_reminder_enabled"
          type="checkbox"
          class="w-4 h-4 rounded border-border-gray bg-background-black accent-cyber-blue"
        />
        <span class="text-sm text-pure-white">Task reminder</span>
      </label>
      <input
        v-if="form.item_reminder_enabled"
        v-model="form.item_reminder_time"
        type="time"
        class="bg-background-black border border-border-gray rounded-lg px-2 py-1.5 text-sm text-pure-white focus:border-cyber-blue focus:outline-none"
      />
    </div>

    <!-- Actions -->
    <div class="flex gap-2 pt-1">
      <BaseButton variant="primary" size="sm" :loading="loading" @click="submit">
        {{ isEdit ? 'Save' : 'Add task' }}
      </BaseButton>
      <BaseButton variant="ghost" size="sm" @click="emit('cancel')">
        Cancel
      </BaseButton>
    </div>
  </div>
</template>
