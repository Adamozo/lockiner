<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const { t } = useI18n()

const module = computed<ModuleData>(() => ({
  name: t('landing.households_name'),
  headline: t('landing.households_headline'),
  subheadline: t('landing.households_sub'),
  icon: "i-heroicons-home-modern",
  color: "cyber-blue",
  slides: [
    {
      tab: t('landing.households_tab1'),
      icon: "i-heroicons-home",
      title: t('landing.households_slide1_title'),
      description: t('landing.households_slide1_desc'),
      highlights: [t('landing.households_slide1_h1'), t('landing.households_slide1_h2'), t('landing.households_slide1_h3')],
    },
    {
      tab: t('landing.households_tab2'),
      icon: "i-heroicons-user-group",
      title: t('landing.households_slide2_title'),
      description: t('landing.households_slide2_desc'),
      highlights: [t('landing.households_slide2_h1'), t('landing.households_slide2_h2'), t('landing.households_slide2_h3')],
    },
    {
      tab: t('landing.households_tab3'),
      icon: "i-heroicons-chart-pie",
      title: t('landing.households_slide3_title'),
      description: t('landing.households_slide3_desc'),
      highlights: [t('landing.households_slide3_h1'), t('landing.households_slide3_h2'), t('landing.households_slide3_h3')],
    },
  ],
}))
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
