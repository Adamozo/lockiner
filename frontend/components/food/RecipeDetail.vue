<script setup lang="ts">
import type { FoodRecipe } from '~/types/food'

const props = defineProps<{
  recipe: FoodRecipe
}>()

const emit = defineEmits<{
  rate: [id: number, rating: number]
  close: []
}>()

const stars = [1, 2, 3, 4, 5]
</script>

<template>
  <div class="space-y-5">
    <!-- Header -->
    <div>
      <div class="flex items-center gap-2 mb-1">
        <h2 class="text-xl font-bold text-pure-white">{{ recipe.name }}</h2>
        <UIcon
          v-if="recipe.source === 'saved_from_ai'"
          name="i-heroicons-sparkles"
          class="w-4 h-4 text-cyber-blue"
          title="Wygenerowany przez AI"
        />
      </div>
      <p v-if="recipe.description" class="text-pure-white/60 text-sm">{{ recipe.description }}</p>
    </div>

    <!-- Meta -->
    <div class="flex flex-wrap gap-4 text-sm text-pure-white/60">
      <span v-if="recipe.prep_time_minutes" class="flex items-center gap-1.5">
        <UIcon name="i-heroicons-clock" class="w-4 h-4 text-cyber-blue" />
        {{ recipe.prep_time_minutes }} minut
      </span>
      <span v-if="recipe.servings" class="flex items-center gap-1.5">
        <UIcon name="i-heroicons-user-group" class="w-4 h-4 text-cyber-blue" />
        {{ recipe.servings }} porcji
      </span>
    </div>

    <!-- Rating -->
    <div class="flex items-center gap-1.5">
      <span class="text-sm text-pure-white/60 mr-1">Ocena:</span>
      <button
        v-for="star in stars"
        :key="star"
        class="transition-colors"
        :class="star <= (recipe.rating ?? 0) ? 'text-warning-orange' : 'text-pure-white/20 hover:text-warning-orange/60'"
        @click="emit('rate', recipe.id, star)"
      >
        <UIcon name="i-heroicons-star-solid" class="w-5 h-5" />
      </button>
      <span v-if="recipe.rating" class="text-sm text-pure-white/40 ml-1">{{ recipe.rating }}/5</span>
    </div>

    <!-- Tags -->
    <div v-if="recipe.tags.length" class="flex flex-wrap gap-1.5">
      <span
        v-for="tag in recipe.tags"
        :key="tag"
        class="px-2.5 py-0.5 rounded-full bg-electric-green/10 border border-electric-green/20 text-electric-green text-xs"
      >
        {{ tag }}
      </span>
    </div>

    <!-- Ingredients -->
    <div v-if="recipe.ingredients.length">
      <h3 class="text-sm font-semibold text-pure-white/80 uppercase tracking-wide mb-2">
        Składniki
      </h3>
      <ul class="space-y-1.5">
        <li
          v-for="ing in recipe.ingredients"
          :key="ing.id"
          class="flex items-center gap-2 text-sm text-pure-white/80"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-electric-green flex-shrink-0" />
          <span>{{ ing.name }}</span>
          <span v-if="ing.quantity" class="text-pure-white/40">
            — {{ ing.quantity }} {{ ing.unit ?? '' }}
          </span>
        </li>
      </ul>
    </div>

    <!-- Instructions -->
    <div v-if="recipe.instructions.length">
      <h3 class="text-sm font-semibold text-pure-white/80 uppercase tracking-wide mb-2">
        Przygotowanie
      </h3>
      <ol class="space-y-3">
        <li
          v-for="(step, idx) in recipe.instructions"
          :key="idx"
          class="flex gap-3 text-sm text-pure-white/80"
        >
          <span class="flex-shrink-0 w-6 h-6 rounded-full bg-electric-green/20 text-electric-green flex items-center justify-center text-xs font-bold">
            {{ idx + 1 }}
          </span>
          <span class="pt-0.5">{{ step }}</span>
        </li>
      </ol>
    </div>
  </div>
</template>
