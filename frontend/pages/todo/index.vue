<script setup lang="ts">
definePageMeta({ layout: 'todo' })

useSeoMeta({ title: 'Todo – LockIner' })

const today = new Date().toISOString().split('T')[0]

// Redirect to today's list
navigateTo(`/todo/${today}`, { replace: true })
</script>

<template>
  <div />
</template>
