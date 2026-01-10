<script setup lang="ts">
// Landing page - Public page with CTAs to login/register
import { useAuthStore } from "~/stores/auth";

definePageMeta({
  layout: false,
});

useSeoMeta({
  title: "LockIner - Lock In and Improve",
  description: "Manage your finances, fitness, and skills all in one place",
});

const authStore = useAuthStore();

// Redirect to home if already authenticated
onMounted(async () => {
  if (import.meta.server) return;

  if (!authStore.initialized) {
    authStore.initialize();
  }

  if (authStore.accessToken && !authStore.user) {
    await authStore.fetchCurrentUser();
  }

  if (authStore.isAuthenticated) {
    await navigateTo("/home");
  }
});
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <LandingNav />
    <LandingHero />
    <LandingFeatures />
    <LandingFooter />
  </div>
</template>
