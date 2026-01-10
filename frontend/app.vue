<script setup lang="ts">
// Initialize categories store on app mount
const categoriesStore = useCategoriesStore()

onMounted(async () => {
  try {
    await categoriesStore.fetchCategories()
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
})
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <NuxtLoadingIndicator />
    <NuxtLayout>
      <NuxtPage :transition="{ name: 'page', mode: 'out-in' }" />
    </NuxtLayout>
  </div>
</template>
