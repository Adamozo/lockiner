<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const { t } = useI18n()

const module = computed<ModuleData>(() => ({
  name: t('landing.journal_name'),
  headline: t('landing.journal_headline'),
  subheadline: t('landing.journal_sub'),
  icon: "i-heroicons-pencil-square",
  color: "cyber-blue",
  slides: [
    {
      tab: t('landing.journal_tab1'),
      icon: "i-heroicons-home",
      title: t('landing.journal_slide1_title'),
      description: t('landing.journal_slide1_desc'),
      highlights: [t('landing.journal_slide1_h1'), t('landing.journal_slide1_h2'), t('landing.journal_slide1_h3'), t('landing.journal_slide1_h4')],
    },
    {
      tab: t('landing.journal_tab2'),
      icon: "i-heroicons-pencil",
      title: t('landing.journal_slide2_title'),
      description: t('landing.journal_slide2_desc'),
      highlights: [t('landing.journal_slide2_h1'), t('landing.journal_slide2_h2'), t('landing.journal_slide2_h3'), t('landing.journal_slide2_h4')],
    },
    {
      tab: t('landing.journal_tab3'),
      icon: "i-heroicons-calendar-days",
      title: t('landing.journal_slide3_title'),
      description: t('landing.journal_slide3_desc'),
      highlights: [t('landing.journal_slide3_h1'), t('landing.journal_slide3_h2')],
    },
    {
      tab: t('landing.journal_tab4'),
      icon: "i-heroicons-chart-bar",
      title: t('landing.journal_slide4_title'),
      description: t('landing.journal_slide4_desc'),
      highlights: [t('landing.journal_slide4_h1'), t('landing.journal_slide4_h2'), t('landing.journal_slide4_h3')],
    },
  ],
}))
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
