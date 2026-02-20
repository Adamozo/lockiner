<script setup lang="ts">
definePageMeta({ layout: 'todo' })

useSeoMeta({ title: 'Todo – Reminder Rules – LockIner' })
</script>

<template>
  <div class="space-y-6 max-w-lg">
    <h1 class="text-xl font-bold text-pure-white">Reminder rules</h1>

    <p class="text-sm text-border-gray">
      Configure when you want to receive notifications about your tasks. You can add as many rules as you need.
    </p>

    <div class="bg-card-black border border-border-gray rounded-xl p-5">
      <TodoNotificationRules />
    </div>
  </div>
</template>
