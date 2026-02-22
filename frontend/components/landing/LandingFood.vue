<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const { t } = useI18n()

const module = computed<ModuleData>(() => ({
  name: t('landing.food_name'),
  headline: t('landing.food_headline'),
  subheadline: t('landing.food_sub'),
  icon: "i-heroicons-cake",
  color: "electric-green",
  slides: [
    {
      tab: t('landing.food_tab1'),
      icon: "i-heroicons-archive-box",
      title: t('landing.food_slide1_title'),
      description: t('landing.food_slide1_desc'),
      highlights: [t('landing.food_slide1_h1'), t('landing.food_slide1_h2'), t('landing.food_slide1_h3'), t('landing.food_slide1_h4')],
    },
    {
      tab: t('landing.food_tab2'),
      icon: "i-heroicons-arrow-down-tray",
      title: t('landing.food_slide2_title'),
      description: t('landing.food_slide2_desc'),
      highlights: [t('landing.food_slide2_h1'), t('landing.food_slide2_h2')],
    },
    {
      tab: t('landing.food_tab3'),
      icon: "i-heroicons-book-open",
      title: t('landing.food_slide3_title'),
      description: t('landing.food_slide3_desc'),
      highlights: [t('landing.food_slide3_h1'), t('landing.food_slide3_h2')],
    },
  ],
}))
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
