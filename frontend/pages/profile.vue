<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: 'Profile - LockIner',
  description: 'Manage your account settings',
})
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header>
      <h1 class="text-3xl font-bold text-pure-white">Profile</h1>
      <p class="mt-2 text-pure-white/60">Manage your account settings</p>
    </header>

    <!-- User Info Card -->
    <ProfileAccountInfo />

    <!-- Update Profile Section -->
    <ProfileUpdateForm />

    <!-- Change Password Section -->
    <ProfilePasswordForm />
  </div>
</template>
