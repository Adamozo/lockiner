<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const module: ModuleData = {
  name: "Households",
  headline: "Shared costs. Zero awkwardness.",
  subheadline:
    "Splitting bills between flatmates or managing family finances shouldn't need a group chat thread. Households puts everyone on the same page, automatically.",
  icon: "i-heroicons-home-modern",
  color: "cyber-blue",
  slides: [
    {
      tab: "Overview",
      icon: "i-heroicons-home",
      title: "One app, multiple homes.",
      description:
        "Switch between your personal context and shared household contexts instantly. Manage your own finances and shared ones — without mixing them up.",
      highlights: [
        "Personal & shared contexts",
        "Multiple households",
        "One-click switching",
      ],
    },
    {
      tab: "Members",
      icon: "i-heroicons-user-group",
      title: "Invite. Manage. Collaborate.",
      description:
        "Share access to a household with a simple invitation link. Control who's in, manage members, and keep the shared space organised.",
      highlights: [
        "Invite by link",
        "Member management",
        "Shared access control",
      ],
    },
    {
      tab: "Analytics",
      icon: "i-heroicons-chart-pie",
      title: "Who spent what? Now you know.",
      description:
        "Household-level breakdowns show shared spending, contributions per member and category totals. No guessing. No awkward conversations.",
      highlights: [
        "Shared spending overview",
        "Per-member breakdown",
        "Category totals",
      ],
    },
  ],
};
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
