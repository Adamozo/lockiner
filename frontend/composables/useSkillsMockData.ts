// Mock data for Skills module
import type { LearningJourney, LearningLogEntry } from '~/types/skills'

const today = new Date()
const formatDate = (daysAgo: number) => {
  const date = new Date(today)
  date.setDate(date.getDate() - daysAgo)
  return date.toISOString().split('T')[0]
}

export const mockJourneys: LearningJourney[] = [
  {
    id: 1,
    name: 'Python Programming',
    description: 'Learn Python from basics to advanced concepts',
    category: 'programming',
    status: 'active',
    started_at: formatDate(45),
    target_hours: 100,
    logged_hours: 32,
    icon: 'i-heroicons-code-bracket',
    color: 'cyber-blue',
    milestones: [
      { id: 1, title: 'Complete Python basics', completed: true, completed_at: formatDate(30) },
      { id: 2, title: 'Learn data structures', completed: true, completed_at: formatDate(20) },
      { id: 3, title: 'Build first project', completed: false },
      { id: 4, title: 'Learn web frameworks', completed: false },
      { id: 5, title: 'Build portfolio project', completed: false },
    ],
  },
  {
    id: 2,
    name: 'SQL Interview Prep',
    description: 'Prepare for SQL technical interviews',
    category: 'programming',
    status: 'active',
    started_at: formatDate(20),
    target_hours: 30,
    logged_hours: 12,
    icon: 'i-heroicons-circle-stack',
    color: 'electric-green',
    milestones: [
      { id: 6, title: 'Review SQL basics', completed: true, completed_at: formatDate(15) },
      { id: 7, title: 'Practice JOINs and subqueries', completed: true, completed_at: formatDate(10) },
      { id: 8, title: 'Window functions', completed: false },
      { id: 9, title: 'Optimization techniques', completed: false },
      { id: 10, title: 'Mock interviews', completed: false },
    ],
  },
  {
    id: 3,
    name: 'Italian Cooking',
    description: 'Master authentic Italian recipes',
    category: 'cooking',
    status: 'active',
    started_at: formatDate(60),
    target_hours: 50,
    logged_hours: 18,
    icon: 'i-heroicons-fire',
    color: 'warning-orange',
    milestones: [
      { id: 11, title: 'Master pasta basics', completed: true, completed_at: formatDate(40) },
      { id: 12, title: 'Learn sauce techniques', completed: true, completed_at: formatDate(25) },
      { id: 13, title: 'Pizza from scratch', completed: false },
      { id: 14, title: 'Risotto perfection', completed: false },
    ],
  },
  {
    id: 4,
    name: 'TypeScript Advanced',
    description: 'Deep dive into TypeScript type system',
    category: 'programming',
    status: 'paused',
    started_at: formatDate(90),
    target_hours: 40,
    logged_hours: 8,
    icon: 'i-heroicons-code-bracket-square',
    color: 'cyber-blue',
    milestones: [
      { id: 15, title: 'Generics mastery', completed: true, completed_at: formatDate(80) },
      { id: 16, title: 'Utility types', completed: false },
      { id: 17, title: 'Type challenges', completed: false },
    ],
  },
]

export const mockLogEntries: LearningLogEntry[] = [
  {
    id: 1,
    journey_id: 1,
    journey_name: 'Python Programming',
    date: formatDate(0),
    duration_minutes: 90,
    activity: 'Worked on Flask REST API tutorial',
    notes: 'Built a simple CRUD API, learned about decorators',
    resources: ['Flask documentation', 'Real Python tutorial'],
  },
  {
    id: 2,
    journey_id: 2,
    journey_name: 'SQL Interview Prep',
    date: formatDate(1),
    duration_minutes: 60,
    activity: 'Practiced window functions on LeetCode',
    notes: 'ROW_NUMBER, RANK, DENSE_RANK are clear now',
  },
  {
    id: 3,
    journey_id: 1,
    journey_name: 'Python Programming',
    date: formatDate(2),
    duration_minutes: 120,
    activity: 'List comprehensions and generators',
    notes: 'Memory efficiency with generators is impressive',
  },
  {
    id: 4,
    journey_id: 3,
    journey_name: 'Italian Cooking',
    date: formatDate(3),
    duration_minutes: 150,
    activity: 'Made carbonara from scratch',
    notes: 'Finally got the egg technique right!',
  },
  {
    id: 5,
    journey_id: 2,
    journey_name: 'SQL Interview Prep',
    date: formatDate(4),
    duration_minutes: 45,
    activity: 'Complex JOIN problems',
  },
  {
    id: 6,
    journey_id: 1,
    journey_name: 'Python Programming',
    date: formatDate(5),
    duration_minutes: 60,
    activity: 'Object-oriented programming concepts',
  },
  {
    id: 7,
    journey_id: 3,
    journey_name: 'Italian Cooking',
    date: formatDate(7),
    duration_minutes: 180,
    activity: 'Attempted homemade pizza',
    notes: 'Dough needs more practice',
  },
]

export const categoryOptions = [
  { value: 'programming', label: 'Programming', icon: 'i-heroicons-code-bracket' },
  { value: 'language', label: 'Language', icon: 'i-heroicons-language' },
  { value: 'cooking', label: 'Cooking', icon: 'i-heroicons-fire' },
  { value: 'music', label: 'Music', icon: 'i-heroicons-musical-note' },
  { value: 'other', label: 'Other', icon: 'i-heroicons-academic-cap' },
]
