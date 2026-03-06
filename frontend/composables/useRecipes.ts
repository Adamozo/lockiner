import type { FoodRecipe, FoodRecipeCreate, FoodRecipeUpdate, RecipeGenerateRequest, RecipeMatchResult } from '~/types/food'

export function useRecipes() {
  const api = useApi()
  const recipes = ref<FoodRecipe[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchRecipes = async () => {
    loading.value = true
    error.value = null
    try {
      recipes.value = await api<FoodRecipe[]>('/api/v1/food/recipes/')
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load recipes'
    } finally {
      loading.value = false
    }
  }

  const createRecipe = async (data: FoodRecipeCreate): Promise<FoodRecipe> => {
    const recipe = await api<FoodRecipe>('/api/v1/food/recipes/', { method: 'POST', body: data })
    recipes.value.unshift(recipe)
    return recipe
  }

  const updateRecipe = async (id: number, data: FoodRecipeUpdate): Promise<FoodRecipe> => {
    const updated = await api<FoodRecipe>(`/api/v1/food/recipes/${id}`, { method: 'PUT', body: data })
    const idx = recipes.value.findIndex(r => r.id === id)
    if (idx !== -1) recipes.value[idx] = updated
    return updated
  }

  const deleteRecipe = async (id: number): Promise<void> => {
    await api(`/api/v1/food/recipes/${id}`, { method: 'DELETE' })
    recipes.value = recipes.value.filter(r => r.id !== id)
  }

  const rateRecipe = async (id: number, rating: number): Promise<FoodRecipe> => {
    const updated = await api<FoodRecipe>(`/api/v1/food/recipes/${id}/rating`, {
      method: 'PATCH',
      body: { rating },
    })
    const idx = recipes.value.findIndex(r => r.id === id)
    if (idx !== -1) recipes.value[idx] = updated
    return updated
  }

  const generateRecipes = async (data: RecipeGenerateRequest): Promise<FoodRecipeCreate[]> => {
    return await api<FoodRecipeCreate[]>('/api/v1/food/recipes/generate', { method: 'POST', body: data })
  }

  const matchRecipes = async (): Promise<RecipeMatchResult[]> => {
    return await api<RecipeMatchResult[]>('/api/v1/food/recipes/match/inventory')
  }

  const saveGeneratedRecipe = async (data: FoodRecipeCreate): Promise<FoodRecipe> => {
    return await createRecipe({ ...data, source: 'saved_from_ai' })
  }

  return {
    recipes,
    loading,
    error,
    fetchRecipes,
    createRecipe,
    updateRecipe,
    deleteRecipe,
    rateRecipe,
    generateRecipes,
    matchRecipes,
    saveGeneratedRecipe,
  }
}
