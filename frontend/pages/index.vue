<script setup lang="ts">
definePageMeta({
  layout: false,
});

useSeoMeta({
  title: "LockIner - Lock In and Improve",
  description: "Manage your life in one place",
});
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <LandingNav />
    <LandingHero />
    <LandingFeatures />
    <LandingFinance />
    <LandingFitness />
    <LandingFood />
    <LandingJournal />
    <LandingFooter />
  </div>
</template>
