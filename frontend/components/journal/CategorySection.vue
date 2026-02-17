<script setup lang="ts">
import type { JournalCategory, JournalItemCreate } from '~/types/journal'
import { CATEGORY_META } from '~/types/journal'

const props = defineProps<{
  category: JournalCategory
  items: JournalItemCreate[]
}>()

const emit = defineEmits<{
  'update:items': [items: JournalItemCreate[]]
}>()

const meta = computed(() => CATEGORY_META[props.category])

const newItemText = ref('')

const addItem = () => {
  const text = newItemText.value.trim()
  if (!text) return
  const updated = [
    ...props.items,
    { category: props.category, position: props.items.length, content: text },
  ]
  emit('update:items', updated)
  newItemText.value = ''
}

const removeItem = (index: number) => {
  const updated = props.items
    .filter((_, i) => i !== index)
    .map((item, i) => ({ ...item, position: i }))
  emit('update:items', updated)
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    e.preventDefault()
    addItem()
  }
}
</script>

<template>
  <div class="space-y-3">
    <!-- Category Header -->
    <div class="flex items-center gap-2">
      <UIcon :name="meta.icon" class="w-5 h-5" :class="meta.color" />
      <h3 class="font-semibold text-pure-white">{{ meta.label }}</h3>
      <span class="text-xs text-pure-white/40">({{ items.length }})</span>
    </div>

    <!-- Item List -->
    <div v-if="items.length > 0" class="space-y-2">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="flex items-center gap-2 group"
      >
        <span class="text-pure-white/30 text-sm w-4 text-right flex-shrink-0">{{ index + 1 }}.</span>
        <p class="flex-1 text-pure-white/80 text-sm">{{ item.content }}</p>
        <button
          @click="removeItem(index)"
          class="p-2 rounded-lg border border-danger-red/30 text-danger-red/60 hover:text-danger-red hover:border-danger-red/60 hover:bg-danger-red/10 transition-all flex-shrink-0"
        >
          <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Add Item Input -->
    <div class="flex items-center gap-2">
      <input
        v-model="newItemText"
        type="text"
        :placeholder="`Add something you ${category === 'grateful' ? 'are grateful for' : category}...`"
        class="flex-1 bg-background-black border border-border-gray rounded-lg px-3 py-2 text-sm text-pure-white placeholder-pure-white/30 focus:outline-none focus:border-cyber-blue/50 transition-colors"
        @keydown="handleKeydown"
      />
      <button
        @click="addItem"
        :disabled="!newItemText.trim()"
        class="p-2 rounded-lg bg-cyber-blue/10 text-cyber-blue hover:bg-cyber-blue/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
      >
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
