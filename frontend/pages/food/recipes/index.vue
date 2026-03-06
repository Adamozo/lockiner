<script setup lang="ts">
import type { FoodRecipe, FoodRecipeCreate, RecipeGenerateRequest, RecipeMatchResult } from '~/types/food'

definePageMeta({ layout: 'food' })

useSeoMeta({
  title: 'Przepisy - LockIner',
  description: 'Twoje przepisy kulinarne i sugestie AI',
})

const { currentHouseholdId } = useHouseholdContext()
const { recipes, loading: recipesLoading, fetchRecipes, deleteRecipe, rateRecipe, saveGeneratedRecipe, generateRecipes, matchRecipes } = useRecipes()
const { inventory, fetchInventory } = useFoodInventory()
const { lists: shoppingLists, loading: shoppingListsLoading, fetchLists, createList, addItem: addShoppingItem } = useShoppingLists()
const { confirm } = useConfirm()
const toast = useToast()

// Tabs
type Tab = 'my' | 'match' | 'generate'
const activeTab = ref<Tab>('my')

// Modal state
const selectedRecipe = ref<FoodRecipe | null>(null)
const isDetailOpen = ref(false)
const selectedMatchRecipe = ref<RecipeMatchResult | null>(null)
const isMatchDetailOpen = ref(false)

// Shopping list modal state
const isShoppingModalOpen = ref(false)
const selectedListId = ref<number | null>(null)
const newListName = ref('')
const addingToList = ref(false)

// Generate state
const generatedRecipes = ref<FoodRecipeCreate[]>([])
const generating = ref(false)
const savingId = ref<number | null>(null)

// Match state
const matchResults = ref<RecipeMatchResult[]>([])
const matchLoading = ref(false)

// Load on mount
onMounted(async () => {
  await Promise.all([
    fetchRecipes(),
    fetchInventory(currentHouseholdId.value),
  ])
})

watch(currentHouseholdId, () => fetchInventory(currentHouseholdId.value))

// Switch tab — lazy load match
watch(activeTab, async (tab) => {
  if (tab === 'match' && matchResults.value.length === 0) {
    await loadMatch()
  }
})

const loadMatch = async () => {
  matchLoading.value = true
  try {
    matchResults.value = await matchRecipes()
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się załadować dopasowań', color: 'red' })
  } finally {
    matchLoading.value = false
  }
}

// Handlers
const handleRate = async (id: number, rating: number) => {
  try {
    await rateRecipe(id, rating)
    if (selectedRecipe.value?.id === id) {
      selectedRecipe.value = recipes.value.find(r => r.id === id) ?? selectedRecipe.value
    }
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się zapisać oceny', color: 'red' })
  }
}

const handleDelete = async (id: number) => {
  if (!await confirm({ message: 'Usunąć ten przepis?', confirmText: 'Usuń' })) return
  try {
    await deleteRecipe(id)
    if (selectedRecipe.value?.id === id) isDetailOpen.value = false
    toast.add({ title: 'Usunięto', color: 'green' })
    // Refresh match if on that tab
    if (activeTab.value === 'match') await loadMatch()
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się usunąć przepisu', color: 'red' })
  }
}

const handleView = (recipe: FoodRecipe) => {
  selectedRecipe.value = recipe
  isDetailOpen.value = true
}

const handleViewMatch = (match: RecipeMatchResult) => {
  selectedMatchRecipe.value = match
  isMatchDetailOpen.value = true
}

const handleGenerate = async (request: RecipeGenerateRequest) => {
  generating.value = true
  generatedRecipes.value = []
  try {
    generatedRecipes.value = await generateRecipes(request)
    if (generatedRecipes.value.length === 0) {
      toast.add({ title: 'Brak wyników', description: 'AI nie zwróciło przepisów. Spróbuj ponownie.', color: 'yellow' })
    }
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Błąd generowania'
    toast.add({ title: 'Błąd', description: msg, color: 'red' })
  } finally {
    generating.value = false
  }
}

const handleSaveGenerated = async (recipe: FoodRecipeCreate, idx: number) => {
  savingId.value = idx
  try {
    await saveGeneratedRecipe(recipe)
    generatedRecipes.value.splice(idx, 1)
    toast.add({ title: 'Zapisano!', description: `"${recipe.name}" dodany do Twoich przepisów`, color: 'green' })
    if (activeTab.value === 'match') await loadMatch()
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się zapisać przepisu', color: 'red' })
  } finally {
    savingId.value = null
  }
}

const openShoppingModal = async () => {
  isMatchDetailOpen.value = false
  isShoppingModalOpen.value = true
  newListName.value = ''
  selectedListId.value = null
  try {
    await fetchLists('active')
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się załadować list zakupów', color: 'red' })
  }
}

const handleAddToShoppingList = async () => {
  if (!selectedMatchRecipe.value) return
  const missing = selectedMatchRecipe.value.missing_ingredients
  if (!missing.length) return

  addingToList.value = true
  try {
    let listId = selectedListId.value

    if (!listId) {
      const name = newListName.value.trim() || `Zakupy do: ${selectedMatchRecipe.value.recipe.name}`
      const newList = await createList({ name, visibility: 'private' })
      listId = newList.id
    }

    await Promise.all(
      missing.map((ing, idx) =>
        addShoppingItem(listId!, {
          name: ing.name,
          quantity: ing.quantity ?? undefined,
          unit: ing.unit ?? undefined,
          position: idx,
        })
      )
    )

    toast.add({ title: 'Dodano!', description: `${missing.length} składników dodanych do listy zakupów`, color: 'green' })
    isShoppingModalOpen.value = false
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się dodać składników', color: 'red' })
  } finally {
    addingToList.value = false
  }
}

const tabs: { key: Tab; label: string; icon: string }[] = [
  { key: 'my', label: 'Moje przepisy', icon: 'i-heroicons-book-open' },
  { key: 'match', label: 'Co mogę zrobić?', icon: 'i-heroicons-light-bulb' },
  { key: 'generate', label: 'Generuj z AI', icon: 'i-heroicons-sparkles' },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-pure-white">Przepisy</h1>
      <p class="text-pure-white/60 text-sm mt-1">
        Twoja baza przepisów, dopasowania do spiżarni i sugestie AI
      </p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-card-black border border-border-gray rounded-xl p-1">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all"
        :class="activeTab === tab.key
          ? 'bg-electric-green/10 text-electric-green border border-electric-green/30'
          : 'text-pure-white/50 hover:text-pure-white hover:bg-pure-white/5'"
        @click="activeTab = tab.key"
      >
        <UIcon :name="tab.icon" class="w-4 h-4" />
        <span class="hidden sm:inline">{{ tab.label }}</span>
        <span v-if="tab.key === 'my' && recipes.length" class="text-xs bg-electric-green/20 text-electric-green px-1.5 py-0.5 rounded-full">
          {{ recipes.length }}
        </span>
      </button>
    </div>

    <!-- ================================ -->
    <!-- Tab: Moje przepisy -->
    <!-- ================================ -->
    <div v-if="activeTab === 'my'">
      <div v-if="recipesLoading" class="flex justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-pure-white/40 animate-spin" />
      </div>

      <div v-else-if="recipes.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <FoodRecipeCard
          v-for="recipe in recipes"
          :key="recipe.id"
          :recipe="recipe"
          @view="handleView"
          @delete="handleDelete"
          @rate="handleRate"
        />
      </div>

      <div v-else class="bg-card-black border border-border-gray rounded-xl p-12 text-center">
        <div class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4">
          <UIcon name="i-heroicons-book-open" class="w-8 h-8 text-pure-white/30" />
        </div>
        <h3 class="text-pure-white font-medium mb-2">Brak zapisanych przepisów</h3>
        <p class="text-pure-white/50 text-sm mb-4">
          Wygeneruj przepisy z AI lub dodaj ręcznie
        </p>
        <BaseButton variant="secondary" size="sm" @click="activeTab = 'generate'">
          <UIcon name="i-heroicons-sparkles" class="w-4 h-4 mr-1" />
          Generuj przepisy
        </BaseButton>
      </div>
    </div>

    <!-- ================================ -->
    <!-- Tab: Co mogę zrobić? -->
    <!-- ================================ -->
    <div v-if="activeTab === 'match'">
      <div v-if="matchLoading" class="flex justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-pure-white/40 animate-spin" />
      </div>

      <div v-else-if="matchResults.length" class="space-y-4">
        <!-- Expiring soon highlight -->
        <div
          v-if="matchResults.some(r => r.expiring_soon_count > 0)"
          class="bg-warning-orange/10 border border-warning-orange/30 rounded-xl p-3 flex items-center gap-3"
        >
          <UIcon name="i-heroicons-fire" class="w-5 h-5 text-warning-orange flex-shrink-0" />
          <p class="text-sm text-warning-orange/90">
            Zaznaczone przepisy zawierają produkty kończące ważność — zrób je jak najszybciej!
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <FoodRecipeMatchCard
            v-for="match in matchResults"
            :key="match.recipe.id"
            :match="match"
            @view="handleViewMatch"
          />
        </div>
      </div>

      <div v-else-if="recipes.length === 0" class="bg-card-black border border-border-gray rounded-xl p-12 text-center">
        <UIcon name="i-heroicons-light-bulb" class="w-12 h-12 text-pure-white/30 mx-auto mb-4" />
        <h3 class="text-pure-white font-medium mb-2">Brak przepisów do dopasowania</h3>
        <p class="text-pure-white/50 text-sm mb-4">Najpierw dodaj przepisy do swojej bazy</p>
        <BaseButton variant="secondary" size="sm" @click="activeTab = 'generate'">Generuj z AI</BaseButton>
      </div>

      <div v-else class="bg-card-black border border-border-gray rounded-xl p-12 text-center">
        <UIcon name="i-heroicons-light-bulb" class="w-12 h-12 text-pure-white/30 mx-auto mb-4" />
        <h3 class="text-pure-white font-medium mb-2">Brak dopasowań</h3>
        <p class="text-pure-white/50 text-sm">Uzupełnij inwentarz lub dodaj więcej przepisów</p>
      </div>
    </div>

    <!-- ================================ -->
    <!-- Tab: Generuj z AI -->
    <!-- ================================ -->
    <div v-if="activeTab === 'generate'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Form -->
      <div class="bg-card-black border border-border-gray rounded-xl p-5">
        <h2 class="text-pure-white font-semibold mb-4 flex items-center gap-2">
          <UIcon name="i-heroicons-cpu-chip" class="w-5 h-5 text-cyber-blue" />
          Generuj przepisy
        </h2>
        <FoodRecipeGenerateForm
          :inventory="inventory"
          :loading="generating"
          @generate="handleGenerate"
        />
      </div>

      <!-- Results -->
      <div class="flex flex-col gap-4">
        <div v-if="generating" class="bg-card-black border border-border-gray rounded-xl p-8 text-center">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-cyber-blue animate-spin mx-auto mb-3" />
          <p class="text-pure-white/60 text-sm">AI generuje przepisy...</p>
        </div>

        <template v-else-if="generatedRecipes.length">
          <div class="flex items-center justify-between">
            <h3 class="text-pure-white font-medium">Propozycje AI ({{ generatedRecipes.length }})</h3>
            <p class="text-xs text-pure-white/40">Kliknij "Zapisz" aby dodać do bazy</p>
          </div>

          <div
            v-for="(recipe, idx) in generatedRecipes"
            :key="idx"
            class="bg-card-black border border-border-gray rounded-xl p-4 space-y-3"
          >
            <!-- Recipe header -->
            <div class="flex items-start justify-between gap-2">
              <div>
                <h4 class="text-pure-white font-semibold">{{ recipe.name }}</h4>
                <p v-if="recipe.description" class="text-pure-white/60 text-sm mt-0.5">{{ recipe.description }}</p>
              </div>
              <BaseButton
                variant="primary"
                size="sm"
                :disabled="savingId === idx"
                @click="handleSaveGenerated(recipe, idx)"
              >
                <UIcon name="i-heroicons-bookmark" class="w-3.5 h-3.5 mr-1" />
                {{ savingId === idx ? 'Zapisuję...' : 'Zapisz' }}
              </BaseButton>
            </div>

            <!-- Meta -->
            <div class="flex gap-3 text-xs text-pure-white/40">
              <span v-if="recipe.prep_time_minutes">
                <UIcon name="i-heroicons-clock" class="w-3 h-3 inline mr-0.5" />
                {{ recipe.prep_time_minutes }} min
              </span>
              <span v-if="recipe.servings">
                <UIcon name="i-heroicons-user-group" class="w-3 h-3 inline mr-0.5" />
                {{ recipe.servings }} porcji
              </span>
              <span>
                <UIcon name="i-heroicons-list-bullet" class="w-3 h-3 inline mr-0.5" />
                {{ recipe.ingredients.length }} składników
              </span>
            </div>

            <!-- Tags -->
            <div v-if="recipe.tags?.length" class="flex flex-wrap gap-1">
              <span
                v-for="tag in recipe.tags"
                :key="tag"
                class="px-2 py-0.5 bg-electric-green/10 text-electric-green text-xs rounded-full"
              >{{ tag }}</span>
            </div>

            <!-- Ingredients preview -->
            <details class="text-sm text-pure-white/70">
              <summary class="cursor-pointer text-cyber-blue/80 text-xs hover:text-cyber-blue select-none">
                Pokaż składniki i kroki
              </summary>
              <div class="mt-2 space-y-2 pl-2">
                <div>
                  <p class="text-pure-white/50 text-xs mb-1">Składniki:</p>
                  <ul class="space-y-0.5">
                    <li v-for="ing in recipe.ingredients" :key="ing.name" class="text-xs flex gap-1">
                      <span class="text-electric-green">•</span>
                      {{ ing.name }}
                      <span v-if="ing.quantity" class="text-pure-white/40">{{ ing.quantity }} {{ ing.unit }}</span>
                    </li>
                  </ul>
                </div>
                <div v-if="recipe.instructions?.length">
                  <p class="text-pure-white/50 text-xs mb-1">Kroki:</p>
                  <ol class="space-y-0.5">
                    <li v-for="(step, i) in recipe.instructions" :key="i" class="text-xs">
                      <span class="text-cyber-blue">{{ i + 1 }}.</span> {{ step }}
                    </li>
                  </ol>
                </div>
              </div>
            </details>
          </div>
        </template>

        <div v-else class="bg-card-black border border-dashed border-border-gray rounded-xl h-full min-h-64 flex flex-col items-center justify-center gap-3">
          <UIcon name="i-heroicons-sparkles" class="w-10 h-10 text-pure-white/20" />
          <p class="text-pure-white/40 text-sm">Tutaj pojawią się wygenerowane przepisy</p>
        </div>
      </div>
    </div>

    <!-- Recipe detail modal -->
    <BaseModal v-model="isDetailOpen" :title="selectedRecipe?.name ?? 'Przepis'" max-width="2xl">
      <FoodRecipeDetail
        v-if="selectedRecipe"
        :recipe="selectedRecipe"
        @rate="handleRate"
        @close="isDetailOpen = false"
      />
    </BaseModal>

    <!-- Shopping list picker overlay -->
    <Teleport to="body">
      <div
        v-if="isShoppingModalOpen && selectedMatchRecipe"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="isShoppingModalOpen = false"
      >
        <div class="absolute inset-0 bg-black/60" @click="isShoppingModalOpen = false" />
        <div class="relative bg-card-black border border-border-gray rounded-2xl p-5 w-full max-w-sm shadow-2xl space-y-4">
          <!-- Header -->
          <div class="flex items-center justify-between">
            <h3 class="text-pure-white font-semibold flex items-center gap-2">
              <UIcon name="i-heroicons-shopping-cart" class="w-5 h-5 text-electric-green" />
              Dodaj do listy zakupów
            </h3>
            <button class="text-pure-white/40 hover:text-pure-white transition-colors" @click="isShoppingModalOpen = false">
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
            </button>
          </div>

          <p class="text-sm text-pure-white/60">
            Dodaję <span class="text-danger-red font-medium">{{ selectedMatchRecipe.missing_ingredients.length }} brakujących składników</span> do listy zakupów.
          </p>

          <!-- Existing lists -->
          <div>
            <label class="text-xs text-pure-white/50 uppercase tracking-wide mb-2 block">Wybierz istniejącą listę</label>
            <div v-if="shoppingListsLoading" class="text-center py-3">
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 text-pure-white/30 animate-spin" />
            </div>
            <div v-else-if="shoppingLists.length" class="space-y-1.5 max-h-40 overflow-y-auto pr-1">
              <button
                v-for="list in shoppingLists"
                :key="list.id"
                class="w-full text-left px-3 py-2 rounded-lg border text-sm transition-all"
                :class="selectedListId === list.id
                  ? 'border-electric-green bg-electric-green/10 text-electric-green'
                  : 'border-border-gray text-pure-white/70 hover:border-electric-green/30'"
                @click="selectedListId = list.id; newListName = ''"
              >
                {{ list.name }}
                <span class="text-pure-white/30 text-xs ml-1">({{ list.total_items }})</span>
              </button>
            </div>
            <p v-else class="text-pure-white/40 text-sm text-center py-2">Brak aktywnych list</p>
          </div>

          <!-- Or create new -->
          <div>
            <label class="text-xs text-pure-white/50 uppercase tracking-wide mb-2 block">lub utwórz nową listę</label>
            <input
              v-model="newListName"
              type="text"
              :placeholder="`Zakupy do: ${selectedMatchRecipe.recipe.name}`"
              class="w-full rounded-lg border border-border-gray bg-background-black text-pure-white placeholder-pure-white/30 px-3 py-2 text-sm focus:border-electric-green focus:outline-none focus:ring-1 focus:ring-electric-green/30"
              @focus="selectedListId = null"
            />
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-1">
            <button
              class="flex-1 px-3 py-2 rounded-lg border border-border-gray text-pure-white/60 text-sm hover:border-pure-white/30 transition-colors"
              @click="isShoppingModalOpen = false"
            >
              Anuluj
            </button>
            <button
              class="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-1.5"
              :class="addingToList || (!selectedListId && !newListName.trim())
                ? 'bg-electric-green/20 text-electric-green/40 cursor-not-allowed'
                : 'bg-electric-green/20 border border-electric-green text-electric-green hover:bg-electric-green/30'"
              :disabled="addingToList || (!selectedListId && !newListName.trim())"
              @click="handleAddToShoppingList"
            >
              <UIcon name="i-heroicons-arrow-path" v-if="addingToList" class="w-4 h-4 animate-spin" />
              <UIcon name="i-heroicons-shopping-cart" v-else class="w-4 h-4" />
              {{ addingToList ? 'Dodaję...' : 'Dodaj składniki' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Match detail modal -->
    <BaseModal v-model="isMatchDetailOpen" :title="selectedMatchRecipe?.recipe.name ?? 'Przepis'" max-width="2xl">
      <div v-if="selectedMatchRecipe" class="space-y-4">
        <!-- Match summary -->
        <div class="flex flex-wrap gap-3 text-sm p-3 bg-background-black rounded-lg">
          <span class="text-electric-green font-semibold">
            {{ selectedMatchRecipe.match_percentage }}% dopasowania
          </span>
          <span class="text-pure-white/50">·</span>
          <span class="text-electric-green/80">
            {{ selectedMatchRecipe.available_ingredients.length }} dostępnych
          </span>
          <span v-if="selectedMatchRecipe.missing_ingredients.length" class="text-danger-red/80">
            · {{ selectedMatchRecipe.missing_ingredients.length }} brakuje
          </span>
          <span v-if="selectedMatchRecipe.expiring_soon_count" class="text-warning-orange">
            · {{ selectedMatchRecipe.expiring_soon_count }} wygasa wkrótce!
          </span>
        </div>

        <!-- Missing ingredients -->
        <div v-if="selectedMatchRecipe.missing_ingredients.length" class="bg-danger-red/5 border border-danger-red/20 rounded-lg p-3">
          <div class="flex items-center justify-between mb-1.5">
            <p class="text-xs text-danger-red font-medium">Brakujące składniki:</p>
            <button
              class="flex items-center gap-1 text-xs text-cyber-blue hover:text-cyber-blue/80 transition-colors"
              @click="openShoppingModal"
            >
              <UIcon name="i-heroicons-shopping-cart" class="w-3.5 h-3.5" />
              Dodaj do listy
            </button>
          </div>
          <ul class="space-y-0.5">
            <li
              v-for="ing in selectedMatchRecipe.missing_ingredients"
              :key="ing.name"
              class="text-sm text-pure-white/70 flex gap-1"
            >
              <span class="text-danger-red/60">✗</span>
              {{ ing.name }}
              <span v-if="ing.quantity" class="text-pure-white/40">{{ ing.quantity }} {{ ing.unit }}</span>
            </li>
          </ul>
        </div>

        <FoodRecipeDetail
          :recipe="selectedMatchRecipe.recipe"
          @rate="handleRate"
          @close="isMatchDetailOpen = false"
        />
      </div>
    </BaseModal>
  </div>
</template>
