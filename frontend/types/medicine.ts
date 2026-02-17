// Medicine/Supplement module types

export interface MedicineSchedule {
  id: number
  medicine_id: number
  frequency_type: 'daily' | 'every_n_days' | 'weekly' | 'monthly'
  frequency_value: number | null
  time_of_day: string
  days_of_week: string | null
  day_of_month: number | null
  notifications_enabled: boolean
  active: boolean
  created_at: string
  updated_at: string | null
}

export interface MedicineScheduleCreate {
  frequency_type: 'daily' | 'every_n_days' | 'weekly' | 'monthly'
  frequency_value?: number | null
  time_of_day: string
  days_of_week?: string | null
  day_of_month?: number | null
  notifications_enabled?: boolean
}

export interface MedicineScheduleUpdate {
  frequency_type?: string
  frequency_value?: number | null
  time_of_day?: string
  days_of_week?: string | null
  day_of_month?: number | null
  notifications_enabled?: boolean
  active?: boolean
}

export interface Medicine {
  id: number
  name: string
  description: string | null
  dosage: string | null
  unit: string | null
  color: string | null
  icon: string | null
  active: boolean
  schedules: MedicineSchedule[]
  created_at: string
  updated_at: string | null
}

export interface MedicineCreate {
  name: string
  description?: string | null
  dosage?: string | null
  unit?: string | null
  color?: string | null
  icon?: string | null
  schedules?: MedicineScheduleCreate[]
}

export interface MedicineUpdate {
  name?: string
  description?: string | null
  dosage?: string | null
  unit?: string | null
  color?: string | null
  icon?: string | null
  active?: boolean
}

export interface TodayDose {
  log_id: number
  medicine_id: number
  medicine_name: string
  medicine_color: string | null
  medicine_icon: string | null
  dosage: string | null
  unit: string | null
  scheduled_time: string
  taken: boolean
  taken_at: string | null
}

export interface MedicineLog {
  id: number
  medicine_id: number
  schedule_id: number
  scheduled_date: string
  scheduled_time: string
  taken: boolean
  taken_at: string | null
  created_at: string
}

export interface MedicineStats {
  today_total: number
  today_taken: number
  weekly_adherence_pct: number
  current_streak_days: number
}
