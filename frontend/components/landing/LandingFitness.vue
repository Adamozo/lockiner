<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const { t } = useI18n()

const module = computed<ModuleData>(() => ({
  name: t('landing.fitness_name'),
  headline: t('landing.fitness_headline'),
  subheadline: t('landing.fitness_sub'),
  icon: "i-heroicons-fire",
  color: "warning-orange",
  slides: [
    {
      tab: t('landing.fitness_tab1'),
      icon: "i-heroicons-home",
      title: t('landing.fitness_slide1_title'),
      description: t('landing.fitness_slide1_desc'),
      highlights: [t('landing.fitness_slide1_h1'), t('landing.fitness_slide1_h2'), t('landing.fitness_slide1_h3'), t('landing.fitness_slide1_h4')],
    },
    {
      tab: t('landing.fitness_tab2'),
      icon: "i-heroicons-bolt",
      title: t('landing.fitness_slide2_title'),
      description: t('landing.fitness_slide2_desc'),
      highlights: [t('landing.fitness_slide2_h1'), t('landing.fitness_slide2_h2'), t('landing.fitness_slide2_h3'), t('landing.fitness_slide2_h4')],
    },
    {
      tab: t('landing.fitness_tab3'),
      icon: "i-heroicons-arrow-trending-up",
      title: t('landing.fitness_slide3_title'),
      description: t('landing.fitness_slide3_desc'),
      highlights: [t('landing.fitness_slide3_h1'), t('landing.fitness_slide3_h2'), t('landing.fitness_slide3_h3')],
    },
    {
      tab: t('landing.fitness_tab4'),
      icon: "i-heroicons-chart-bar",
      title: t('landing.fitness_slide4_title'),
      description: t('landing.fitness_slide4_desc'),
      highlights: [t('landing.fitness_slide4_h1'), t('landing.fitness_slide4_h2'), t('landing.fitness_slide4_h3')],
    },
    {
      tab: t('landing.fitness_tab5'),
      icon: "i-heroicons-beaker",
      title: t('landing.fitness_slide5_title'),
      description: t('landing.fitness_slide5_desc'),
      highlights: [t('landing.fitness_slide5_h1'), t('landing.fitness_slide5_h2'), t('landing.fitness_slide5_h3')],
    },
  ],
}))
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
