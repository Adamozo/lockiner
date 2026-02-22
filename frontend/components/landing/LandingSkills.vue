<script setup lang="ts">
import type { ModuleData } from "./LandingModuleSection.vue";

const { t } = useI18n()

const module = computed<ModuleData>(() => ({
  name: t('landing.skills_name'),
  headline: t('landing.skills_headline'),
  subheadline: t('landing.skills_sub'),
  icon: "i-heroicons-academic-cap",
  color: "cyber-blue",
  comingSoon: true,
  slides: [
    {
      tab: t('landing.skills_tab1'),
      icon: "i-heroicons-map",
      title: t('landing.skills_slide1_title'),
      description: t('landing.skills_slide1_desc'),
      highlights: [t('landing.skills_slide1_h1'), t('landing.skills_slide1_h2'), t('landing.skills_slide1_h3')],
    },
    {
      tab: t('landing.skills_tab2'),
      icon: "i-heroicons-clock",
      title: t('landing.skills_slide2_title'),
      description: t('landing.skills_slide2_desc'),
      highlights: [t('landing.skills_slide2_h1'), t('landing.skills_slide2_h2'), t('landing.skills_slide2_h3')],
    },
  ],
}))
</script>

<template>
  <LandingModuleSection :module="module" />
</template>
