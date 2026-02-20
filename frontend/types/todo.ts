// Todo List module types

export interface TodoItem {
  id: number
  list_id: number
  user_id: number
  title: string
  description: string | null
  completed: boolean
  completed_at: string | null
  estimated_minutes: number | null
  priority: 'low' | 'medium' | 'high'
  position: number
  postponed_count: number
  original_list_id: number | null
  item_reminder_enabled: boolean
  item_reminder_time: string | null // "HH:MM"
  created_at: string
  updated_at: string | null
}

export interface TodoItemCreate {
  title: string
  description?: string | null
  estimated_minutes?: number | null
  priority?: 'low' | 'medium' | 'high'
  position?: number
  item_reminder_enabled?: boolean
  item_reminder_time?: string | null
}

export interface TodoItemUpdate {
  title?: string
  description?: string | null
  estimated_minutes?: number | null
  priority?: 'low' | 'medium' | 'high'
  position?: number
  item_reminder_enabled?: boolean
  item_reminder_time?: string | null
}

export interface TodoList {
  id: number
  user_id: number
  title: string
  date: string // "YYYY-MM-DD"
  created_in_advance_days: number
  items: TodoItem[]
  created_at: string
  updated_at: string | null
}

export interface TodoListSummary {
  id: number
  user_id: number
  title: string
  date: string
  created_in_advance_days: number
  total_items: number
  completed_items: number
  estimated_minutes_total: number | null
  created_at: string
}

export interface TodoListCreate {
  title: string
  date: string // "YYYY-MM-DD"
}

export interface TodoListUpdate {
  title?: string
}

export interface TodoPostponeRequest {
  to_date?: string | null
  to_list_title?: string | null
  excuse: 'busy' | 'other'
}

export interface TodoNotificationRule {
  id: number
  user_id: number
  label: string | null
  trigger_type: 'fixed_time' | 'before_end_of_day' | 'interval'
  fixed_time: string | null       // "HH:MM"
  minutes_before_end: number | null
  interval_minutes: number | null
  window_start: string | null     // "HH:MM"
  window_end: string | null       // "HH:MM"
  notify_only_if_incomplete: boolean
  enabled: boolean
  last_sent_at: string | null
  created_at: string
}

export interface TodoNotificationRuleCreate {
  label?: string | null
  trigger_type: 'fixed_time' | 'before_end_of_day' | 'interval'
  fixed_time?: string | null
  minutes_before_end?: number | null
  interval_minutes?: number | null
  window_start?: string | null
  window_end?: string | null
  notify_only_if_incomplete?: boolean
  enabled?: boolean
}

export interface TodoNotificationRuleUpdate {
  label?: string | null
  trigger_type?: 'fixed_time' | 'before_end_of_day' | 'interval'
  fixed_time?: string | null
  minutes_before_end?: number | null
  interval_minutes?: number | null
  window_start?: string | null
  window_end?: string | null
  notify_only_if_incomplete?: boolean
  enabled?: boolean
}

export interface TodoStats {
  total_created: number
  total_completed: number
  total_postponed: number
  completion_rate_pct: number
  postpone_rate_pct: number
  current_streak_days: number
  days_analyzed: number
}
