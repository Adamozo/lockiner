/**
 * Composable for food nutrition tracking (calorie logging, daily summary, goals).
 */

export interface OFFProductInfo {
  code: string
  name?: string
  brands?: string
  quantity?: string
  nutriscore_grade?: string
  calories_100g?: number
  protein_100g?: number
  carbohydrates_100g?: number
  fat_100g?: number
  image_url?: string
}

export interface InventoryItemForProduct {
  id: number
  location: string
  quantity: number
  unit: string
  expiry_date?: string
  status: string
}

export interface LocalProduct {
  id: number
  name: string
  barcode?: string
  calories?: number
  protein?: number
  carbohydrates?: number
  fat?: number
  default_unit: string
}

export interface ProductSearchResult {
  source: 'local' | 'off'
  product?: LocalProduct
  off_product?: OFFProductInfo
  inventory_items: InventoryItemForProduct[]
  in_stock: boolean
}

export interface MealLogEntry {
  id: number
  product_name: string
  quantity: number
  unit: string
  calories?: number
  consumed_at: string
}

export interface MealSummary {
  meal_type: string
  logs: MealLogEntry[]
  total_calories: number
}

export interface DailyGoal {
  calories?: number
  protein?: number
  carbohydrates?: number
  fat?: number
}

export interface DailyNutritionSummary {
  date: string
  total: { calories: number; protein: number; carbohydrates: number; fat: number }
  by_meal: MealSummary[]
  goal?: DailyGoal
  goal_progress_pct: number
}

export interface WeeklyDay {
  date: string
  calories: number
  goal_calories: number
}

export interface DirectConsumptionRequest {
  product_id?: number
  off_product_code?: string
  product_name?: string
  quantity: number
  unit: string
  meal_type?: string
  calories_override?: number
  notes?: string
}

export function useFoodNutrition() {
  const api = useApi()

  async function scanBarcode(ean: string): Promise<ProductSearchResult | null> {
    try {
      return await api<ProductSearchResult>(`/api/v1/food/products/scan/${ean}`)
    } catch {
      return null
    }
  }

  async function searchGlobal(query: string, lang?: string): Promise<ProductSearchResult[]> {
    const params = new URLSearchParams({ q: query })
    if (lang) params.set('lang', lang)
    return await api<ProductSearchResult[]>(`/api/v1/food/products/search-global?${params}`)
  }

  async function logDirect(data: DirectConsumptionRequest) {
    return await api('/api/v1/food/consumption/direct', {
      method: 'POST',
      body: data,
    })
  }

  async function consumeInventoryItem(itemId: number, data: {
    quantity?: number
    meal_type?: string
    notes?: string
  }) {
    return await api(`/api/v1/food/inventory/${itemId}/consume`, {
      method: 'POST',
      body: data,
    })
  }

  async function deleteLog(logId: number): Promise<void> {
    await api(`/api/v1/food/consumption/${logId}`, { method: 'DELETE' })
  }

  async function fetchDailySummary(date?: string): Promise<DailyNutritionSummary> {
    const params = date ? `?date=${date}` : ''
    return await api<DailyNutritionSummary>(`/api/v1/food/consumption/daily-summary${params}`)
  }

  async function fetchWeeklySummary(): Promise<WeeklyDay[]> {
    return await api<WeeklyDay[]>('/api/v1/food/consumption/weekly-summary')
  }

  async function fetchGoal(): Promise<DailyGoal & { id: number; user_id: number }> {
    return await api('/api/v1/food/goals')
  }

  async function updateGoal(data: DailyGoal) {
    return await api('/api/v1/food/goals', {
      method: 'PUT',
      body: data,
    })
  }

  return {
    scanBarcode,
    searchGlobal,
    logDirect,
    consumeInventoryItem,
    deleteLog,
    fetchDailySummary,
    fetchWeeklySummary,
    fetchGoal,
    updateGoal,
  }
}
