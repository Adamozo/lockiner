// Mock data for Fitness module
import type { Workout, WeightEntry } from "~/types/fitness";

const today = new Date();
const formatDate = (daysAgo: number) => {
  const date = new Date(today);
  date.setDate(date.getDate() - daysAgo);
  return date.toISOString().split("T")[0];
};

export const mockWorkouts: Workout[] = [
  // {
  //   id: 1,
  //   date: formatDate(0),
  //   name: 'Push Day',
  //   exercises: [
  //     { id: 1, name: 'Bench Press', sets: 4, reps: 8, weight_kg: 80, rest_seconds: 90 },
  //     { id: 2, name: 'Overhead Press', sets: 3, reps: 10, weight_kg: 40, rest_seconds: 60 },
  //     { id: 3, name: 'Incline Dumbbell Press', sets: 3, reps: 12, weight_kg: 30, rest_seconds: 60 },
  //     { id: 4, name: 'Tricep Pushdown', sets: 3, reps: 15, weight_kg: 25, rest_seconds: 45 },
  //   ],
  //   duration_minutes: 65,
  //   notes: 'Felt strong today!',
  //   completed: true,
  // },
  // {
  //   id: 2,
  //   date: formatDate(2),
  //   name: 'Pull Day',
  //   exercises: [
  //     { id: 5, name: 'Deadlift', sets: 4, reps: 6, weight_kg: 120, rest_seconds: 120 },
  //     { id: 6, name: 'Barbell Row', sets: 4, reps: 8, weight_kg: 70, rest_seconds: 90 },
  //     { id: 7, name: 'Lat Pulldown', sets: 3, reps: 12, weight_kg: 60, rest_seconds: 60 },
  //     { id: 8, name: 'Bicep Curl', sets: 3, reps: 12, weight_kg: 15, rest_seconds: 45 },
  //   ],
  //   duration_minutes: 70,
  //   completed: true,
  // },
  // {
  //   id: 3,
  //   date: formatDate(4),
  //   name: 'Leg Day',
  //   exercises: [
  //     { id: 9, name: 'Squat', sets: 4, reps: 8, weight_kg: 100, rest_seconds: 120 },
  //     { id: 10, name: 'Romanian Deadlift', sets: 3, reps: 10, weight_kg: 80, rest_seconds: 90 },
  //     { id: 11, name: 'Leg Press', sets: 3, reps: 12, weight_kg: 150, rest_seconds: 90 },
  //     { id: 12, name: 'Calf Raise', sets: 4, reps: 15, weight_kg: 60, rest_seconds: 45 },
  //   ],
  //   duration_minutes: 75,
  //   notes: 'Legs were shaking!',
  //   completed: true,
  // },
  // {
  //   id: 4,
  //   date: formatDate(6),
  //   name: 'Upper Body',
  //   exercises: [
  //     { id: 13, name: 'Bench Press', sets: 4, reps: 8, weight_kg: 77.5, rest_seconds: 90 },
  //     { id: 14, name: 'Pull-ups', sets: 3, reps: 8, weight_kg: 0, rest_seconds: 90 },
  //     { id: 15, name: 'Dumbbell Shoulder Press', sets: 3, reps: 10, weight_kg: 25, rest_seconds: 60 },
  //   ],
  //   duration_minutes: 55,
  //   completed: true,
  // },
  // {
  //   id: 5,
  //   date: formatDate(8),
  //   name: 'Push Day',
  //   exercises: [
  //     { id: 16, name: 'Bench Press', sets: 4, reps: 8, weight_kg: 75, rest_seconds: 90 },
  //     { id: 17, name: 'Overhead Press', sets: 3, reps: 10, weight_kg: 37.5, rest_seconds: 60 },
  //     { id: 18, name: 'Dips', sets: 3, reps: 10, weight_kg: 0, rest_seconds: 60 },
  //   ],
  //   duration_minutes: 50,
  //   completed: true,
  // },
];

export const mockWeightEntries: WeightEntry[] = [
  // { id: 1, date: formatDate(0), weight_kg: 82.5, body_fat_percentage: 15.2 },
  // { id: 2, date: formatDate(3), weight_kg: 82.8, body_fat_percentage: 15.4 },
  // { id: 3, date: formatDate(7), weight_kg: 83.0, body_fat_percentage: 15.5 },
  // { id: 4, date: formatDate(10), weight_kg: 83.2, body_fat_percentage: 15.8 },
  // { id: 5, date: formatDate(14), weight_kg: 83.5, body_fat_percentage: 16.0 },
  // { id: 6, date: formatDate(21), weight_kg: 84.0, body_fat_percentage: 16.2 },
  // { id: 7, date: formatDate(28), weight_kg: 84.5, body_fat_percentage: 16.5 },
];

export const exerciseLibrary = [
  // // Chest
  // "Bench Press",
  // "Incline Bench Press",
  // "Dumbbell Press",
  // "Incline Dumbbell Press",
  // "Cable Fly",
  // "Push-ups",
  // "Dips",
  // // Back
  // "Deadlift",
  // "Barbell Row",
  // "Dumbbell Row",
  // "Lat Pulldown",
  // "Pull-ups",
  // "Chin-ups",
  // "Cable Row",
  // // Shoulders
  // "Overhead Press",
  // "Dumbbell Shoulder Press",
  // "Lateral Raise",
  // "Front Raise",
  // "Face Pull",
  // // Legs
  // "Squat",
  // "Front Squat",
  // "Leg Press",
  // "Romanian Deadlift",
  // "Leg Curl",
  // "Leg Extension",
  // "Calf Raise",
  // "Lunges",
  // // Arms
  // "Bicep Curl",
  // "Hammer Curl",
  // "Tricep Pushdown",
  // "Skull Crusher",
  // "Close Grip Bench Press",
];
