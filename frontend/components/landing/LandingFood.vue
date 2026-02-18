<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const module: ModuleData = {
  name: "Food",
  headline: "Your fridge is a graveyard?",
  subheadline:
    "Expired yoghurt. Forgotten leftovers. Vegetables you had plans for. Food tracks your entire pantry with live expiry status — so nothing disappears quietly.",
  icon: "i-heroicons-cake",
  color: "electric-green",
  slides: [
    {
      tab: "Inventory",
      icon: "i-heroicons-archive-box",
      title: "Know exactly what you have",
      description:
        "Your full pantry, one view. Items expiring in 3 days are flagged. Items already expired are highlighted. Consume with one tap. Never buy duplicates again.",
      highlights: [
        "Live expiry status",
        "3-day warning alerts",
        "Multi-location support",
        "One-tap consume",
      ],
    },
    {
      tab: "Imports",
      icon: "i-heroicons-arrow-down-tray",
      title: "Just got back from shopping?",
      description:
        "Add everything at once instead of one by one. Bulk import keeps your inventory current without making restocking feel like a chore.",
      highlights: ["Batch product entry", "Fast inventory updates"],
    },
    {
      tab: "Recipes",
      icon: "i-heroicons-book-open",
      title: "Cook what you already have",
      description:
        "Your personal recipe library, tied to your pantry. Plan meals around ingredients you need to use up. Less waste, more intention.",
      highlights: [
        "Personal recipe collection",
        "Ingredient-based meal planning",
      ],
    },
  ],
};
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
