// Fitness module types

export interface ExerciseSet {
  id: number
  set_number: number
  reps: number
  weight_kg: number
  completed: boolean
}

export interface ExerciseSetCreate {
  set_number: number
  reps: number
  weight_kg: number
  completed?: boolean
}

export interface ExerciseDefinition {
  name: string
  category: 'push' | 'pull' | 'legs' | 'core' | 'other'
}

export interface Exercise {
  id: number
  name: string
  sets: number
  reps: number
  weight_kg: number
  rest_seconds?: number
  notes?: string
  sets_detail: ExerciseSet[]
}

export interface Workout {
  id: number
  date: string
  name: string
  exercises: Exercise[]
  duration_minutes?: number
  notes?: string
  completed: boolean
  created_at: string
  updated_at?: string
  timer_started_at?: string
  timer_ended_at?: string
  timer_paused_at?: string
  total_paused_seconds: number
  default_rest_seconds?: number
}

export interface WorkoutCreate {
  date: string
  name: string
  exercises: Omit<Exercise, 'id' | 'sets_detail'> & { sets_detail?: ExerciseSetCreate[] }[]
  duration_minutes?: number
  notes?: string
  completed?: boolean
}

export interface WeightEntry {
  id: number
  date: string
  weight_kg: number
  body_fat_percentage?: number
  notes?: string
  created_at: string
}

export interface WeightEntryCreate {
  date: string
  weight_kg: number
  body_fat_percentage?: number
  notes?: string
}

export interface FitnessStats {
  total_workouts: number
  workouts_this_week: number
  workouts_this_month: number
  total_weight_lifted_kg: number
  current_weight_kg: number | null
  weight_change_kg: number | null
}

export interface ExerciseProgress {
  exercise_name: string
  dates: string[]
  max_weights: number[]
}

export interface WorkoutUpdate {
  date?: string
  name?: string
  exercises?: (Omit<Exercise, 'id' | 'sets_detail'> & { sets_detail?: ExerciseSetCreate[] })[]
  duration_minutes?: number
  notes?: string
  completed?: boolean
  default_rest_seconds?: number
}

export interface WeightEntryUpdate {
  date?: string
  weight_kg?: number
  body_fat_percentage?: number
  notes?: string
}

export interface UserBodyProfile {
  id: number
  user_id: number
  height_cm: number | null
  updated_at: string | null
}

export interface BodyMeasurementEntry {
  id: number
  date: string
  bicep_cm?: number
  waist_cm?: number
  thigh_cm?: number
  calf_cm?: number
  chest_cm?: number
  notes?: string
  created_at: string
}

export interface BodyMeasurementEntryCreate {
  date: string
  bicep_cm?: number
  waist_cm?: number
  thigh_cm?: number
  calf_cm?: number
  chest_cm?: number
  notes?: string
}

export interface BodyMeasurementEntryUpdate {
  date?: string
  bicep_cm?: number | null
  waist_cm?: number | null
  thigh_cm?: number | null
  calf_cm?: number | null
  chest_cm?: number | null
  notes?: string
}
