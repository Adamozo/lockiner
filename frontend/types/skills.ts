// Skills module types

export type JourneyCategory = 'programming' | 'language' | 'cooking' | 'music' | 'other'
export type JourneyStatus = 'active' | 'paused' | 'completed'

export interface Milestone {
  id: number
  title: string
  completed: boolean
  completed_at?: string
}

export interface LearningJourney {
  id: number
  name: string
  description?: string
  category: JourneyCategory
  status: JourneyStatus
  started_at: string
  target_hours?: number
  logged_hours: number
  milestones: Milestone[]
  icon?: string
  color?: string
}

export interface JourneyCreate {
  name: string
  description?: string
  category: JourneyCategory
  target_hours?: number
  milestones?: string[]
}

export interface LearningLogEntry {
  id: number
  journey_id: number
  journey_name: string
  date: string
  duration_minutes: number
  activity: string
  notes?: string
  resources?: string[]
}

export interface LogEntryCreate {
  journey_id: number
  date: string
  duration_minutes: number
  activity: string
  notes?: string
  resources?: string[]
}

export interface SkillsStats {
  total_journeys: number
  active_journeys: number
  completed_journeys: number
  total_hours_logged: number
  hours_this_week: number
  completed_milestones: number
}
