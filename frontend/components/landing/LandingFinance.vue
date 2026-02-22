<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const { t } = useI18n()

const module = computed<ModuleData>(() => ({
  name: t('landing.finance_name'),
  headline: t('landing.finance_headline'),
  subheadline: t('landing.finance_sub'),
  icon: "i-heroicons-banknotes",
  color: "electric-green",
  slides: [
    {
      tab: t('landing.finance_tab1'),
      icon: "i-heroicons-home",
      title: t('landing.finance_slide1_title'),
      description: t('landing.finance_slide1_desc'),
      highlights: [t('landing.finance_slide1_h1'), t('landing.finance_slide1_h2'), t('landing.finance_slide1_h3'), t('landing.finance_slide1_h4')],
    },
    {
      tab: t('landing.finance_tab2'),
      icon: "i-heroicons-list-bullet",
      title: t('landing.finance_slide2_title'),
      description: t('landing.finance_slide2_desc'),
      highlights: [t('landing.finance_slide2_h1'), t('landing.finance_slide2_h2'), t('landing.finance_slide2_h3'), t('landing.finance_slide2_h4')],
    },
    {
      tab: t('landing.finance_tab3'),
      icon: "i-heroicons-document-text",
      title: t('landing.finance_slide3_title'),
      description: t('landing.finance_slide3_desc'),
      highlights: [t('landing.finance_slide3_h1'), t('landing.finance_slide3_h2'), t('landing.finance_slide3_h3')],
    },
    {
      tab: t('landing.finance_tab4'),
      icon: "i-heroicons-chart-bar",
      title: t('landing.finance_slide4_title'),
      description: t('landing.finance_slide4_desc'),
      highlights: [t('landing.finance_slide4_h1'), t('landing.finance_slide4_h2'), t('landing.finance_slide4_h3')],
    },
    {
      tab: t('landing.finance_tab5'),
      icon: "i-heroicons-shield-check",
      title: t('landing.finance_slide5_title'),
      description: t('landing.finance_slide5_desc'),
      highlights: [t('landing.finance_slide5_h1'), t('landing.finance_slide5_h2'), t('landing.finance_slide5_h3')],
    },
  ],
}))
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
