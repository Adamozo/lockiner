/**
 * Categories Pinia Store
 * Global state management for categories with caching
 */

import { defineStore } from 'pinia'
import type { Category, CategoryCreate } from '~/types/api'

export const useCategoriesStore = defineStore('categories', () => {
  // State
  const categories = ref<Category[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetched = ref<Date | null>(null)

  // API client
  const api = useApi()

  // Cache duration (5 minutes)
  const CACHE_DURATION = 5 * 60 * 1000

  // Getters
  const categoryNames = computed(() => {
    return categories.value.map(c => c.name)
  })

  const getCategoryByName = computed(() => {
    return (name: string) => {
      return categories.value.find(c => c.name === name)
    }
  })

  const getCategoryById = computed(() => {
    return (id: number) => {
      return categories.value.find(c => c.id === id)
    }
  })

  const isCacheValid = computed(() => {
    if (!lastFetched.value) return false
    const now = new Date()
    return now.getTime() - lastFetched.value.getTime() < CACHE_DURATION
  })

  // Actions
  const fetchCategories = async (force = false): Promise<void> => {
    // Use cache if valid and not forced
    if (!force && isCacheValid.value && categories.value.length > 0) {
      return
    }

    loading.value = true
    error.value = null

    try {
      const data = await api<Category[]>('/api/v1/categories/')
      categories.value = data
      lastFetched.value = new Date()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch categories'
      throw e
    } finally {
      loading.value = false
    }
  }

  const createCategory = async (category: CategoryCreate): Promise<Category> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<Category>('/api/v1/categories/', {
        method: 'POST',
        body: category,
      })

      categories.value.push(data)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create category'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateCategory = async (
    id: number,
    updates: Partial<CategoryCreate>
  ): Promise<Category> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<Category>(`/api/v1/categories/${id}`, {
        method: 'PUT',
        body: updates,
      })

      const index = categories.value.findIndex(c => c.id === id)
      if (index !== -1) {
        categories.value[index] = data
      }

      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update category'
      throw e
    } finally {
      loading.value = false
    }
  }

  const deleteCategory = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api(`/api/v1/categories/${id}`, {
        method: 'DELETE',
      })

      categories.value = categories.value.filter(c => c.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete category'
      throw e
    } finally {
      loading.value = false
    }
  }

  const invalidateCache = () => {
    lastFetched.value = null
  }

  return {
    // State
    categories,
    loading,
    error,

    // Getters
    categoryNames,
    getCategoryByName,
    getCategoryById,
    isCacheValid,

    // Actions
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    invalidateCache,
  }
})
