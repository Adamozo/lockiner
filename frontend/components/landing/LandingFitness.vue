<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const module: ModuleData = {
  name: "Fitness",
  headline: "Stop relying on memory!",
  subheadline:
    "You won't remember what you lifted last Tuesday. Fitness logs every set, every kilo, every session — so you always know exactly how far you've come.",
  icon: "i-heroicons-fire",
  color: "warning-orange",
  slides: [
    {
      tab: "Dashboard",
      icon: "i-heroicons-home",
      title: "This week, at a glance",
      description:
        "How many workouts this week? What's your current weight? Did you take your supplements? All of it — answered the moment you open the app.",
      highlights: [
        "Workouts this week",
        "Current body weight",
        "Today's medicines",
        "Total volume lifted",
      ],
    },
    {
      tab: "Workouts",
      icon: "i-heroicons-bolt",
      title: "Log smarter, not harder",
      description:
        "Track every exercise with per-set weight and reps. Build a complete workout history. See what you did last session — and beat it.",
      highlights: [
        "Per-set weight & reps",
        "Full exercise library",
        "Workout history",
        "Draft workouts (auto-saved)",
      ],
    },
    {
      tab: "Weight",
      icon: "i-heroicons-arrow-trending-up",
      title: "The scale tells a story",
      description:
        "Log your body weight regularly. See it plotted over time. Weekly changes, monthly trends — the data shows progress your eyes might miss.",
      highlights: [
        "Daily weigh-in logging",
        "Weight history chart",
        "Change indicators",
      ],
    },
    {
      tab: "Progress",
      icon: "i-heroicons-chart-bar",
      title: "Your long game, visualized",
      description:
        "Charts, personal records and volume trends. Progress isn't always obvious day-to-day — but over months, the numbers don't lie.",
      highlights: [
        "Strength progress charts",
        "Personal records",
        "Volume over time",
      ],
    },
    {
      tab: "Medicines",
      icon: "i-heroicons-beaker",
      title: "Consistency is the supplement",
      description:
        "Track daily supplements and medications. Mark each dose. See your adherence rate. The routine you've been meaning to build — finally built.",
      highlights: [
        "Daily dose tracking",
        "Adherence rate",
        "Custom medication schedules",
      ],
    },
  ],
};
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
