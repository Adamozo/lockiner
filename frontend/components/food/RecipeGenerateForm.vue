<script setup lang="ts">
import type { FoodInventoryItem } from '~/types/food'
import type { FoodRecipeCreate, RecipeGenerateRequest } from '~/types/food'

const props = defineProps<{
  inventory: FoodInventoryItem[]
  loading: boolean
}>()

const emit = defineEmits<{
  generate: [request: RecipeGenerateRequest]
}>()

const useAll = ref(true)
const selectedProductIds = ref<number[]>([])
const preferences = ref('')
const maxRecipes = ref(3)

const availableProducts = computed(() =>
  props.inventory.filter(i => i.status === 'available' || i.status === 'opened')
)

const toggleProduct = (productId: number) => {
  const idx = selectedProductIds.value.indexOf(productId)
  if (idx === -1) selectedProductIds.value.push(productId)
  else selectedProductIds.value.splice(idx, 1)
}

const handleGenerate = () => {
  emit('generate', {
    product_ids: useAll.value ? null : selectedProductIds.value,
    preferences: preferences.value || null,
    max_recipes: maxRecipes.value,
  })
}
</script>

<template>
  <div class="space-y-5">
    <!-- Product selection -->
    <div>
      <label class="text-sm font-medium text-pure-white mb-2 block">Produkty</label>
      <div class="flex gap-2 mb-3">
        <button
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
          :class="useAll ? 'bg-electric-green/20 border border-electric-green text-electric-green' : 'border border-border-gray text-pure-white/60 hover:border-electric-green/40'"
          @click="useAll = true"
        >
          Cały inwentarz ({{ availableProducts.length }})
        </button>
        <button
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
          :class="!useAll ? 'bg-cyber-blue/20 border border-cyber-blue text-cyber-blue' : 'border border-border-gray text-pure-white/60 hover:border-cyber-blue/40'"
          @click="useAll = false"
        >
          Wybierz ręcznie
        </button>
      </div>

      <!-- Manual selection -->
      <div v-if="!useAll" class="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-48 overflow-y-auto pr-1">
        <button
          v-for="item in availableProducts"
          :key="item.id"
          class="px-2 py-1.5 rounded-lg text-xs text-left transition-all border"
          :class="selectedProductIds.includes(item.product_id)
            ? 'border-electric-green bg-electric-green/10 text-electric-green'
            : 'border-border-gray text-pure-white/60 hover:border-electric-green/30'"
          @click="toggleProduct(item.product_id)"
        >
          {{ item.product.name }}
        </button>
        <p v-if="availableProducts.length === 0" class="text-pure-white/40 text-sm col-span-full text-center py-4">
          Brak produktów w inwentarzu
        </p>
      </div>
    </div>

    <!-- Preferences -->
    <div>
      <label class="text-sm font-medium text-pure-white mb-1.5 block">
        Preferencje <span class="text-pure-white/40 font-normal">(opcjonalne)</span>
      </label>
      <input
        v-model="preferences"
        type="text"
        placeholder="np. wegetariańskie, szybkie, bez glutenu..."
        class="w-full rounded-lg border border-border-gray bg-background-black text-pure-white placeholder-pure-white/30 px-3 py-2 text-sm focus:border-electric-green focus:outline-none focus:ring-1 focus:ring-electric-green/30"
      />
    </div>

    <!-- Max recipes -->
    <div>
      <label class="text-sm font-medium text-pure-white mb-1.5 block">
        Liczba przepisów: <span class="text-electric-green">{{ maxRecipes }}</span>
      </label>
      <input
        v-model.number="maxRecipes"
        type="range"
        min="1"
        max="5"
        class="w-full accent-electric-green"
      />
      <div class="flex justify-between text-xs text-pure-white/30 mt-0.5">
        <span>1</span><span>5</span>
      </div>
    </div>

    <!-- Generate button -->
    <BaseButton
      variant="primary"
      class="w-full"
      icon="i-heroicons-sparkles"
      :disabled="loading || (!useAll && selectedProductIds.length === 0)"
      @click="handleGenerate"
    >
      {{ loading ? 'Generuję...' : 'Generuj przepisy' }}
    </BaseButton>
  </div>
</template>
