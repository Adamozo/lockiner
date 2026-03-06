<script setup lang="ts">
import type { RecipeMatchResult } from '~/types/food'

const props = defineProps<{
  match: RecipeMatchResult
}>()

const emit = defineEmits<{
  view: [match: RecipeMatchResult]
}>()

const matchColor = computed(() => {
  if (props.match.match_percentage >= 80) return 'text-electric-green'
  if (props.match.match_percentage >= 50) return 'text-warning-orange'
  return 'text-danger-red'
})

const barColor = computed(() => {
  if (props.match.match_percentage >= 80) return 'bg-electric-green'
  if (props.match.match_percentage >= 50) return 'bg-warning-orange'
  return 'bg-danger-red'
})
</script>

<template>
  <div
    class="bg-card-black border border-border-gray rounded-xl p-4 flex flex-col gap-3 hover:border-electric-green/40 transition-colors cursor-pointer"
    @click="emit('view', match)"
  >
    <!-- Header -->
    <div class="flex items-start justify-between gap-2">
      <div class="flex-1 min-w-0">
        <h3 class="text-pure-white font-semibold truncate">{{ match.recipe.name }}</h3>
        <p v-if="match.recipe.description" class="text-pure-white/60 text-sm mt-0.5 line-clamp-1">
          {{ match.recipe.description }}
        </p>
      </div>
      <!-- Expiring badge -->
      <div
        v-if="match.expiring_soon_count > 0"
        class="flex-shrink-0 flex items-center gap-1 bg-warning-orange/10 border border-warning-orange/30 text-warning-orange text-xs px-2 py-0.5 rounded-full"
        title="Przepis zawiera produkty kończące ważność"
      >
        <UIcon name="i-heroicons-fire" class="w-3 h-3" />
        {{ match.expiring_soon_count }} wygasa
      </div>
    </div>

    <!-- Match bar -->
    <div>
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs text-pure-white/50">Dopasowanie</span>
        <span class="text-sm font-bold" :class="matchColor">
          {{ match.match_percentage }}%
        </span>
      </div>
      <div class="h-1.5 bg-background-black rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all"
          :class="barColor"
          :style="{ width: `${match.match_percentage}%` }"
        />
      </div>
    </div>

    <!-- Ingredients summary -->
    <div class="flex items-center gap-4 text-xs text-pure-white/50">
      <span class="flex items-center gap-1 text-electric-green">
        <UIcon name="i-heroicons-check-circle" class="w-3.5 h-3.5" />
        {{ match.available_ingredients.length }} masz
      </span>
      <span v-if="match.missing_ingredients.length" class="flex items-center gap-1 text-danger-red/80">
        <UIcon name="i-heroicons-x-circle" class="w-3.5 h-3.5" />
        {{ match.missing_ingredients.length }} brakuje
      </span>
    </div>

    <!-- Missing ingredients (top 3) -->
    <div v-if="match.missing_ingredients.length" class="text-xs text-pure-white/40">
      Brakuje: {{ match.missing_ingredients.slice(0, 3).map(i => i.name).join(', ') }}
      <span v-if="match.missing_ingredients.length > 3">
        i {{ match.missing_ingredients.length - 3 }} więcej
      </span>
    </div>
  </div>
</template>
