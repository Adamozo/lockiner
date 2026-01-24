<script setup lang="ts">
defineProps<{
  title: string;
  description: string;
}>();
</script>

<template>
  <header>
    <h1 class="text-3xl font-bold text-pure-white">{{ title }}</h1>
    <p class="mt-2 text-pure-white/60">
      {{ description }}
    </p>
  </header>
</template>
