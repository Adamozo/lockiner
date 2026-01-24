<script setup lang="ts">
definePageMeta({
  layout: "fitness",
});

useSeoMeta({
  title: "Fitness Dashboard - LockIner",
  description: "Track your workout progress and fitness goals",
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div>
      <h1 class="text-3xl font-bold text-pure-white">Fitness Dashboard</h1>
      <p class="mt-2 text-pure-white/60">
        Track your workouts and monitor your progress
      </p>
    </div>

    <!-- Work in Progress Banner -->
    <div
      class="bg-warning-orange/10 border border-warning-orange/30 rounded-xl p-6"
    >
      <div class="flex items-center gap-4">
        <div
          class="w-12 h-12 rounded-full bg-warning-orange/20 flex items-center justify-center flex-shrink-0"
        >
          <UIcon
            name="i-heroicons-wrench-screwdriver"
            class="w-6 h-6 text-warning-orange"
          />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-warning-orange">
            Work in Progress
          </h3>
          <p class="text-pure-white/70 mt-1">
            The Fitness module is under development. Planned features:
          </p>
          <ul class="text-pure-white/60 mt-2 space-y-1 text-sm">
            <li class="flex items-center gap-2">
              <UIcon
                name="i-heroicons-check"
                class="w-4 h-4 text-electric-green"
              />
              Ready-made workout plans and AI generation
            </li>
            <li class="flex items-center gap-2">
              <UIcon
                name="i-heroicons-check"
                class="w-4 h-4 text-electric-green"
              />
              Body measurements tracking (circumferences, body fat %)
            </li>
            <li class="flex items-center gap-2">
              <UIcon
                name="i-heroicons-check"
                class="w-4 h-4 text-electric-green"
              />
              Progress charts and workout analytics
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Workouts This Week -->
      <div
        class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden"
      >
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-warning-orange to-electric-green"
        ></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">This Week</p>
            <p class="mt-2 text-3xl font-bold text-warning-orange">--</p>
            <p class="text-xs text-pure-white/40 mt-1">workouts</p>
          </div>
          <div
            class="p-3 bg-gradient-to-br from-warning-orange/20 to-warning-orange/5 rounded-full border border-warning-orange/30"
          >
            <UIcon
              name="i-heroicons-fire"
              class="w-8 h-8 text-warning-orange"
            />
          </div>
        </div>
      </div>

      <!-- Total Workouts -->
      <div
        class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden"
      >
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
        ></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Total Workouts</p>
            <p class="mt-2 text-3xl font-bold text-cyber-blue">--</p>
            <p class="text-xs text-pure-white/40 mt-1">all time</p>
          </div>
          <div
            class="p-3 bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 rounded-full border border-cyber-blue/30"
          >
            <UIcon name="i-heroicons-trophy" class="w-8 h-8 text-cyber-blue" />
          </div>
        </div>
      </div>

      <!-- Current Weight -->
      <div
        class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden"
      >
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-electric-green to-cyber-blue"
        ></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">Current Weight</p>
            <p class="mt-2 text-3xl font-bold text-electric-green">--</p>
          </div>
          <div
            class="p-3 bg-gradient-to-br from-electric-green/20 to-electric-green/5 rounded-full border border-electric-green/30"
          >
            <UIcon
              name="i-heroicons-scale"
              class="w-8 h-8 text-electric-green"
            />
          </div>
        </div>
      </div>

      <!-- Weight Lifted -->
      <div
        class="bg-card-black border border-border-gray rounded-lg p-6 relative overflow-hidden"
      >
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-danger-red to-warning-orange"
        ></div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-pure-white/60">
              Total Weight Lifted
            </p>
            <p class="mt-2 text-3xl font-bold text-pure-white">--</p>
            <p class="text-xs text-pure-white/40 mt-1">all time</p>
          </div>
          <div
            class="p-3 bg-gradient-to-br from-pure-white/10 to-pure-white/5 rounded-full border border-pure-white/20"
          >
            <UIcon name="i-heroicons-bolt" class="w-8 h-8 text-pure-white" />
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State - Recent Workouts -->
    <div
      class="bg-card-black border border-border-gray rounded-xl p-12 text-center"
    >
      <div
        class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4"
      >
        <UIcon name="i-heroicons-fire" class="w-8 h-8 text-pure-white/40" />
      </div>
      <h3 class="text-lg font-medium text-pure-white mb-2">No Workouts</h3>
      <p class="text-pure-white/60 max-w-md mx-auto">
        This section will display your workout history, exercises, and training
        sessions.
      </p>
    </div>

    <!-- Empty State - Weight Tracking -->
    <div
      class="bg-card-black border border-border-gray rounded-xl p-12 text-center"
    >
      <div
        class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4"
      >
        <UIcon name="i-heroicons-scale" class="w-8 h-8 text-pure-white/40" />
      </div>
      <h3 class="text-lg font-medium text-pure-white mb-2">No Weight Data</h3>
      <p class="text-pure-white/60 max-w-md mx-auto">
        This section will display your weight tracking history and progress over
        time.
      </p>
    </div>
  </div>
</template>
