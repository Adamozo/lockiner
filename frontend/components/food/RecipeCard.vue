<script setup lang="ts">
import type { FoodRecipe } from '~/types/food'

const props = defineProps<{
  recipe: FoodRecipe
}>()

const emit = defineEmits<{
  view: [recipe: FoodRecipe]
  delete: [id: number]
  rate: [id: number, rating: number]
}>()

const stars = [1, 2, 3, 4, 5]
</script>

<template>
  <div
    class="bg-card-black border border-border-gray rounded-xl p-4 flex flex-col gap-3 hover:border-electric-green/40 transition-colors cursor-pointer"
    @click="emit('view', recipe)"
  >
    <!-- Header -->
    <div class="flex items-start justify-between gap-2">
      <div class="flex-1 min-w-0">
        <h3 class="text-pure-white font-semibold truncate">{{ recipe.name }}</h3>
        <p v-if="recipe.description" class="text-pure-white/60 text-sm mt-0.5 line-clamp-2">
          {{ recipe.description }}
        </p>
      </div>
      <UIcon
        v-if="recipe.source === 'saved_from_ai'"
        name="i-heroicons-sparkles"
        class="w-4 h-4 text-cyber-blue flex-shrink-0 mt-0.5"
        title="AI generated"
      />
    </div>

    <!-- Meta -->
    <div class="flex items-center gap-3 text-xs text-pure-white/50">
      <span v-if="recipe.prep_time_minutes" class="flex items-center gap-1">
        <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
        {{ recipe.prep_time_minutes }} min
      </span>
      <span v-if="recipe.servings" class="flex items-center gap-1">
        <UIcon name="i-heroicons-user-group" class="w-3.5 h-3.5" />
        {{ recipe.servings }} porcji
      </span>
      <span class="flex items-center gap-1">
        <UIcon name="i-heroicons-list-bullet" class="w-3.5 h-3.5" />
        {{ recipe.ingredients.length }} składników
      </span>
    </div>

    <!-- Tags -->
    <div v-if="recipe.tags.length" class="flex flex-wrap gap-1">
      <span
        v-for="tag in recipe.tags"
        :key="tag"
        class="px-2 py-0.5 rounded-full bg-electric-green/10 text-electric-green text-xs"
      >
        {{ tag }}
      </span>
    </div>

    <!-- Rating + Actions -->
    <div class="flex items-center justify-between pt-1 border-t border-border-gray/50">
      <!-- Stars -->
      <div class="flex items-center gap-0.5" @click.stop>
        <button
          v-for="star in stars"
          :key="star"
          class="transition-colors"
          :class="star <= (recipe.rating ?? 0) ? 'text-warning-orange' : 'text-pure-white/20 hover:text-warning-orange/60'"
          @click="emit('rate', recipe.id, star)"
        >
          <UIcon name="i-heroicons-star-solid" class="w-4 h-4" />
        </button>
        <span v-if="recipe.rating" class="text-xs text-pure-white/40 ml-1">{{ recipe.rating }}/5</span>
      </div>

      <!-- Delete -->
      <button
        class="text-pure-white/30 hover:text-danger-red transition-colors p-1"
        @click.stop="emit('delete', recipe.id)"
      >
        <UIcon name="i-heroicons-trash" class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
