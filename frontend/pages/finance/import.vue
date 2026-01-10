<script setup lang="ts">
// Redirect to transactions page
// The import functionality is now available as a dialog on the transactions page

definePageMeta({
  layout: 'finance',
})

const router = useRouter()

onMounted(() => {
  router.push('/finance/transactions')
})
</script>

<template>
  <div class="flex items-center justify-center min-h-[50vh]">
    <div class="text-center">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 mx-auto text-electric-green animate-spin mb-4" />
      <p class="text-pure-white/60">
        Redirecting to transactions page...
      </p>
    </div>
  </div>
</template>
