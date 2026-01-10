/**
 * Food module composable for categories and products
 * Handles category listing and product CRUD operations
 */

import type {
  FoodCategory,
  FoodProduct,
  FoodProductCreate,
  FoodProductUpdate,
  FoodProductAlias,
  FoodProductAliasCreate,
} from '~/types/food'
import { buildQueryParams } from './useApi'

export const useFood = () => {
  const api = useApi()
  const categories = ref<FoodCategory[]>([])
  const products = ref<FoodProduct[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // -------------------------------------------------------------------------
  // Categories
  // -------------------------------------------------------------------------

  /**
   * Fetch all food categories
   */
  const fetchCategories = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const data = await api<FoodCategory[]>('/api/v1/food/categories')
      categories.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch food categories'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Get category by ID
   */
  const getCategory = async (categoryId: number): Promise<FoodCategory> => {
    try {
      return await api<FoodCategory>(`/api/v1/food/categories/${categoryId}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch category'
      throw e
    }
  }

  /**
   * Get category by ID from local cache
   */
  const getCategoryById = (categoryId: number): FoodCategory | undefined => {
    return categories.value.find((c) => c.id === categoryId)
  }

  // -------------------------------------------------------------------------
  // Products
  // -------------------------------------------------------------------------

  /**
   * Fetch products with optional filters
   */
  const fetchProducts = async (params?: {
    search?: string
    category_id?: number
    skip?: number
    limit?: number
  }): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const queryString = buildQueryParams(params || {})
      const data = await api<FoodProduct[]>(`/api/v1/food/products${queryString}`)
      products.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch products'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Search products by name or barcode
   */
  const searchProducts = async (query: string, limit: number = 20): Promise<FoodProduct[]> => {
    try {
      const queryString = buildQueryParams({ query, limit })
      return await api<FoodProduct[]>(`/api/v1/food/products/search${queryString}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to search products'
      throw e
    }
  }

  /**
   * Get product by ID
   */
  const getProduct = async (productId: number): Promise<FoodProduct> => {
    try {
      return await api<FoodProduct>(`/api/v1/food/products/${productId}`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch product'
      throw e
    }
  }

  /**
   * Get product by barcode
   */
  const getProductByBarcode = async (barcode: string): Promise<FoodProduct | null> => {
    try {
      return await api<FoodProduct>(`/api/v1/food/products/barcode/${barcode}`)
    } catch (e) {
      // 404 means product not found, return null
      if ((e as any)?.response?.status === 404) {
        return null
      }
      error.value = e instanceof Error ? e.message : 'Failed to fetch product'
      throw e
    }
  }

  /**
   * Create a new product
   */
  const createProduct = async (data: FoodProductCreate): Promise<FoodProduct> => {
    loading.value = true
    error.value = null

    try {
      const product = await api<FoodProduct>('/api/v1/food/products', {
        method: 'POST',
        body: data,
      })
      products.value.push(product)
      return product
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create product'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Update a product
   */
  const updateProduct = async (productId: number, data: FoodProductUpdate): Promise<FoodProduct> => {
    loading.value = true
    error.value = null

    try {
      const product = await api<FoodProduct>(`/api/v1/food/products/${productId}`, {
        method: 'PUT',
        body: data,
      })
      const index = products.value.findIndex((p) => p.id === productId)
      if (index !== -1) {
        products.value[index] = product
      }
      return product
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update product'
      throw e
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // Product Aliases
  // -------------------------------------------------------------------------

  /**
   * Get aliases for a product
   */
  const getProductAliases = async (productId: number): Promise<FoodProductAlias[]> => {
    try {
      return await api<FoodProductAlias[]>(`/api/v1/food/products/${productId}/aliases`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch aliases'
      throw e
    }
  }

  /**
   * Create a product alias
   */
  const createProductAlias = async (data: FoodProductAliasCreate): Promise<FoodProductAlias> => {
    try {
      return await api<FoodProductAlias>('/api/v1/food/products/aliases', {
        method: 'POST',
        body: data,
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create alias'
      throw e
    }
  }

  // -------------------------------------------------------------------------
  // Computed
  // -------------------------------------------------------------------------

  /**
   * Get category names for dropdown
   */
  const categoryNames = computed(() => categories.value.map((c) => c.name))

  /**
   * Get category options for select
   */
  const categoryOptions = computed(() =>
    categories.value.map((c) => ({
      label: c.name,
      value: c.id,
      icon: c.icon,
      color: c.color,
    }))
  )

  return {
    // State
    categories,
    products,
    loading,
    error,
    // Categories
    fetchCategories,
    getCategory,
    getCategoryById,
    categoryNames,
    categoryOptions,
    // Products
    fetchProducts,
    searchProducts,
    getProduct,
    getProductByBarcode,
    createProduct,
    updateProduct,
    // Aliases
    getProductAliases,
    createProductAlias,
  }
}
