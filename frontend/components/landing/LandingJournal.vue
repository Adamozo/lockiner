<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const module: ModuleData = {
  name: "Journal",
  headline: "The year ends. You can't remember it",
  subheadline:
    "You did things. Overcame things. Achieved things. But when someone asks — or when you ask yourself — it's all a blur. Journal is your personal record: daily entries, mood, what's been grinding you down and what's genuinely been making you proud. So when December rolls around, you actually know what happened.",
  icon: "i-heroicons-pencil-square",
  color: "cyber-blue",
  slides: [
    {
      tab: "Dashboard",
      icon: "i-heroicons-home",
      title: "Your year, already taking shape",
      description:
        "Streak, entry count, average mood, monthly consistency. At a glance — the proof that you showed up. Or the reminder that you should.",
      highlights: [
        "Current writing streak",
        "Average mood score",
        "Total & monthly entries",
        "Longest streak ever",
      ],
    },
    {
      tab: "Today",
      icon: "i-heroicons-pencil",
      title: "What happened today? Write it down",
      description:
        "Free-form entry for whatever's on your mind. Rate your mood. Add what annoyed you today and what made you genuinely proud. Two minutes now — priceless context later.",
      highlights: [
        "Free-form daily entry",
        "Mood rating (1–10)",
        "Annoyed by today",
        "Proud of today",
      ],
    },
    {
      tab: "History",
      icon: "i-heroicons-calendar-days",
      title: "Proof that a lot happened",
      description:
        "Scroll back through your entries. Read what you wrote in March. See the version of you that was struggling, or thriving, or somewhere in between. It's all there.",
      highlights: [
        "Full chronological history",
        "Easy date navigation",
      ],
    },
    {
      tab: "Reports",
      icon: "i-heroicons-chart-bar",
      title: "Patterns you didn't know were there",
      description:
        "Which months were rough? What's been consistently annoying you? Where does your mood dip — and what came right after? Reports turn your entries into answers.",
      highlights: [
        "Mood trends over time",
        "Writing consistency",
        "Monthly breakdowns",
      ],
    },
  ],
};
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
