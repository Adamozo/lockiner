// Journal module types

export const JOURNAL_CATEGORIES = ['accomplished', 'grateful', 'proud', 'annoyed', 'learned'] as const
export type JournalCategory = typeof JOURNAL_CATEGORIES[number]

export const CATEGORY_META: Record<JournalCategory, { label: string; icon: string; color: string }> = {
  accomplished: { label: 'Accomplished', icon: 'i-heroicons-trophy', color: 'text-electric-green' },
  grateful: { label: 'Grateful For', icon: 'i-heroicons-heart', color: 'text-cyber-blue' },
  proud: { label: 'Proud Of', icon: 'i-heroicons-star', color: 'text-warning-orange' },
  annoyed: { label: 'Annoyed By', icon: 'i-heroicons-bolt', color: 'text-danger-red' },
  learned: { label: 'Learned', icon: 'i-heroicons-light-bulb', color: 'text-purple-400' },
}

export interface JournalItem {
  id: number
  category: JournalCategory
  position: number
  content: string
}

export interface JournalItemCreate {
  category: JournalCategory
  position: number
  content: string
}

export interface JournalEntry {
  id: number
  date: string
  mood_score: number | null
  notes: string | null
  items: JournalItem[]
  created_at: string
  updated_at: string | null
}

export interface JournalEntryCreate {
  date: string
  mood_score?: number | null
  notes?: string | null
  items: JournalItemCreate[]
}

export interface JournalEntryUpdate {
  mood_score?: number | null
  notes?: string | null
  items?: JournalItemCreate[]
}

export interface JournalStats {
  total_entries: number
  entries_this_week: number
  entries_this_month: number
  current_streak: number
  longest_streak: number
  avg_mood: number | null
}

export interface CategoryReportData {
  count: number
  items: string[]
}

export interface ReportData {
  categories: Record<JournalCategory, CategoryReportData>
  avg_mood: number | null
  entry_count: number
  current_streak: number
  longest_streak: number
}

export interface JournalReport {
  id: number
  report_type: 'monthly' | 'yearly'
  period: string
  data: ReportData
  entry_count: number
  created_at: string
  updated_at: string | null
}

export interface ReportGenerateRequest {
  report_type: 'monthly' | 'yearly'
  period: string
}
