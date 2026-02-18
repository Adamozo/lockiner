<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const module: ModuleData = {
  name: "Finance",
  headline: "Don't know where your money goes?",
  subheadline:
    "Most people are surprised when they finally check. Finance makes it obvious — every transaction logged, every category tracked, every limit respected.",
  icon: "i-heroicons-banknotes",
  color: "electric-green",
  slides: [
    {
      tab: "Dashboard",
      icon: "i-heroicons-home",
      title: "Your money, at a glance",
      description:
        "Open the app and instantly see your total income, expenses and current balance. No digging, no mental math — just the numbers that matter.",
      highlights: [
        "Income & expense totals",
        "Running balance",
        "Recent transactions",
        "Quick add shortcut",
      ],
    },
    {
      tab: "Transactions",
      icon: "i-heroicons-list-bullet",
      title: "Every cent, accounted for",
      description:
        "Log income and expenses in seconds. Filter by date, category or amount. Search when you need to find something specific. Your financial history — clean and complete.",
      highlights: [
        "Add income & expenses",
        "Filter by date & category",
        "Search transactions",
        "Category labels",
      ],
    },
    {
      tab: "Receipts",
      icon: "i-heroicons-document-text",
      title: "Never lose a receipt again",
      description:
        "Store receipts digitally and link them to transactions. Tax season, warranty claims, expense reports — whatever the reason, your receipts are always findable.",
      highlights: [
        "Digital receipt storage",
        "Linked to transactions",
        "Always retrievable",
      ],
    },
    {
      tab: "Analytics",
      icon: "i-heroicons-chart-bar",
      title: "See where it actually goes",
      description:
        "Charts and breakdowns show exactly which categories eat your budget. Spot the patterns you didn't notice. Adjust before it's too late.",
      highlights: [
        "Category spending charts",
        "Monthly trends",
        "Biggest expense breakdown",
      ],
    },
    {
      tab: "Limits",
      icon: "i-heroicons-shield-check",
      title: "Set the rules. Stick to them",
      description:
        "Define spending limits per category. See how close you are in real time. Stop overspending before it happens — not after you check the balance.",
      highlights: [
        "Per-category budgets",
        "Live limit tracking",
        "Overspend warnings",
      ],
    },
  ],
};
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
