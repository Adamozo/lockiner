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
}

export interface WeightEntryUpdate {
  date?: string
  weight_kg?: number
  body_fat_percentage?: number
  notes?: string
}
