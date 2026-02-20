<script setup lang="ts">
import type { ShoppingListCreate } from '~/types/shopping'

definePageMeta({ layout: 'shopping' })

const { lists, loading, fetchLists, createList, deleteList } = useShoppingLists()

onMounted(() => fetchLists('active'))

const showNewListModal = ref(false)
const createError = ref<string | null>(null)

async function onCreate(data: ShoppingListCreate) {
  createError.value = null
  try {
    const created = await createList(data)
    showNewListModal.value = false
    navigateTo(`/shopping/${created.id}`)
  } catch (e) {
    createError.value = e instanceof Error ? e.message : 'Failed to create list'
  }
}

async function onDelete(listId: number) {
  await deleteList(listId)
}
</script>

<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-pure-white">Shopping Lists</h1>
      <BaseButton variant="primary" @click="showNewListModal = true">
        <span class="i-heroicons-plus text-sm mr-1" />
        New list
      </BaseButton>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <span class="i-heroicons-arrow-path animate-spin text-2xl text-border-gray" />
    </div>

    <!-- Empty state -->
    <div v-else-if="lists.length === 0" class="text-center py-16 space-y-4">
      <span class="i-heroicons-shopping-bag text-5xl text-border-gray" />
      <p class="text-pure-white font-medium">No active lists</p>
      <p class="text-sm text-border-gray">Create a list to start planning your shopping</p>
      <div class="flex justify-center">
        <BaseButton variant="primary" class="max-w-xs w-full" @click="showNewListModal = true">
          Create first list
        </BaseButton>
      </div>
    </div>

    <!-- Lists grid -->
    <div v-else class="space-y-3">
      <ShoppingListCard
        v-for="list in lists"
        :key="list.id"
        :list="list"
        @delete="onDelete"
      />
    </div>

    <!-- New list modal -->
    <ShoppingNewListModal
      v-if="showNewListModal"
      :error="createError"
      @confirm="onCreate"
      @cancel="showNewListModal = false; createError = null"
    />
  </div>
</template>
