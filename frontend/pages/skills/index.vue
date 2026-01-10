<script setup lang="ts">
definePageMeta({
  layout: 'skills',
})

useSeoMeta({
  title: 'Skills Dashboard - LockIner',
  description: 'Track your learning journeys and skill development',
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div>
      <h1 class="text-3xl font-bold text-pure-white">Skills Dashboard</h1>
      <p class="mt-2 text-pure-white/60">
        Track your learning progress and master new skills
      </p>
    </div>

    <!-- Work in Progress Banner -->
    <div class="bg-cyber-blue/10 border border-cyber-blue/30 rounded-xl p-6">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-cyber-blue/20 flex items-center justify-center flex-shrink-0">
          <UIcon name="i-heroicons-wrench-screwdriver" class="w-6 h-6 text-cyber-blue" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-cyber-blue">Work in Progress</h3>
          <p class="text-pure-white/70 mt-1">
            The Skills module is under development. Planned features:
          </p>
          <ul class="text-pure-white/60 mt-2 space-y-1 text-sm">
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green" />
              Integration with external platforms (Udemy, Coursera)
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green" />
              Automatic course progress tracking
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green" />
              AI-powered learning path suggestions
            </li>
            <li class="flex items-center gap-2">
              <UIcon name="i-heroicons-check" class="w-4 h-4 text-electric-green" />
              Regular learning reminders
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Active Journeys -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Active Journeys</p>
            <p class="mt-2 text-3xl font-bold text-cyber-blue">--</p>
          </div>
          <div class="p-3 bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 rounded-full border border-cyber-blue/30">
            <UIcon name="i-heroicons-academic-cap" class="w-8 h-8 text-cyber-blue" />
          </div>
        </div>
      </div>

      <!-- Hours This Week -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-electric-green to-cyber-blue"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">This Week</p>
            <p class="mt-2 text-3xl font-bold text-electric-green">--</p>
          </div>
          <div class="p-3 bg-gradient-to-br from-electric-green/20 to-electric-green/5 rounded-full border border-electric-green/30">
            <UIcon name="i-heroicons-clock" class="w-8 h-8 text-electric-green" />
          </div>
        </div>
      </div>

      <!-- Total Hours -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-warning-orange to-electric-green"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Total Hours</p>
            <p class="mt-2 text-3xl font-bold text-warning-orange">--</p>
          </div>
          <div class="p-3 bg-gradient-to-br from-warning-orange/20 to-warning-orange/5 rounded-full border border-warning-orange/30">
            <UIcon name="i-heroicons-fire" class="w-8 h-8 text-warning-orange" />
          </div>
        </div>
      </div>

      <!-- Milestones -->
      <div class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-danger-red to-warning-orange"></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Milestones</p>
            <p class="mt-2 text-3xl font-bold text-pure-white">--</p>
            <p class="text-xs text-pure-white/40 mt-1">completed</p>
          </div>
          <div class="p-3 bg-gradient-to-br from-pure-white/10 to-pure-white/5 rounded-full border border-pure-white/20">
            <UIcon name="i-heroicons-trophy" class="w-8 h-8 text-pure-white" />
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State - Active Journeys -->
    <div class="bg-card-black border border-border-gray rounded-xl p-12 text-center">
      <div class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-academic-cap" class="w-8 h-8 text-pure-white/40" />
      </div>
      <h3 class="text-lg font-medium text-pure-white mb-2">No Learning Journeys</h3>
      <p class="text-pure-white/60 max-w-md mx-auto">
        This section will display your active learning journeys, courses, and skill development progress.
      </p>
    </div>

    <!-- Empty State - Recent Activity -->
    <div class="bg-card-black border border-border-gray rounded-xl p-12 text-center">
      <div class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-clipboard-document-list" class="w-8 h-8 text-pure-white/40" />
      </div>
      <h3 class="text-lg font-medium text-pure-white mb-2">No Activity Logged</h3>
      <p class="text-pure-white/60 max-w-md mx-auto">
        This section will display your recent learning activities and time spent on each skill.
      </p>
    </div>
  </div>
</template>
