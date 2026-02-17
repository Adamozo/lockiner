<script setup lang="ts">
const today = new Date().toISOString().slice(0, 10)
await navigateTo(`/journal/${today}`, { replace: true })
</script>

<template>
  <div />
</template>
