<script setup lang="ts">
import type { TodoItem } from '~/types/todo'

definePageMeta({ layout: 'todo' })

const route = useRoute()
const dateParam = computed(() => route.params.date as string)

const {
  currentList,
  loading,
  error,
  completedItems,
  pendingItems,
  completionProgress,
  estimatedMinutesRemaining,
  fetchListByDate,
  createList,
  completeItem,
  deleteItem,
  postponeItem,
} = useTodo()

onMounted(async () => {
  await fetchListByDate(dateParam.value)
})

watch(dateParam, async (newDate) => {
  await fetchListByDate(newDate)
})

const formattedDate = computed(() => {
  const d = new Date(dateParam.value + 'T00:00:00')
  return d.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
})

const isToday = computed(() => dateParam.value === new Date().toISOString().split('T')[0])

const showItemForm = ref(false)
const editingItem = ref<TodoItem | null>(null)

function startEdit(item: TodoItem) {
  editingItem.value = item
  showItemForm.value = false
}

async function onItemSaved() {
  editingItem.value = null
  showItemForm.value = false
  await fetchListByDate(dateParam.value)
}

const postponingItem = ref<TodoItem | null>(null)

async function onPostpone(data: { to_date?: string | null; excuse: 'busy' | 'other' }) {
  if (!postponingItem.value) return
  await postponeItem(postponingItem.value.id, data)
  postponingItem.value = null
}

async function handleCreateList() {
  const d = new Date(dateParam.value + 'T00:00:00')
  const defaultTitle = `List for ${d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long' })}`
  await createList({ title: defaultTitle, date: dateParam.value })
}

const showNotifications = ref(false)

const progressColor = computed(() => {
  if (completionProgress.value === 100) return 'bg-electric-green'
  if (completionProgress.value >= 50) return 'bg-cyber-blue'
  return 'bg-warning-orange'
})

function goToDay(offset: number) {
  const d = new Date(dateParam.value + 'T00:00:00')
  d.setDate(d.getDate() + offset)
  navigateTo(`/todo/${d.toISOString().split('T')[0]}`)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button
          class="p-1.5 rounded-lg text-border-gray hover:text-pure-white hover:bg-card-black transition-colors"
          @click="goToDay(-1)"
        >
          <span class="i-heroicons-chevron-left text-lg" />
        </button>

        <div>
          <h1 class="text-xl font-bold text-pure-white capitalize">{{ formattedDate }}</h1>
          <p v-if="isToday" class="text-xs text-cyber-blue mt-0.5">Today</p>
        </div>

        <button
          class="p-1.5 rounded-lg text-border-gray hover:text-pure-white hover:bg-card-black transition-colors"
          @click="goToDay(1)"
        >
          <span class="i-heroicons-chevron-right text-lg" />
        </button>
      </div>

      <button
        class="p-2 rounded-lg text-border-gray hover:text-cyber-blue hover:bg-cyber-blue/10 transition-colors"
        title="Reminder rules"
        @click="showNotifications = !showNotifications"
      >
        <span class="i-heroicons-bell text-lg" />
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <span class="i-heroicons-arrow-path animate-spin text-2xl text-border-gray" />
    </div>

    <!-- No list exists -->
    <div v-else-if="!currentList" class="text-center py-16 space-y-4">
      <span class="i-heroicons-clipboard-document-list text-5xl text-border-gray" />
      <p class="text-pure-white font-medium">No list for this day</p>
      <p class="text-sm text-border-gray">Create a list to start planning</p>
      <BaseButton variant="primary" @click="handleCreateList">
        Create list
      </BaseButton>
    </div>

    <!-- List exists -->
    <template v-else>
      <!-- Progress bar -->
      <div v-if="currentList.items.length > 0" class="space-y-2">
        <div class="flex items-center justify-between text-xs text-border-gray">
          <span>{{ completedItems.length }}/{{ currentList.items.length }} tasks</span>
          <span v-if="estimatedMinutesRemaining > 0">~{{ estimatedMinutesRemaining }} min remaining</span>
          <span v-if="completionProgress === 100" class="text-electric-green font-medium">All done!</span>
        </div>
        <div class="h-1.5 bg-background-black rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="progressColor"
            :style="{ width: `${completionProgress}%` }"
          />
        </div>
      </div>

      <!-- Notification config panel -->
      <div v-if="showNotifications" class="bg-card-black border border-border-gray rounded-xl p-4">
        <TodoNotificationRules />
      </div>

      <!-- Items list -->
      <div class="space-y-2">
        <!-- Inline edit form -->
        <div v-if="editingItem" class="mb-3">
          <TodoItemForm
            :item="editingItem"
            :list-id="currentList.id"
            @saved="onItemSaved"
            @cancel="editingItem = null"
          />
        </div>

        <!-- Pending items -->
        <template v-if="pendingItems.length > 0">
          <TodoItemRow
            v-for="item in pendingItems"
            :key="item.id"
            :item="item"
            @complete="completeItem($event, true)"
            @edit="startEdit"
            @postpone="postponingItem = $event"
            @delete="deleteItem"
          />
        </template>

        <!-- Completed items -->
        <details v-if="completedItems.length > 0" class="mt-4">
          <summary class="text-xs text-border-gray cursor-pointer hover:text-pure-white transition-colors select-none">
            Completed ({{ completedItems.length }})
          </summary>
          <div class="mt-2 space-y-2">
            <TodoItemRow
              v-for="item in completedItems"
              :key="item.id"
              :item="item"
              @complete="completeItem($event, false)"
              @edit="startEdit"
              @postpone="postponingItem = $event"
              @delete="deleteItem"
            />
          </div>
        </details>

        <!-- Empty state -->
        <p v-if="currentList.items.length === 0" class="text-center text-sm text-border-gray py-8">
          The list is empty. Add your first task!
        </p>
      </div>

      <!-- Add item section -->
      <div>
        <div v-if="showItemForm && !editingItem">
          <TodoItemForm
            :list-id="currentList.id"
            @saved="onItemSaved"
            @cancel="showItemForm = false"
          />
        </div>
        <div v-else-if="!editingItem" class="flex justify-center">
          <BaseButton
            variant="primary"
            class="max-w-xs w-full"
            @click="showItemForm = true"
          >
            <span class="i-heroicons-plus text-sm mr-1" />
            Add task
          </BaseButton>
        </div>
      </div>
    </template>

    <!-- Postpone modal -->
    <TodoPostponeModal
      v-if="postponingItem"
      :item="postponingItem"
      @confirm="onPostpone"
      @cancel="postponingItem = null"
    />
  </div>
</template>
