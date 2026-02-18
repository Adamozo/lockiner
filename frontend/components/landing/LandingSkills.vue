<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const module: ModuleData = {
  name: "Skills",
  headline: "You start. You drift. You forget.",
  subheadline:
    "Learning something new is easy. Finishing it is not. Skills keeps your learning paths structured, your sessions logged and your consistency visible — so you actually make it.",
  icon: "i-heroicons-academic-cap",
  color: "cyber-blue",
  comingSoon: true,
  slides: [
    {
      tab: "Journeys",
      icon: "i-heroicons-map",
      title: "Learning with a destination.",
      description:
        "Create a learning journey for any skill. Define milestones, track progress and see how far you are from where you want to be.",
      highlights: [
        "Custom learning paths",
        "Milestone tracking",
        "Progress visibility",
      ],
    },
    {
      tab: "Log",
      icon: "i-heroicons-clock",
      title: "Sessions logged. Hours counted.",
      description:
        "Log every study or practice session as it happens. Build a history of real effort — not intentions. Your consistency becomes the proof.",
      highlights: [
        "Session logging",
        "Total hours tracking",
        "Consistency view",
      ],
    },
  ],
};
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
