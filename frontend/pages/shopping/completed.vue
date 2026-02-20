<script setup lang="ts">
definePageMeta({ layout: 'shopping' })

const { lists, loading, fetchLists, deleteList } = useShoppingLists()

onMounted(() => fetchLists('completed'))

async function onDelete(listId: number) {
  await deleteList(listId)
}
</script>

<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <h1 class="text-xl font-bold text-pure-white">Completed Lists</h1>

    <div v-if="loading" class="flex justify-center py-12">
      <span class="i-heroicons-arrow-path animate-spin text-2xl text-border-gray" />
    </div>

    <div v-else-if="lists.length === 0" class="text-center py-16 space-y-3">
      <span class="i-heroicons-check-circle text-5xl text-border-gray" />
      <p class="text-pure-white font-medium">No completed lists yet</p>
      <p class="text-sm text-border-gray">Finished lists will appear here</p>
    </div>

    <div v-else class="space-y-3">
      <ShoppingListCard
        v-for="list in lists"
        :key="list.id"
        :list="list"
        @delete="onDelete"
      />
    </div>
  </div>
</template>
