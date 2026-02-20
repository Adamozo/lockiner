// Shopping Lists module types

export type ShoppingListStatus = 'active' | 'completed' | 'archived'
export type ShoppingListVisibility = 'private' | 'household'
export type ShoppingItemStatus = 'pending' | 'in_cart' | 'purchased'

export interface ShoppingListItem {
  id: number
  list_id: number
  added_by: number
  food_product_id: number | null
  name: string
  quantity: number | null
  unit: string | null
  category: string | null
  status: ShoppingItemStatus
  is_recurring: boolean
  notes: string | null
  position: number
  created_at: string
  updated_at: string | null
}

export interface ShoppingListItemCreate {
  name: string
  quantity?: number | null
  unit?: string | null
  category?: string | null
  notes?: string | null
  position?: number
  food_product_id?: number | null
  is_recurring?: boolean
}

export interface ShoppingListItemUpdate {
  name?: string
  quantity?: number | null
  unit?: string | null
  category?: string | null
  notes?: string | null
  position?: number
  is_recurring?: boolean
}

export interface ShoppingList {
  id: number
  owner_id: number
  household_id: number | null
  visibility: ShoppingListVisibility
  name: string
  store_name: string | null
  planned_date: string | null
  status: ShoppingListStatus
  notes: string | null
  items: ShoppingListItem[]
  created_at: string
  updated_at: string | null
}

export interface ShoppingListSummary {
  id: number
  owner_id: number
  household_id: number | null
  visibility: ShoppingListVisibility
  name: string
  store_name: string | null
  planned_date: string | null
  status: ShoppingListStatus
  total_items: number
  pending_items: number
  in_cart_items: number
  purchased_items: number
  created_at: string
}

export interface ShoppingListCreate {
  name: string
  store_name?: string | null
  planned_date?: string | null
  visibility?: ShoppingListVisibility
  household_id?: number | null
  notes?: string | null
}

export interface ShoppingListUpdate {
  name?: string
  store_name?: string | null
  planned_date?: string | null
  visibility?: ShoppingListVisibility
  household_id?: number | null
  notes?: string | null
  status?: ShoppingListStatus
}
