<script setup lang="ts">
import type { TodoItem } from '~/types/todo'

const props = defineProps<{
  item: TodoItem
}>()

const emit = defineEmits<{
  complete: [id: number, completed: boolean]
  edit: [item: TodoItem]
  postpone: [item: TodoItem]
  delete: [id: number]
}>()

const priorityColors: Record<string, string> = {
  high: 'text-danger-red border-danger-red',
  medium: 'text-warning-orange border-warning-orange',
  low: 'text-border-gray border-border-gray',
}

const priorityLabel: Record<string, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}
</script>

<template>
  <div
    class="flex items-start gap-3 p-3 rounded-lg border transition-all"
    :class="item.completed
      ? 'bg-background-black border-border-gray opacity-60'
      : 'bg-card-black border-border-gray hover:border-cyber-blue/40'"
  >
    <!-- Checkbox -->
    <button
      class="mt-0.5 flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors"
      :class="item.completed
        ? 'bg-electric-green border-electric-green'
        : 'border-border-gray hover:border-electric-green'"
      @click="emit('complete', item.id, !item.completed)"
    >
      <span v-if="item.completed" class="i-heroicons-check text-xs text-background-black" />
    </button>

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <p
        class="text-sm font-medium leading-snug"
        :class="item.completed ? 'line-through text-border-gray' : 'text-pure-white'"
      >
        {{ item.title }}
      </p>

      <p v-if="item.description" class="text-xs text-border-gray mt-0.5 truncate">
        {{ item.description }}
      </p>

      <!-- Meta row -->
      <div class="flex items-center gap-3 mt-1.5 flex-wrap">
        <!-- Priority badge -->
        <span
          class="text-xs border rounded px-1.5 py-0.5"
          :class="priorityColors[item.priority]"
        >
          {{ priorityLabel[item.priority] }}
        </span>

        <!-- Estimated time -->
        <span v-if="item.estimated_minutes" class="text-xs text-border-gray flex items-center gap-1">
          <span class="i-heroicons-clock text-xs" />
          {{ item.estimated_minutes }} min
        </span>

        <!-- Reminder -->
        <span v-if="item.item_reminder_enabled && item.item_reminder_time" class="text-xs text-cyber-blue flex items-center gap-1">
          <span class="i-heroicons-bell text-xs" />
          {{ item.item_reminder_time }}
        </span>

        <!-- Postponed badge -->
        <span v-if="item.postponed_count > 0" class="text-xs text-warning-orange flex items-center gap-1">
          <span class="i-heroicons-arrow-uturn-right text-xs" />
          Postponed {{ item.postponed_count }}x
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div v-if="!item.completed" class="flex-shrink-0 flex items-center gap-1">
      <button
        class="p-1.5 rounded text-border-gray hover:text-pure-white hover:bg-border-gray/20 transition-colors"
        title="Edit"
        @click="emit('edit', item)"
      >
        <span class="i-heroicons-pencil-square text-sm" />
      </button>
      <button
        class="p-1.5 rounded text-border-gray hover:text-warning-orange hover:bg-warning-orange/10 transition-colors"
        title="Postpone"
        @click="emit('postpone', item)"
      >
        <span class="i-heroicons-arrow-uturn-right text-sm" />
      </button>
      <button
        class="p-1.5 rounded text-border-gray hover:text-danger-red hover:bg-danger-red/10 transition-colors"
        title="Delete"
        @click="emit('delete', item.id)"
      >
        <span class="i-heroicons-trash text-sm" />
      </button>
    </div>
  </div>
</template>
