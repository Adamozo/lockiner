// Food module types

// ============================================================================
// Categories
// ============================================================================

export interface FoodCategory {
  id: number
  name: string
  icon: string
  color: string
  default_expiry_days: number | null
  storage_tips: string | null
}

// ============================================================================
// Products
// ============================================================================

export interface FoodProduct {
  id: number
  name: string
  name_normalized: string
  barcode: string | null
  barcode_type: string | null
  food_category_id: number | null
  food_category: FoodCategory | null
  calories: number | null
  protein: number | null
  carbohydrates: number | null
  fat: number | null
  fiber: number | null
  sugar: number | null
  sodium: number | null
  default_unit: string
  is_verified: boolean
  created_at: string
  updated_at: string | null
}

export interface FoodProductCreate {
  name: string
  barcode?: string
  barcode_type?: string
  food_category_id?: number
  calories?: number
  protein?: number
  carbohydrates?: number
  fat?: number
  fiber?: number
  sugar?: number
  sodium?: number
  default_unit?: string
}

export interface FoodProductUpdate {
  name?: string
  barcode?: string
  barcode_type?: string
  food_category_id?: number
  calories?: number
  protein?: number
  carbohydrates?: number
  fat?: number
  fiber?: number
  sugar?: number
  sodium?: number
  default_unit?: string
}

// ============================================================================
// Product Aliases
// ============================================================================

export interface FoodProductAlias {
  id: number
  product_id: number
  alias: string
  alias_normalized: string
  source: string
  created_at: string
}

export interface FoodProductAliasCreate {
  product_id: number
  alias: string
  source?: string
}

// ============================================================================
// Pending Imports
// ============================================================================

export type FoodPendingImportStatus = 'pending' | 'partially_accepted' | 'accepted' | 'rejected'
export type FoodPendingImportItemStatus = 'pending' | 'accepted' | 'rejected' | 'skipped'
export type FoodMatchMethod = 'exact_name' | 'alias' | 'barcode' | 'ai_suggestion'

export interface FoodPendingImportItem {
  id: number
  original_name: string
  quantity: number | null
  unit_price: number | null
  total_price: number | null
  matched_product_id: number | null
  matched_product: FoodProduct | null
  match_method: FoodMatchMethod | null
  match_confidence: number | null
  ai_suggested_name: string | null
  ai_suggested_category_id: number | null
  ai_suggested_expiry_days: number | null
  suggested_expiry_date: string | null
  status: FoodPendingImportItemStatus
  final_product_id: number | null
  final_expiry_date: string | null
  final_quantity: number | null
  final_unit: string | null
}

export interface FoodPendingImport {
  id: number
  receipt_id: number
  user_id: number
  household_id: number | null
  status: FoodPendingImportStatus
  created_at: string
  processed_at: string | null
  items: FoodPendingImportItem[]
}

export interface FoodPendingImportItemAccept {
  final_product_id?: number
  final_expiry_date?: string
  final_quantity?: number
  final_unit?: string
  new_product_name?: string
  new_product_category_id?: number
}

// ============================================================================
// Inventory
// ============================================================================

export type FoodInventoryStatus = 'available' | 'opened' | 'consumed' | 'expired' | 'thrown_away'
export type FoodInventoryLocation = 'fridge' | 'freezer' | 'pantry'

export interface FoodInventoryItem {
  id: number
  user_id: number
  household_id: number | null
  product_id: number
  product: FoodProduct
  quantity: number
  unit: string
  purchase_date: string | null
  expiry_date: string | null
  opened_date: string | null
  status: FoodInventoryStatus
  location: FoodInventoryLocation
  notes: string | null
  added_manually: boolean
  created_at: string
  updated_at: string | null
}

export interface FoodInventoryCreate {
  product_id: number
  quantity?: number
  unit?: string
  expiry_date?: string
  purchase_date?: string
  location?: FoodInventoryLocation
  notes?: string
}

export interface FoodInventoryUpdate {
  quantity?: number
  unit?: string
  expiry_date?: string
  opened_date?: string
  status?: FoodInventoryStatus
  location?: FoodInventoryLocation
  notes?: string
}

export interface FoodInventoryConsumeRequest {
  quantity?: number
  meal_type?: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  notes?: string
}

// ============================================================================
// Reminders
// ============================================================================

export type FoodReminderStatus = 'pending' | 'sent' | 'dismissed'

export interface FoodExpiryReminder {
  id: number
  user_id: number
  inventory_item_id: number
  inventory_item: FoodInventoryItem | null
  remind_at: string
  days_before_expiry: number
  status: FoodReminderStatus
  sent_at: string | null
  created_at: string
}

export interface FoodReminderSettings {
  id: number
  user_id: number
  enabled: boolean
  default_days_before: number
  dairy_days_before: number
  meat_days_before: number
  vegetables_days_before: number
  fruits_days_before: number
  bread_days_before: number
  frozen_days_before: number
  created_at: string
  updated_at: string | null
}

export interface FoodReminderSettingsUpdate {
  enabled?: boolean
  default_days_before?: number
  dairy_days_before?: number
  meat_days_before?: number
  vegetables_days_before?: number
  fruits_days_before?: number
  bread_days_before?: number
  frozen_days_before?: number
}

// ============================================================================
// Consumption Log
// ============================================================================

export type FoodMealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

export interface FoodConsumptionLog {
  id: number
  user_id: number
  product_id: number | null
  product: FoodProduct | null
  inventory_item_id: number | null
  quantity: number
  unit: string
  calories: number | null
  protein: number | null
  carbohydrates: number | null
  fat: number | null
  consumed_at: string
  meal_type: FoodMealType | null
  notes: string | null
  created_at: string
}

export interface FoodConsumptionLogCreate {
  product_id?: number
  inventory_item_id?: number
  quantity?: number
  unit?: string
  consumed_at: string
  meal_type?: FoodMealType
  notes?: string
}

// ============================================================================
// Filter Parameters
// ============================================================================

export interface FoodProductSearchParams {
  query?: string
  category_id?: number
  skip?: number
  limit?: number
}

export interface FoodInventoryFilterParams {
  status?: FoodInventoryStatus
  location?: FoodInventoryLocation
  category_id?: number
  expiring_within_days?: number
  skip?: number
  limit?: number
}
